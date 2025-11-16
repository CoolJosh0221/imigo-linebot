from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="token-abc123",
)

completion = client.chat.completions.create(
    model="aisingapore/Llama-SEA-LION-v3.5-8B-R",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)