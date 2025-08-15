import traceback
from typing import Literal

import polars as pl

from quantplay.broker.xts import XTS
from quantplay.broker.xts_utils_v2.ConnectV2 import XTSConnectV2
from quantplay.broker.xts_utils_v2.InteractiveSocketClientV2 import (
    OrderSocket_io_V2,
)
from quantplay.exception.exceptions import InvalidArgumentException, TokenException


XTS_ROOT_URL_MAP = {
    "A": "https://smpa.jainam.in:6543",
    "B": "https://smpb.jainam.in:4143",
    "C": "https://smpc.jainam.in:14543",
}

XTS_LOGIN_URL_MAP = {
    "https://smpa.jainam.in:6543": "https://smpa.jainam.in:4000",
    "https://smpb.jainam.in:4143": "https://smpa.jainam.in:4001",
    "https://smpc.jainam.in:14543": "https://smpc.jainam.in:4003",
}


class Jainam(XTS):
    def __init__(
        self,
        api_secret: str | None = None,
        api_key: str | None = None,
        md_api_key: str | None = None,
        md_api_secret: str | None = None,
        wrapper: str | None = None,
        md_wrapper: str | None = None,
        client_id: str | None = None,
        load_instrument: bool = True,
        is_dealer: bool = False,
        XTS_type: Literal["A", "B", "C"] = "A",
    ) -> None:
        super().__init__(
            root_url=XTS_ROOT_URL_MAP[XTS_type],
            api_key=api_key,
            api_secret=api_secret,
            md_api_key=md_api_key,
            md_api_secret=md_api_secret,
            wrapper=wrapper,
            md_wrapper=md_wrapper,
            ClientID=client_id,
            is_dealer=is_dealer,
            load_instrument=load_instrument,
        )

        if is_dealer:
            self.ClientID = "*****"

        self.ORDER_POLLING_INTERVAL = 5

    def login(
        self, api_key: str, api_secret: str, md_api_key: str, md_api_secret: str
    ) -> None:
        try:
            self.wrapper = XTSConnectV2(
                apiKey=api_key,
                secretKey=api_secret,
                root=self.root_url,
            )

            root = XTS_LOGIN_URL_MAP[self.root_url]

            xt_core_response = self.invoke_xts_api(self.wrapper.session_login, root=root)

            self.md_wrapper = XTSConnectV2(
                apiKey=md_api_key,
                secretKey=md_api_secret,
                root=self.root_url,
            )
            md_response = self.invoke_xts_api(self.md_wrapper.marketdata_login)

            if "type" not in xt_core_response or xt_core_response["type"] != "success":
                print(f"api login response {xt_core_response}")
                raise TokenException("Api key credentials are incorrect")

            if "type" not in md_response or md_response["type"] != "success":
                print(f"market data login response {md_response}")
                raise TokenException("Market data api credentials are invalid")

            self.ClientID = xt_core_response["result"]["userID"]

        except TokenException:
            raise

        except Exception:
            traceback.print_exc()
            raise InvalidArgumentException("Invalid api key/secret")

    def stream_order_updates_ws(self) -> None:
        if self.wrapper.token is None:
            raise InvalidArgumentException("XTS Token Missing")

        socket = OrderSocket_io_V2(
            userID=self.ClientID,
            token=self.wrapper.token,
            root_url=self.root_url,
        )
        socket.setup_event_listners(on_order=self.order_event_handler)
        socket.connect()

    def stream_order_updates(self) -> None:
        self.stream_order_updates_legacy()

    def orders(self, tag: str | None = None, add_ltp: bool = True) -> pl.DataFrame:
        orders = super().orders(tag, add_ltp)
        orders = orders.with_columns(
            pl.when(
                pl.col("status").eq("CANCELLED")
                & pl.col("status_message")
                .str.to_lowercase()
                .str.replace_all(" ", "")
                .str.contains("selftrade")
            )
            .then(pl.lit("REJECTED"))
            .otherwise(pl.col("status"))
            .alias("status")
        )

        return orders
