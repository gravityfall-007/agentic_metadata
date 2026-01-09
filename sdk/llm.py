import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL_PRICING = {
    "llama-3.3-70b-versatile": 0.000059,
    "llama-3.1-8b-instant": 0.00005
}

def call_llm(prompt: str, model="llama-3.1-8b-instant"):
    start = time.time()

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    duration_ms = int((time.time() - start) * 1000)

    usage = completion.usage
    tokens_in = usage.prompt_tokens
    tokens_out = usage.completion_tokens

    cost = ((tokens_in + tokens_out) / 1000) * MODEL_PRICING.get(model, 0)

    return {
        "response": completion.choices[0].message.content,
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost, 6),
        "duration_ms": duration_ms
    }
