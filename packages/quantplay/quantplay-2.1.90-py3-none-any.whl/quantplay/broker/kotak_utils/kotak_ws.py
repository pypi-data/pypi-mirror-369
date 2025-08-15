import json
import threading
import time
from collections.abc import Callable
from typing import Any, Literal

from retrying import retry  # type: ignore

from quantplay.broker.kotak_utils.kotak_ws_lib import HSIWebSocket

OLD_ORDER_FEED_URL = "wss://clhsi.kotaksecurities.com/realtime?sId={server_id}"

ORDER_FEED_URL = "wss://mis.kotaksecurities.com/realtime"
ORDER_FEED_URL_ADC = "wss://cis.kotaksecurities.com/realtime"
ORDER_FEED_URL_E21 = "wss://e21.kotaksecurities.com/realtime"
ORDER_FEED_URL_E22 = "wss://e22.kotaksecurities.com/realtime"
ORDER_FEED_URL_E41 = "wss://e41.kotaksecurities.com/realtime"
ORDER_FEED_URL_E43 = "wss://e43.kotaksecurities.com/realtime"


class NeoWebSocket:
    def __init__(
        self,
        sid: str | None,
        token: str | None,
        server_id: str | None,
        data_center: str | None,
        version: Literal["OLD", "NEW"],
    ) -> None:
        self.hsiWebsocket = None
        self.is_hsi_open = 0
        self.sid = sid
        self.access_token = token
        self.server_id = server_id
        self.version: Literal["OLD", "NEW"] = version
        self.data_center = data_center

        self.on_message: Callable[[Any], None] | None = None
        self.on_error: Callable[[Any], None] | None = None
        self.on_close: Callable[[], None] | None = None
        self.on_open: Callable[[], None] | None = None
        self.hsi_thread = None

    def on_hsi_open(self) -> None:
        server = "WEB"
        json_d = {
            "type": "CONNECTION",
            "Authorization": self.access_token,
            "Sid": self.sid,
            "source": server,
        }
        json_d = json.dumps(json_d)

        # print(f"[KOTAK_OPEN_SEND]: {json_d}")

        if self.hsiWebsocket:
            self.hsiWebsocket.send(json_d)

        if self.on_open:
            self.on_open()

    def on_hsi_close(self) -> None:
        if self.is_hsi_open == 1:
            self.is_hsi_open = 0

        if self.on_close:
            self.on_close()

        self.reconnect()

    @retry(
        wait_exponential_multiplier=3000,
        wait_exponential_max=20000,
        stop_max_attempt_number=5,
    )
    def reconnect(self) -> None:
        print("Reconnect")
        self.get_order_feed()

    def on_hsi_error(self, error: Any) -> None:
        if self.is_hsi_open == 1:
            self.is_hsi_open = 0

        if self.on_error:
            self.on_error(error)
        else:
            print("Error Occurred in Websocket! Error Message ", error)

    def on_hsi_message(self, message: Any) -> None:
        if message:
            if isinstance(message, str):
                req = json.loads(message)
                if req["type"] == "cn":
                    self.is_hsi_open = 1
                    threading.Thread(target=self.start_hsi_ping_thread).start()

        if self.on_message:
            self.on_message({"type": "order_feed", "data": message})

    def start_hsi_ping_thread(self) -> None:
        while self.hsiWebsocket and self.is_hsi_open:
            time.sleep(30)
            payload = {"type": "HB"}
            self.hsiWebsocket.send(json.dumps(payload))

    def start_hsi_websocket(self) -> None:
        if self.version == "NEW":
            url = ORDER_FEED_URL

            if self.data_center:
                if self.data_center.lower() == "adc":
                    url = ORDER_FEED_URL_ADC
                # elif self.data_center.lower() == "e21":
                #     url = ORDER_FEED_URL_E21
                # elif self.data_center.lower() == "e22":
                #     url = ORDER_FEED_URL_E22
                # elif self.data_center.lower() == "e41":
                #     url = ORDER_FEED_URL_E41
                # elif self.data_center.lower() == "e43":
                #     url = ORDER_FEED_URL_E43

        else:
            url = OLD_ORDER_FEED_URL.format(server_id=self.server_id)

        self.hsiWebsocket = HSIWebSocket(self.version)
        self.hsiWebsocket.open_connection(
            url=url,
            onopen=self.on_hsi_open,
            onmessage=self.on_hsi_message,
            onclose=self.on_hsi_close,
            onerror=self.on_hsi_error,
        )

    def start_hsi_websocket_thread(self) -> None:
        self.hsi_thread = threading.Thread(target=self.start_hsi_websocket)
        self.hsi_thread.start()

    def get_order_feed(self) -> None:
        if self.hsiWebsocket is None or self.is_hsi_open == 0:
            self.start_hsi_websocket_thread()
        else:
            print("you had already subscribed for order feed")
