r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import json
import os
import pprint

import requests

from payloop._config import Config


class Collector:
    def __init__(self, config: Config):
        self.__base = os.environ.get("PAYLOOP_COLLECTOR_URL_BASE")
        if self.__base is None:
            self.__base = "https://collector.trypayloop.com"

        self.config = config

    def fire_and_forget(self, payload):
        if os.environ.get("PAYLOOP_TEST_MODE") is None:
            try:
                requests.post(
                    f"{self.__base}/rec",
                    json=json.loads(json.dumps(payload, default=str)),
                    timeout=self.config.secs_requests_timeout,
                )
            except:
                pass
        else:
            pprint.pprint(payload)

        return self
