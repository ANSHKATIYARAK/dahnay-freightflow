import urllib.request
import json

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/dispatch",
    data=json.dumps({"agent_name": "ai-engineer", "prompt": "Architect LangGraph agent graph"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        print("API Dispatch Response:")
        print("Status:", res.get("status"))
        print("Agent:", res.get("agent_name"))
        print("Department:", res.get("department"))
        print("Execution time:", res.get("execution_time_ms"), "ms")
        print("Output preview:", res.get("output_text")[:200])
except Exception as e:
    print("Error:", e)
