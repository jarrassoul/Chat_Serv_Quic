# #chat_client.py
# import asyncio
# import sys
# import logging
# from typing import Optional
# from aioquic.asyncio import connect, QuicConnectionProtocol
# from aioquic.quic.configuration import QuicConfiguration

# from src.protocol.message import MsgType, pack, unpack
# from src.utils.config_loader import load_config
# from src.protocol.states import ConnectionState
# from .client_state import ClientStateManager

# logging.basicConfig(level=logging.INFO)

# class ChatClientProtocol(QuicConnectionProtocol):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.state_manager = ClientStateManager()
#         self.token: Optional[str] = None

#     def quic_event_received(self, event) -> None:
#         from aioquic.quic.events import StreamDataReceived
#         if isinstance(event, StreamDataReceived):
#             try:
#                 message = unpack(event.data)
#             except Exception as e:
#                 logging.error(f"Error decoding message: {e}")
#                 return
#             t = message.get("t")
#             if t == MsgType.AUTH_OK:
#                 print(f"\n[SYSTEM] {message.get('body')}")
#                 self.token = message.get("token")
#             elif t == MsgType.AUTH_BAD:
#                 print(f"\n[AUTH ERROR] {message.get('body')}")
#             elif t == MsgType.CHAT:
#                 print(f"\n{message.get('body')}")
#             elif t == MsgType.SYS:
#                 print(f"\n[SYSTEM] {message.get('body')}")
#             else:
#                 print(f"\n[UNKNOWN] {message}")

#     async def send_message(self, msg: dict):
#         new_stream = self._quic.get_next_available_stream_id()
#         self._quic.send_stream_data(new_stream, pack(msg), end_stream=True)
#         self.transmit()

# async def main():
#     # Load configuration
#     config = load_config("client")
    
#     # Get user credentials
#     username = input("Enter username: ").strip()
#     password = input("Enter password: ").strip()

#     # Setup QUIC configuration
#     quic_config = QuicConfiguration(is_client=True, alpn_protocols=["chat/1"])
#     quic_config.verify_mode = 0  # Accept self-signed certificates

#     async with connect(
#         config["server_host"],
#         config["server_port"],
#         configuration=quic_config,
#         create_protocol=ChatClientProtocol
#     ) as protocol:
#         # Send authentication
#         auth_msg = {
#             "v": 1,
#             "t": MsgType.AUTH_REQ,
#             "to": username,
#             "body": password,
#             "token": None
#         }
#         await protocol.send_message(auth_msg)
#         await asyncio.sleep(1)

#         if not hasattr(protocol, "token") or protocol.token is None:
#             print("Authentication failed, exiting.")
#             return

#         print("Logged in. Type messages to chat. Type '/quit' to exit.")
        
#         while True:
#             try:
#                 line = await asyncio.get_event_loop().run_in_executor(
#                     None, sys.stdin.readline
#                 )
                
#                 if not line:
#                     continue
                    
#                 line = line.strip()
#                 if line.lower() == "/quit":
#                     print("Exiting chat.")
#                     break

#                 msg_out = {
#                     "v": 1,
#                     "t": MsgType.CHAT,
#                     "body": line,
#                     "to": None,
#                     "token": protocol.token
#                 }

#                 if line.startswith("@"):
#                     parts = line.split(" ", 1)
#                     if len(parts) != 2:
#                         print("Invalid private message format. Use '@username message'")
#                         continue
#                     msg_out["to"] = parts[0][1:]
#                     msg_out["body"] = parts[1]

#                 await protocol.send_message(msg_out)

#             except Exception as e:
#                 logging.error(f"Error sending message: {e}")

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\nClient terminated by user.")





import asyncio
import sys
import logging
from typing import Optional
from aioquic.asyncio import connect, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration

from src.protocol.message import MsgType, pack, unpack
from src.utils.config_loader import load_config
from src.protocol.states import ConnectionState
from .client_state import ClientStateManager

logging.basicConfig(level=logging.INFO)

class ChatClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state_manager = ClientStateManager()
        self.token: Optional[str] = None

    def quic_event_received(self, event) -> None:
        from aioquic.quic.events import StreamDataReceived
        if isinstance(event, StreamDataReceived):
            try:
                message = unpack(event.data)
            except Exception as e:
                logging.error(f"Error decoding message: {e}")
                return
            t = message.get("t")
            if t == MsgType.AUTH_OK:
                print(f"\n[SYSTEM] {message.get('body')}")
                self.token = message.get("token")
                self.state_manager.transition_to(ConnectionState.AUTHENTICATED)
            elif t == MsgType.AUTH_BAD:
                print(f"\n[AUTH ERROR] {message.get('body')}")
            elif t == MsgType.CHAT:
                print(f"\n{message.get('body')}")
            elif t == MsgType.SYS:
                print(f"\n[SYSTEM] {message.get('body')}")
            else:
                print(f"\n[UNKNOWN] {message}")

    async def send_message(self, msg: dict):
        try:
            new_stream = self._quic.get_next_available_stream_id()
            self._quic.send_stream_data(new_stream, pack(msg), end_stream=True)
            self.transmit()
        except Exception as e:
            logging.error(f"Error sending message: {e}")

async def send_keep_alive(protocol, interval=15):
    """Send keep-alive pings to the server every `interval` seconds."""
    while protocol.state_manager.is_connected:
        await asyncio.sleep(interval)
        try:
            await protocol.send_message({"t": MsgType.SYS, "body": "ping"})
            logging.info("Keep-alive ping sent.")
        except Exception as e:
            logging.error(f"Keep-alive error: {e}")

async def main():
    # Load configuration
    config = load_config("client")
    
    # Get user credentials
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # Setup QUIC configuration
    quic_config = QuicConfiguration(is_client=True, alpn_protocols=["chat/1"])
    quic_config.verify_mode = 0  # Accept self-signed certificates

    async with connect(
        config["server_host"],
        config["server_port"],
        configuration=quic_config,
        create_protocol=ChatClientProtocol
    ) as protocol:
        # Send authentication
        auth_msg = {
            "v": 1,
            "t": MsgType.AUTH_REQ,
            "to": username,
            "body": password,
            "token": None
        }
        await protocol.send_message(auth_msg)
        await asyncio.sleep(1)

        if not hasattr(protocol, "token") or protocol.token is None:
            print("Authentication failed, exiting.")
            return

        print("Logged in. Type messages to chat. Type '/quit' to exit.")
        
        # Start keep-alive pings
        asyncio.create_task(send_keep_alive(protocol, interval=15))

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                
                if not line:
                    continue
                    
                line = line.strip()
                if line.lower() == "/quit":
                    print("Exiting chat.")
                    break

                msg_out = {
                    "v": 1,
                    "t": MsgType.CHAT,
                    "body": line,
                    "to": None,
                    "token": protocol.token
                }

                if line.startswith("@"):
                    parts = line.split(" ", 1)
                    if len(parts) != 2:
                        print("Invalid private message format. Use '@username message'")
                        continue
                    msg_out["to"] = parts[0][1:]
                    msg_out["body"] = parts[1]

                await protocol.send_message(msg_out)

            except Exception as e:
                logging.error(f"Error reading input: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient terminated by user.")