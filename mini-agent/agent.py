import time
from google import genai
from google.genai import errors, types
from pydantic import BaseModel

client = genai.Client()
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]

# 💸 Price per 1 million tokens (PLACEHOLDER numbers, check Google's pricing page)
PRICE_IN = 0.10
PRICE_OUT = 0.40

# 🔧 Tools
def get_weather(city: str) -> dict:
    """Get the current weather for a city."""
    print(f"🔧 Tool called: get_weather({city})")
    fake = {"toronto": "5°C, rainy", "london": "12°C, cloudy"}
    return {"city": city, "weather": fake.get(city.lower(), "20°C, sunny")}

def calculate(a: float, b: float, operation: str) -> dict:
    """Do math on two numbers. operation is one of: add, subtract, multiply, divide."""
    print(f"🔧 Tool called: calculate({a} {operation} {b})")
    if operation == "add":
        return {"result": a + b}
    if operation == "subtract":
        return {"result": a - b}
    if operation == "multiply":
        return {"result": a * b}
    if operation == "divide":
        return {"result": a / b} if b != 0 else {"error": "can't divide by 0"}
    return {"error": "unknown operation"}

class Answer(BaseModel):
    city: str
    weather: str
    math_result: float
    summary: str

# 🧊 temperature=0 → more consistent answers
tool_config = types.GenerateContentConfig(tools=[get_weather, calculate], temperature=0)
json_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=Answer,
    temperature=0,
)

def ask(prompt, config):
    for model in MODELS:
        try:
            start = time.time()  # ⏱️ start the stopwatch
            response = client.models.generate_content(
                model=model, contents=prompt, config=config
            )
            seconds = time.time() - start  # ⏱️ stop it

            # 🚕 read the taxi meter
            usage = response.usage_metadata
            tokens_in = usage.prompt_token_count or 0
            tokens_out = usage.candidates_token_count or 0
            cost = (tokens_in * PRICE_IN + tokens_out * PRICE_OUT) / 1_000_000

            print(f"✅ {model} | ⏱️ {seconds:.2f}s | 🪙 {tokens_in} in, {tokens_out} out | 💸 ${cost:.6f}")
            return response
        except errors.APIError as e:
            print("⚠️", model, "failed:", e.code, "→ trying next")
    raise RuntimeError("All models failed")

