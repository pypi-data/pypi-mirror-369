#!/usr/bin/env python3

import asyncio
import os
from payloop import Payloop
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

openrouter_provider = OpenAIProvider(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

o4_mini = OpenAIModel(
    "o4-mini",
    provider=openrouter_provider,
    settings=ModelSettings(max_tokens=1024)
)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).openai.register(openrouter_provider.client)

agent = Agent(
    o4_mini,
    system_prompt="Be concise, reply with one sentence.",
)

#result = agent.run_sync("Hello!")

async def run_agent():
    async with agent.run_stream("Hello!") as result:
        async for chunk in result.stream_text(delta=True):
            print(chunk)

if __name__ == "__main__":
    asyncio.run(run_agent())
