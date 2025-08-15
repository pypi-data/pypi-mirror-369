import ssl
import time

import websocket

from quantplay.utils.constant import Constants

logger = Constants.logger


class AngelOneOrderUpdateWS(object):
    WEBSOCKET_URI = "wss://tns.angelone.in/smart-order-update"
    HEARTBEAT_MESSAGE = "ping"  # Heartbeat message to maintain Socket connection.
    HEARTBEAT_INTERVAL_SECONDS = (
        10  # Interval for sending heartbeat messages to keep the connection alive.
    )
    MAX_CONNECTION_RETRY_ATTEMPTS = (
        2  # Max retry attempts to establish Socket connection in case of failure.
    )
    RETRY_DELAY_SECONDS = (
        10  # Delay between retry attempts when reconnecting to Socket in case of failure.
    )
    wsapp = None  # Socket connection instance
    last_pong_timestamp = None  # Timestamp of the last received pong message
    current_retry_attempt = 0  # Current retry attempt count

    def __init__(
        self,
        auth_token: str,
        api_key: str,
        client_code: str,
        feed_token: str,
    ):
        self.auth_token = auth_token
        self.api_key = api_key
        self.client_code = client_code
        self.feed_token = feed_token

    def on_message(self, wsapp: websocket.WebSocket, message: str | bytes):
        print(message)

    def on_data(
        self,
        wsapp: websocket.WebSocket,
        message: str,
        data_type: int,
        continue_flag: bool,
    ):
        self.on_message(wsapp, message)

    def on_open(self, wsapp: websocket.WebSocket):
        logger.info("Connection opened")

    def on_error(self, wsapp: websocket.WebSocket, error: str):
        logger.error("Error: %s", error)

    def on_close(
        self, wsapp: websocket.WebSocket, close_status_code: int, close_msg: str
    ):
        logger.info("Connection closed")
        self.retry_connect()

    def on_pong(self, wsapp: websocket.WebSocket, data: str):
        if data == self.HEARTBEAT_MESSAGE:
            timestamp = time.time()
            self.last_pong_timestamp = timestamp
        else:
            self.on_data(wsapp, data, websocket.ABNF.OPCODE_BINARY, False)

    def check_connection_status(self):
        current_time = time.time()
        if (
            self.last_pong_timestamp is not None
            and current_time - self.last_pong_timestamp
            > 2 * self.HEARTBEAT_INTERVAL_SECONDS
        ):
            self.close_connection()

    def connect(self):
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "x-api-key": self.api_key,
            "x-client-code": self.client_code,
            "x-feed-token": self.feed_token,
        }
        try:
            self.wsapp = websocket.WebSocketApp(
                self.WEBSOCKET_URI,
                header=headers,
                on_open=self.on_open,
                on_error=self.on_error,
                on_close=self.on_close,
                on_data=self.on_data,
                on_pong=self.on_pong,
            )
            self.wsapp.run_forever(  # type: ignore
                sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=self.HEARTBEAT_INTERVAL_SECONDS,
                ping_payload=self.HEARTBEAT_MESSAGE,
            )
        except Exception as e:
            logger.error("Error connecting to WebSocket: %s", e)
            self.retry_connect()

    def retry_connect(self):
        if self.current_retry_attempt < self.MAX_CONNECTION_RETRY_ATTEMPTS:
            logger.info(
                "Retrying connection (Attempt %s)...", self.current_retry_attempt + 1
            )
            time.sleep(self.RETRY_DELAY_SECONDS)
            self.current_retry_attempt += 1
            self.connect()
        else:
            logger.warning("Max retry attempts reached.")

    def close_connection(self):
        if self.wsapp:
            self.wsapp.close()  # type: ignore
