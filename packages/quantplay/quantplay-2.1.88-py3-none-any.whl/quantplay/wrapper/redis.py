import traceback
from os import environ

import redis  # type:ignore


class Redis:
    error = False
    __instance = None

    @staticmethod
    def get_instance():
        if Redis.__instance is None:
            Redis()

        return Redis.__instance

    def __init__(self) -> None:
        print("Creating Redis instance")
        if (
            environ.get("REDIS_HOST") is None
            or environ.get("REDIS_PORT") is None
            or environ.get("REDIS_PASSWORD") is None
        ):
            self.error = True
            return

        try:
            self.redis_client = redis.Redis(
                host=environ.get("REDIS_HOST", ""),
                port=int(environ.get("REDIS_PORT", 0)),
                password=environ.get("REDIS_PASSWORD", ""),
                decode_responses=True,
                ssl=True,
            )

        except Exception:
            traceback.print_exc()
            self.error = True

        Redis.__instance = self

    def hget(self, key: int):
        if self.error:
            return None

        return self.redis_client.hget(f"mktx:{key}", "c")  # type: ignore

    def hget_multi(self, keys: list[int]) -> list[float] | None:
        if self.error:
            return None

        pipe = self.redis_client.pipeline()  # type: ignore

        for key in keys:
            pipe.hget(f"mktx:{key}", "c")

        return pipe.execute()  # type: ignore
