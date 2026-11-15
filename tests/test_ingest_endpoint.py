import urllib.request
import json

payload = {
    "profile": {
        "name": "Muhammad Hudaifah Mubarak",
        "headline": "Full-Stack Software Engineer and AI Systems Architect",
        "location": "Bengaluru, India",
        "about": "Full-stack engineer dedicated to crafting scalable AI systems, multi-agent frameworks, and high-performance software ventures.",
        "skills": ["Python", "FastAPI", "React", "Next.js", "LangGraph", "mem0", "Crawl4AI", "Tailwind CSS", "Docker", "PostgreSQL"],
        "experience": [
            {
                "title": "Lead Software & Autonomous AI Engineer",
                "company": "VentureOS Autonomous Systems",
                "duration": "2024 - Present",
                "description": "Architected 7 cross-functional departments with 34 specialized autonomous agents. Built high-throughput task dispatch pipelines and enterprise SaaS infrastructure."
            },
            {
                "title": "Full-Stack AI Developer",
                "company": "Independent Software Engineering",
                "duration": "2023 - 2024",
                "description": "Engineered real-time SaaS intelligence engines, browser automation bots, and automated market monitoring pipelines."
            }
        ],
        "education": [
            {
                "school": "Vellore Institute of Technology",
                "degree": "Bachelor of Technology in Computer Science and Engineering",
                "duration": "2021 - 2025"
            }
        ]
    }
}

req = urllib.request.Request(
    "http://127.0.0.1:8000/api/ingest-profile",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode("utf-8"))
    print("Response status:", res.get("status"))
    print("Portfolio URL:", res.get("portfolio_url"))
    print("Extracted Name:", res.get("profile", {}).get("name"))
