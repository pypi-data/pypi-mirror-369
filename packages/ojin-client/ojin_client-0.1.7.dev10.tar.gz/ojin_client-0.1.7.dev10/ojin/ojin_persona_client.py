"""WebSocket client for OJIN Persona service with optimized cancellation handling."""

import asyncio
import contextlib
import json
import logging
import pathlib
import ssl
import time
import uuid
from typing import Dict, Optional, Type, TypeVar

import websockets
from pydantic import BaseModel
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import (
    ConnectionClosedError,
    ConnectionClosedOK,
    WebSocketException,
)

from ojin.entities.interaction_messages import (
    CancelInteractionMessage,
    ErrorResponse,
    ErrorResponseMessage,
    InteractionInput,
    InteractionInputMessage,
    InteractionResponseMessage,
)
from ojin.ojin_persona_messages import (
    IOjinPersonaClient,
    OjinPersonaCancelInteractionMessage,
    OjinPersonaInteractionInputMessage,
    OjinPersonaInteractionReadyMessage,
    OjinPersonaInteractionResponseMessage,
    OjinPersonaMessage,
    OjinPersonaSessionReadyMessage,
    StartInteractionMessage,
    StartInteractionResponseMessage,
)

T = TypeVar("T", bound=OjinPersonaMessage)

logger = logging.getLogger(__name__)


ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
localhost_pem = pathlib.Path(__file__).with_name("cacert.pem")
ssl_context.load_verify_locations(localhost_pem)


class OjinPersonaClient(IOjinPersonaClient):
    """WebSocket client for communicating with the OJIN Persona service.

    This client handles the WebSocket connection, authentication, and message
    serialization/deserialization for the OJIN Persona service.
    """

    def __init__(
        self,
        ws_url: str,
        api_key: str,
        config_id: str,
        reconnect_attempts: int = 3,
        reconnect_delay: float = 1.0,
    ):
        """Initialize the OJIN Persona WebSocket client.

        Args:
            ws_url: WebSocket URL of the OJIN Persona service
            api_key: API key for authentication
            config_id: Configuration ID for the persona
            reconnect_attempts: Number of reconnection attempts on failure
            reconnect_delay: Delay between reconnection attempts in seconds

        """
        super().__init__()
        self.ws_url = ws_url
        self.api_key = api_key
        self.config_id = config_id
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay

        self._ws: Optional[ClientConnection] = None
        self._message_queue: asyncio.Queue[BaseModel] = asyncio.Queue()
        self._running = False
        self._receive_task: Optional[asyncio.Task] = None
        self._inference_server_ready: bool = False
        self._cancelled: bool = False
        self._active_interaction_id: str | None = None
        self._split_audio_task: Optional[asyncio.Task] = None
        self._audio_queue: asyncio.Queue[OjinPersonaInteractionInputMessage] = asyncio.Queue()
        
        # Add cancellation event for immediate stopping
        self._cancel_event = asyncio.Event()

    async def connect(self) -> None:
        """Establish WebSocket connection and authenticate with the service."""
        if self._running:
            logger.warning("Client is already connected")
            return

        attempt = 0
        last_error = None

        try:
            while attempt < self.reconnect_attempts:
                headers = {"Authorization": f"{self.api_key}"}

                # Add query parameters for API key and config ID
                url = f"{self.ws_url}?config_id={self.config_id}"
                self._ws = await websockets.connect(
                    url, additional_headers=headers, ping_interval=30, ping_timeout=10
                )
                self._running = True
                self._receive_task = asyncio.create_task(self._receive_messages())
                self._split_audio_task = asyncio.create_task(self._split_audio())
                logger.info("Successfully connected to OJIN Persona service")
                return
        except WebSocketException as e:
            last_error = e
            attempt += 1
            if attempt < self.reconnect_attempts:
                logger.warning(
                    "Connection attempt %d/%d failed. Retrying in %d seconds...",
                    attempt, self.reconnect_attempts, self.reconnect_delay
                )
                await asyncio.sleep(self.reconnect_delay)

        logger.error("Failed to connect after %d attempts", self.reconnect_attempts)
        raise ConnectionError(
            f"Failed to connect to OJIN Persona service: {last_error}"
        )

    async def close(self) -> None:
        """Close the WebSocket connection."""
        if not self._running:
            pass

        self._running = False
        self._active_interaction_id = None
        self._cancel_event.set()  # Signal cancellation to all tasks

        if self._ws:
            try:
                await self._ws.close()
            except Exception as e:
                logger.error("Error closing WebSocket connection: %s", e)
            self._ws = None
        
        if self._split_audio_task:
            self._split_audio_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._split_audio_task
            self._split_audio_task = None

        if self._receive_task:
            self._receive_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._receive_task
            self._receive_task = None   

        logger.info("Disconnected from OJIN Persona service")

    async def _receive_messages(self) -> None:
        """Continuously receive and process incoming messages."""
        if not self._ws:
            raise RuntimeError("WebSocket connection not established")

        try:
            async for message in self._ws:
                try:
                    await self._handle_message(message)
                except Exception as e:
                    logger.exception("Error processing message: %s", e)
                    await self.close()
                    break
        except (ConnectionClosedOK, ConnectionClosedError) as e:
            if self._running:  # Only log if we didn't initiate the close
                logger.error("WebSocket connection closed: %s", e)
        except Exception as e:
            logger.exception("Error in WebSocket receive loop: %s", e)
        finally:
            self._running = False

    async def _handle_message(self, message: str | bytes) -> None:
        """Handle an incoming WebSocket message.

        Args:
            message: Raw JSON message from WebSocket

        """
        try:
            if isinstance(message, bytes):
                try:
                    interaction_server_response = InteractionResponseMessage.from_bytes(
                        message
                    )
                    interaction_response = OjinPersonaInteractionResponseMessage(
                        interaction_id=interaction_server_response.payload.interaction_id,
                        video_frame_bytes=interaction_server_response.payload.payload,
                        is_final_response=interaction_server_response.payload.is_final_response,
                    )
                    logger.debug("Received InteractionResponse for id %s", interaction_response.interaction_id)
                    
                    # TODO: Possibly want to delete
                    if interaction_response.interaction_id != self._active_interaction_id:
                        logger.warning("Message From other interaction")
                        return
                    await self._message_queue.put(interaction_response)
                    return
                except Exception as e:
                    logger.error(e)
                    raise

            # NOTE: str type
            # TODO: clean when the proxy add structured logs for this error
            if message == "No backend servers available. Please try again later.":
                await self._message_queue.put(
                    ErrorResponseMessage(
                        payload=ErrorResponse(
                            interaction_id=None,
                            code="NO_BACKEND_SERVER_AVAILABLE",
                            message=message,
                            timestamp=int(time.monotonic() * 1000),
                        )
                    )
                )
                raise Exception(message)

            data = json.loads(message)
            msg_type = data.get("type")

            # Map message types to their corresponding classes
            message_types: Dict[str, Type[BaseModel]] = {
                "interaction_ready": OjinPersonaInteractionReadyMessage,
                "interactionResponse": OjinPersonaInteractionResponseMessage,
                "sessionReady": OjinPersonaSessionReadyMessage,
                "errorResponse": ErrorResponseMessage,
            }

            if msg_type in message_types:
                msg_class = message_types[msg_type]
                # Convert the message data to the appropriate message class
                #logger.debug("Received message type %s", msg_type)
                if msg_type == "interactionResponse":
                    interaction_response = OjinPersonaInteractionResponseMessage(
                        interaction_id=data["interaction_id"],
                        video_frame_bytes=data["payload"],
                        is_final_response=data["is_final"],
                    )
                    await self._message_queue.put(interaction_response)
                    return

                msg = msg_class(**data)
                if isinstance(msg, OjinPersonaSessionReadyMessage):
                    self._inference_server_ready = True

                await self._message_queue.put(msg)

                if isinstance(msg, ErrorResponseMessage):
                    raise RuntimeError(f"Error in Inference Server received: {msg}")

                logger.info("Received message: %s", msg)
            else:
                logger.warning("Unknown message type: %s", msg_type)

        except Exception as e:
            logger.exception("Error handling message: %s", e)
            raise Exception(e) from e

    async def send_message(self, message: BaseModel) -> None:
        """Send a message to the OJIN Persona service.

        Args:
            message: The message to send

        Raises:
            ConnectionError: If not connected to the WebSocket

        """
        if not self._ws or not self._running:
            raise ConnectionError("Not connected to OJIN Persona service")

        if self._inference_server_ready is not True:
            raise ConnectionError("Infernece Server is not ready to receive messsages")

        if isinstance(message, OjinPersonaCancelInteractionMessage):
            logger.info("Interrupt - Processing cancellation immediately")
            
            # Set cancellation flag and event immediately
            self._cancelled = True
            self._cancel_event.set()
            
            # Send cancellation message with high priority
            cancel_input = CancelInteractionMessage(
                    payload=message.to_proxy_message()
            )

            # Send immediately without waiting
            try:
                await self._ws.send(cancel_input.model_dump_json())
                logger.info(f"Cancellation message sent immediately for {message.interaction_id}")
            except Exception as e:
                logger.error(f"Failed to send cancellation message: {e}")

            # Clear queues quickly without blocking
            self._clear_queues_non_blocking()

            # Reset cancellation state
            self._cancelled = False
            self._cancel_event.clear()

            return

        if isinstance(message, StartInteractionMessage):
            interaction_id = str(uuid.uuid4())
            self._active_interaction_id = interaction_id
            logger.info("Generate UUID %s", interaction_id)
            interaction_response = StartInteractionResponseMessage(
                interaction_id=interaction_id
            )
            # Clear queues non-blocking
            self._clear_queues_non_blocking()
            self._message_queue.put_nowait(interaction_response)
            return

        if isinstance(message, OjinPersonaInteractionInputMessage):
            logger.info("InteractionMessage")            
            logger.info(f"Message sent {message.interaction_id}")
            if message.interaction_id != self._active_interaction_id:
                return

            if not message.audio_int16_bytes:
                raise ValueError("Audio cannot be empty")
            
            await self._audio_queue.put(message)
            return

        logger.error("The message %s is Unknown", message)
        # TODO: should we close the connection here?
        await self.close()
        error = ErrorResponseMessage(
                payload=ErrorResponse(
                    interaction_id=message.interaction_id,
                    code="UNKNOWN",
                    message="The message is Unknown",
                    timestamp=int(time.monotonic() * 1000),
                )
        )
        raise Exception(error)

    def _clear_queues_non_blocking(self) -> None:
        """Clear all queues without blocking."""
        # Clear message queue
        while True:
            try:
                self._message_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Clear audio queue
        while True:
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

    async def _split_audio(self) -> None:
        """Split audio into chunks and send them, with cancellation support."""
        while self._running:
            message_audio: OjinPersonaInteractionInputMessage | None = None
            
            try:
                # Use wait_for with cancellation event to make this interruptible
                wait_tasks = [
                    asyncio.create_task(self._audio_queue.get()),
                    asyncio.create_task(self._cancel_event.wait())
                ]
                
                done, pending = await asyncio.wait(
                    wait_tasks, 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=0.1  # Short timeout to check cancellation frequently
                )
                
                # Cancel pending tasks
                for task in pending:
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task
                
                # Check if cancellation was triggered
                if self._cancelled or self._cancel_event.is_set():
                    logger.info("Audio splitting cancelled")
                    continue
                
                # Check if we got a message
                if done:
                    completed_task = done.pop()
                    if completed_task == wait_tasks[0]:  # Audio queue task completed
                        message_audio = completed_task.result()
                    else:  # Cancellation event was set
                        continue
                else:
                    # Timeout occurred, continue loop
                    continue
                    
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.01)
                continue
            except Exception as e:
                logger.error(f"Error getting audio message: {e}")
                continue

            if not message_audio:
                continue

            # Process audio chunks with cancellation checks
            max_chunk_size = 3200 * 2
            audio_chunks = [
                message_audio.audio_int16_bytes[i : i + max_chunk_size]
                for i in range(0, len(message_audio.audio_int16_bytes), max_chunk_size)
            ]
            logger.info(
                "Split audio into %d chunks of max %d bytes",
                len(audio_chunks), max_chunk_size
            )

            for i, chunk in enumerate(audio_chunks):
                # Check for cancellation before each chunk
                if self._cancelled or self._cancel_event.is_set():
                    logger.info("Audio chunk sending cancelled")
                    break
                    
                is_last = i == len(audio_chunks) - 1 and message_audio.is_last_input

                interaction_input = InteractionInput(
                    interaction_id=message_audio.interaction_id,
                    is_final_input=is_last,
                    payload_type="audio",
                    payload=chunk,
                    timestamp=int(time.monotonic() * 1000),
                    params=message_audio.params if i == 0 else None,
                )
                proxy_message = InteractionInputMessage(payload=interaction_input)

                try:
                    await self._ws.send(proxy_message.to_bytes())
                except Exception as e:
                    logger.error(f"Failed to send audio chunk: {e}")
                    break

    async def receive_message(self) -> BaseModel | None:
        """Receive the next message from the OJIN Persona service.

        Returns:
            The next available message

        Raises:
            asyncio.QueueEmpty: If no messages are available

        """
        if self._cancelled:
            return None
        return await self._message_queue.get()

    def is_connected(self) -> bool:
        """Check if the client is connected to the WebSocket."""
        return (self._running and self._ws is not None and 
            self._ws.state == websockets.State.OPEN)
