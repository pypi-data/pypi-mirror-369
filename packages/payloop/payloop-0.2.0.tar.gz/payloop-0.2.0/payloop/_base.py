r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

import copy
import json
import time

from google.protobuf import json_format

from payloop._config import Config
from payloop._network import Collector


class BaseClient:
    def __init__(self, config: Config):
        self.client = None
        self.config = config

    def dict_to_json(self, dict_):
        result = {}
        for key, value in dict_.items():
            if isinstance(value, list):
                result[key] = self.list_to_json(value)
            elif isinstance(value, dict):
                result[key] = self.dict_to_json(value)
            else:
                if hasattr(value, "__dict__"):
                    result[key] = self.dict_to_json(value.__dict__)
                else:
                    result[key] = value

        return result

    def _format_payload(
        self, client_title, client_version, start_time, end_time, query, response
    ):
        response_json = self.response_to_json(response)

        payload = {
            "attribution": self.config.attribution,
            "conversation": {
                "client": {"title": client_title, "version": client_version},
                "query": query,
                "response": response_json,
            },
            "meta": {
                "api": {"key": self.config.api_key},
                "sdk": {"version": self.config.version},
            },
            "time": {"end": end_time, "start": start_time},
            "tx": {"uuid": str(self.config.tx_uuid)},
        }

        return payload

    def _invoke(
        self, client_title, client_version, method, kwargs, response_is_protobuf=False
    ):
        start = time.time()

        raw_response = method(**kwargs)
        formatted_response = copy.deepcopy(raw_response)

        if response_is_protobuf:
            formatted_response = json.loads(
                json_format.MessageToJson(formatted_response.__dict__["_pb"])
            )

        Collector().fire_and_forget(
            self._format_payload(
                client_title,
                client_version,
                start,
                time.time(),
                kwargs,
                formatted_response,
            )
        )

        return raw_response

    def list_to_json(self, list_):
        result = []
        for entry in list_:
            if isinstance(entry, list):
                result.append(self.list_to_json(entry))
            elif isinstance(entry, dict):
                result.append(self.dict_to_json(entry))
            else:
                if hasattr(entry, "__dict__"):
                    result.append(self.dict_to_json(entry.__dict__))
                else:
                    result.append(entry)

        return result

    def response_to_json(self, response):
        data = response
        if not isinstance(data, dict):
            data = response.__dict__

        result = {}

        for key, value in data.items():
            if isinstance(value, list):
                result[key] = self.list_to_json(value)
            elif isinstance(value, dict):
                result[key] = self.dict_to_json(value)
            else:
                if hasattr(value, "__dict__"):
                    result[key] = self.dict_to_json(value.__dict__)
                else:
                    result[key] = value

        return result


class BaseProvider:
    def __init__(self, parent):
        self.client = None
        self.parent = parent
        self.config = parent.config
