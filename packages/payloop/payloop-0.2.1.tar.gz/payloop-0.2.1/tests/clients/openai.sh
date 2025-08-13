#!/usr/bin/env python3

import os
from openai import OpenAI
from payloop import Payloop

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

client = OpenAI(
    api_key="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"
)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).openai.register(client)

# Make sure registering the same client again does not cause an issue.
payloop.openai.register(client)

# Test setting attribution.
payloop.attribution(
    parent_id=123,
    parent_name="Abc",
    parent_uuid="95473da0-5d7a-435d-babf-d64c5dabe971",
    subsidiary_id=456,
    subsidiary_name="Def",
    subsidiary_uuid="b789eaf4-c925-4a79-85b1-34d270342353"
)

client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "how are you today?"}
    ]
)
