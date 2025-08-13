r"""
 ___           _
| _ \__ _ _  _| |___  ___ _ __
|  _/ _` | || | / _ \/ _ \ '_ \
|_| \__,_|\_, |_\___/\___/ .__/
          |__/           |_|AI             07312025 / optimus codex
"""

from payloop._base import BaseClient


class Anthropic(BaseClient):
    def register(self, client):
        if not hasattr(client, "messages"):
            raise RuntimeError("client provided is not instance of Anthropic")

        if not hasattr(client, "_payloop_installed"):
            client.messages.actual_create = client.messages.create
            client.messages.create = self.invoke
            client._payloop_installed = True

        self.client = client

        return self

    def invoke(self, **kwargs):
        return self._invoke(
            "anthropic",
            self.client._version,
            self.client.messages.actual_create,
            kwargs,
        )


class Google(BaseClient):
    def register(self, client):
        if not hasattr(client, "models"):
            raise RuntimeError("client provided is not instance of genai.Client")

        if not hasattr(client, "_payloop_installed"):
            client.models.actual_generate_content = client.models.generate_content
            client.models.generate_content = self.invoke
            client._payloop_installed = True

        self.client = client

        return self

    def invoke(self, **kwargs):
        return self._invoke(
            "google", self.client._version, self.client.actual_generate_content, kwargs
        )


class LangChain(BaseClient):
    def register(self, chatopenai=None, chatvertexai=None):
        if chatopenai is not None:
            if not hasattr(chatopenai, "client"):
                raise RuntimeError("client provided is not instance of ChatOpenAI")

            if not hasattr(chatopenai.client._client, "_payloop_installed"):
                chatopenai.client._client.actual_chat_completions_create = (
                    chatopenai.client._client.chat.completions.create
                )
                chatopenai.client._client.chat.completions.create = (
                    self.invoke_chatopenai
                )
                chatopenai.client._client._payloop_installed = True

            self.client_title = "langchain::chatopenai"
            self.client = chatopenai.client._client
        elif chatvertexai is not None:
            if not hasattr(chatvertexai, "prediction_client"):
                raise RuntimeError("client provided isnot instance of ChatVertexAI")

            if not hasattr(chatvertexai.prediction_client, "_payloop_installed"):
                chatvertexai.prediction_client.actual_generate_content = (
                    chatvertexai.prediction_client.generate_content
                )
                chatvertexai.prediction_client.generate_content = (
                    self.invoke_chatvertexai
                )
                chatvertexai.prediction_client._payloop_installed = True

            self.client_title = "langchain::chatvertexai"
            self.client = chatvertexai.prediction_client
        else:
            raise RuntimeError("LangChain::register called without client")

        return self

    def invoke_chatopenai(self, **kwargs):
        return self._invoke(
            self.client_title, None, self.client.actual_chat_completions_create, kwargs
        )

    def invoke_chatvertexai(self, **kwargs):
        return self._invoke(
            self.client_title,
            None,
            self.client.actual_generate_content,
            kwargs,
            uses_protobuf=True,
        )


class OpenAi(BaseClient):
    def register(self, client):
        if not hasattr(client, "chat"):
            raise RuntimeError("client provided is not instance of OpenAI")

        if not hasattr(client, "_payloop_installed"):
            client.chat.completions.actual_chat_completions_create = (
                client.chat.completions.create
            )
            client.chat.completions.create = self.invoke
            client._payloop_installed = True

        self.client = client

        return self

    def invoke(self, **kwargs):
        return self._invoke(
            "openai",
            self.client._version,
            self.client.chat.completions.actual_chat_completions_create,
            kwargs,
        )
