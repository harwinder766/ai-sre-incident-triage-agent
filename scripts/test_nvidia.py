# import os

# from dotenv import load_dotenv
# from openai import AsyncOpenAI


# load_dotenv()

# api_key = os.getenv("NVIDIA_API_KEY")
# base_url = os.getenv(
#     "NVIDIA_BASE_URL",
#     "https://integrate.api.nvidia.com/v1",
# )
# model = os.getenv(
#     "NVIDIA_MODEL",
#     "z-ai/glm-5.3-flash",
# )

# print("MODEL:", model)
# print("BASE URL:", base_url)
# print("API KEY FOUND:", bool(api_key))


# client = AsyncOpenAI(
#     api_key=api_key,
#     base_url=base_url,
# )


# async def main():

#     print("\nSending test request...\n")

#     response = await client.chat.completions.create(
#         model=model,
#         messages=[
#             {
#                 "role": "user",
#                 "content": "Reply with exactly: NVIDIA_TEST_OK",
#             }
#         ],
#         max_tokens=20,
#         temperature=0,
#         reasoning_effort="low",
#     )

#     print("Response:")
#     print(response.choices[0].message.content)


# if __name__ == "__main__":
#     import asyncio

#     asyncio.run(main())

import os
import asyncio
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

XKIRO_API_KEY = os.getenv("XKIRO_API_KEY")

XKIRO_BASE_URL = "https://api.xkiro.com/v1"

# Start with a model shown in xKiro's documentation.
XKIRO_MODEL = "qwen/qwen3.8-omni-flash:free"


if not XKIRO_API_KEY:
    raise ValueError("XKIRO_API_KEY is not configured.")


client = AsyncOpenAI(
    api_key=XKIRO_API_KEY,
    base_url=XKIRO_BASE_URL,
)


async def main():

    print("Base URL:", XKIRO_BASE_URL)
    print("Model:", XKIRO_MODEL)
    print("API Key Found:", bool(XKIRO_API_KEY))

    print("\nSending request...\n")

    start = time.perf_counter()

    response = await client.chat.completions.create(
        model=XKIRO_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: XKIRO_TEST_OK",
            }
        ],
        temperature=0,
        max_tokens=20,
    )

    elapsed = time.perf_counter() - start

    print("Response:")
    print(response.choices[0].message.content)

    print(f"\nTime: {elapsed:.2f} seconds")

    if response.usage:
        print("\nUsage:")
        print("Input tokens:", response.usage.prompt_tokens)
        print("Output tokens:", response.usage.completion_tokens)
        print("Total tokens:", response.usage.total_tokens)


if __name__ == "__main__":
    asyncio.run(main())