import asyncio
import httpx
import time

async def probe_model(model_name: str, concurrency: int = 1):
    url = f"http://localhost:7861/unified/v1/models/{model_name}:generateContent?key=pwd"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": "Hello, this is a connectivity test. Reply with OK."}]}]
    }
    
    async def make_request(idx):
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"[{model_name}] Request {idx} starting...")
            resp = await client.post(url, json=payload)
            print(f"[{model_name}] Request {idx} finished with status {resp.status_code}")
            return resp.status_code, resp.text

    print(f"\n--- Probing Model: {model_name} (Concurrency: {concurrency}) ---")
    tasks = [make_request(i) for i in range(concurrency)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for code, text in results if code == 200)
    print(f"Result: {success_count}/{concurrency} successful.")
    if success_count < concurrency:
        print(f"Last Error: {results[-1][1]}")

async def run_diagnostics():
    # 1. Test Lite model (Single) - Reported 500
    await probe_model("gemini-3.1-flash-lite-preview", 1)
    
    # 2. Test Lite model WITHOUT 'preview' tag - Hypothesis: will pass filter
    await probe_model("gemini-3.1-flash-lite", 1)
    
    # 3. Test Standard Flash WITHOUT 'preview' tag
    await probe_model("gemini-3-flash", 1)
    
    # 4. Test 1.5 Flash (legacy check)
    await probe_model("gemini-1.5-flash", 1)

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
