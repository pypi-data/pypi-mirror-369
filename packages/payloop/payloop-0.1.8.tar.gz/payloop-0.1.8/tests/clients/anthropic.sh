#!/usr/bin/env python3

import anthropic
import os
from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

client = anthropic.Anthropic(
    api_key="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"
)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).anthropic.register(client)

client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
