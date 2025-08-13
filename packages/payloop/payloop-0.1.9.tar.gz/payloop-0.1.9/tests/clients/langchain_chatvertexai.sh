#!/usr/bin/env python3

import os
from payloop import Payloop
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage

if os.environ.get("PAYLOOP_TEST_MODE", None) != "1":
    raise RuntimeError("PAYLOOP_TEST_MODE is not set")

messages = [HumanMessage("What is the most popular artificial sweetener?")]

obj = ChatVertexAI(
    model_name="gemini-2.0-flash",
    temperature=0,
    seed=42,
)

payloop = Payloop(
    api_key="Ba2ghufk9YncYhywqQLyAPFq9kGScSLUi1xZ4A66nVyqWlJBVGZJRWGNHeCgBeCHOkgTXWsQH1YMchknyMusYpfR02eyE2JTEKlIm-oTCFPx24yn563Aucb88kMI98ABVXyhse02Fz8i9qrG1UzAalLmYPrpRUS03SCb7AV4wsw"
).langchain.register(chatvertexai=obj)

obj.invoke(messages)
