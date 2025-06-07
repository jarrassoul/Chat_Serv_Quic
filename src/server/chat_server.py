import asyncio
import logging
from typing import Dict, Optional

from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived, ConnectionTerminated

from src.protocol.message import MsgType, Message, pack, unpack  # Updated import
from src.protocol.auth import AuthManager
from src.utils.config_loader import load_config
from .server_state import ServerStateManager

logging.basicConfig(level=logging.INFO)

# ... rest of the file remains the same ...

class ChatProtocol(QuicConnectionProtocol):
    def __init__(self, *args, server_state: ServerStateManager = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.server_state = server_state
        self.auth_manager = AuthManager()
        self.username: Optional[str] = None
        self.token: Optional[str] = None

    def quic_event_received(self, event) -> None:
        if isinstance(event, HandshakeCompleted):
            try:
                cid = self._quic.connection_id.hex()
                logging.info(f"[HS] Handshake completed: CID={cid}, ALPN={event.alpn_protocol}")
            except Exception as e:
                logging.error(f"Handshake error: {e}")

        elif isinstance(event, StreamDataReceived):
            self.handle_stream_data(event.stream_id, event.data, event.end_stream)

        elif isinstance(event, ConnectionTerminated):
            if self.username:
                self.server_state.remove_client(self.username)
                self.broadcast_system_message(f"User '{self.username}' left the chat.")
                self.broadcast_online_users()

    def handle_stream_data(self, stream_id: int, data: bytes, end_stream: bool):
        try:
            message = unpack(data)
            
            if self.username is None:
                self.handle_authentication(message)
            else:
                self.handle_chat_message(message)

        except Exception as e:
            logging.error(f"Error handling stream data: {e}")
            asyncio.create_task(self.async_send(MsgType.SYS, f"Error: {str(e)}"))

    def handle_authentication(self, message: dict):
        if message.get("t") != MsgType.AUTH_REQ:
            asyncio.create_task(self.async_send(MsgType.AUTH_BAD, "Please authenticate first."))
            return

        username = message.get("to")
        password = message.get("body")

        if not username or not password:
            asyncio.create_task(self.async_send(MsgType.AUTH_BAD, "Username and password required."))
            return

        if self.auth_manager.verify(username, password) or self.auth_manager.register(username, password):
            self.username = username
            self.token = self.auth_manager.issue_token(username)
            asyncio.create_task(self.async_send(MsgType.AUTH_OK, f"Welcome, {username}", token=self.token))
            self.server_state.add_client(username, self)
            self.broadcast_system_message(f"User '{username}' joined the chat.")
            self.broadcast_online_users()
        else:
            asyncio.create_task(self.async_send(MsgType.AUTH_BAD, "Authentication failed."))

    def handle_chat_message(self, message: dict):
        if message.get("t") != MsgType.CHAT:
            asyncio.create_task(self.async_send(MsgType.SYS, "Unknown command."))
            return

        body = message.get("body", "")
        target = message.get("to")

        if target:
            self.handle_private_message(target, body)
        else:
            self.broadcast_chat_message(body)

    async def async_send(self, msg_type: MsgType, body: str, to: Optional[str] = None, token: Optional[str] = None):
        new_stream = self._quic.get_next_available_stream_id()
        self._quic.send_stream_data(
            new_stream,
            pack({"v": 1, "t": int(msg_type), "body": body, "to": to, "token": token}),
            end_stream=True
        )
        self.transmit()

    def broadcast_system_message(self, message: str):
        for client_info in self.server_state.clients.values():
            asyncio.create_task(client_info.protocol.async_send(MsgType.SYS, message))

    def broadcast_online_users(self):
        online_list = ", ".join(self.server_state.get_online_users())
        msg = f"Online users: {online_list}"
        for client_info in self.server_state.clients.values():
            asyncio.create_task(client_info.protocol.async_send(MsgType.SYS, msg))

    def handle_private_message(self, target: str, body: str):
        target_client = self.server_state.get_client(target)
        if target_client:
            asyncio.create_task(target_client.protocol.async_send(
                MsgType.CHAT, f"[Private] {self.username}: {body}"
            ))
            asyncio.create_task(self.async_send(
                MsgType.CHAT, f"[Private to {target}] {body}"
            ))
        else:
            asyncio.create_task(self.async_send(
                MsgType.SYS, f"User '{target}' is not online."
            ))

    def broadcast_chat_message(self, body: str):
        for username, client_info in self.server_state.clients.items():
            if username != self.username:
                asyncio.create_task(client_info.protocol.async_send(
                    MsgType.CHAT, f"{self.username}: {body}"
                ))

async def main():
    # Load configuration
    config = load_config("server")
    
    # Initialize server state
    server_state = ServerStateManager()
    
    # Setup QUIC configuration
    quic_config = QuicConfiguration(
        is_client=False,
        alpn_protocols=config["alpn_protocols"]
    )
    quic_config.load_cert_chain(config["cert_path"], config["key_path"])

    logging.info(f"Starting QUIC chat server on {config['host']}:{config['port']}...")
    
    await serve(
        config["host"],
        config["port"],
        configuration=quic_config,
        create_protocol=lambda *args, **kwargs: ChatProtocol(
            *args, server_state=server_state, **kwargs
        )
    )
    
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server terminated by KeyboardInterrupt.")