"""
Portfolio Builder: Generates a complete, modern, responsive personal portfolio.
Can ingest LinkedIn extracted JSON or default profile metadata.
"""

import os
import json
import sys

def build_portfolio(profile_data: dict, output_dir: str = "build/portfolio") -> str:
    os.makedirs(output_dir, exist_ok=True)
    
    name = profile_data.get("name", "Muhammad Hudaifah Mubarak")
    headline = profile_data.get("headline", "Full-Stack Software Engineer & AI Systems Architect")
    location = profile_data.get("location", "")
    about = profile_data.get("about", "Passionate engineer specializing in autonomous agent workflows, distributed systems, and scalable full-stack applications. Dedicated to building impactful software that solves real-world operational bottlenecks.")
    linkedin_url = profile_data.get("url", "https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279")
    
    # Skills list
    skills = profile_data.get("skills", ["Python", "FastAPI", "React", "Next.js", "Tailwind CSS", "LangGraph", "Docker", "PostgreSQL", "Crawl4AI", "mem0"])
    
    # Experience list
    experience = profile_data.get("experience", [
        {
            "title": "Lead Software & Autonomous AI Engineer",
            "company": "VentureOS Autonomous Systems",
            "duration": "2024 - Present",
            "description": "Architected and orchestrated 7 cross-functional departments with 34 specialized autonomous agents. Built high-throughput task dispatch pipelines and enterprise SaaS infrastructure."
        },
        {
            "title": "Full-Stack AI Developer",
            "company": "Independent Software Engineering",
            "duration": "2023 - 2024",
            "description": "Engineered real-time SaaS intelligence engines, browser automation bots, and automated market monitoring pipelines."
        }
    ])

    # Education list
    education = profile_data.get("education", [
        {
            "school": "University of Technology",
            "degree": "Bachelor of Technology in Computer Science & Engineering",
            "duration": "2020 - 2024"
        }
    ])

    # Build Experience HTML
    experience_html = ""
    for exp in experience:
        title = exp.get("title", "")
        company = exp.get("company", "")
        dur = exp.get("duration", "")
        desc = exp.get("description", "")
        desc_p = f'<p class="text-xs text-slate-400 mt-2 leading-relaxed">{desc}</p>' if desc else ""
        experience_html += f"""
        <div class="relative pl-8 pb-8 border-l border-blue-500/30 last:border-l-0">
            <div class="absolute -left-1.5 top-1 w-3 h-3 rounded-full bg-blue-500 ring-4 ring-slate-950"></div>
            <div class="text-xs font-semibold text-blue-400">{dur}</div>
            <div class="text-base font-bold text-white mt-0.5">{title}</div>
            <div class="text-sm text-slate-300 font-medium">{company}</div>
            {desc_p}
        </div>
        """

    # Build Education HTML
    education_html = ""
    for edu in education:
        school = edu.get("school", "")
        degree = edu.get("degree", "")
        dur = edu.get("duration", "")
        education_html += f"""
        <div class="glass-card p-6 rounded-2xl border border-slate-800">
            <div class="flex items-center justify-between mb-2">
                <div class="text-base font-bold text-white">{degree or 'Degree'}</div>
                {f'<span class="text-xs text-blue-400 font-medium">{dur}</span>' if dur else ''}
            </div>
            <div class="text-sm text-slate-400">{school}</div>
        </div>
        """

    # Build Skills HTML
    skills_chips = "".join([f'<span class="px-3.5 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 hover:text-white hover:border-slate-700 transition">{s}</span>' for s in skills])

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {headline}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .glass-card {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .glow {{
            background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.18) 0%, transparent 70%);
        }}
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen antialiased selection:bg-blue-600 selection:text-white flex flex-col justify-between">

    <!-- Top Navigation -->
    <header class="sticky top-0 z-50 glass-card border-b border-slate-800/80 px-6 py-4">
        <div class="max-w-6xl mx-auto flex items-center justify-between">
            <a href="#" class="font-extrabold text-lg tracking-tight bg-gradient-to-r from-blue-400 via-indigo-300 to-white bg-clip-text text-transparent">
                {name.split()[0]}<span class="text-blue-500">.</span>dev
            </a>
            <nav class="hidden md:flex items-center gap-8 text-sm font-medium text-slate-400">
                <a href="#about" class="hover:text-white transition">About</a>
                <a href="#experience" class="hover:text-white transition">Experience</a>
                <a href="#projects" class="hover:text-white transition">Projects</a>
                <a href="#skills" class="hover:text-white transition">Skills</a>
                <a href="#contact" class="hover:text-white transition">Contact</a>
            </nav>
            <div class="flex items-center gap-3">
                <a href="/ingest" class="px-3.5 py-1.5 rounded-full glass-card hover:bg-slate-800 text-slate-300 font-semibold text-xs transition border border-slate-700/60 flex items-center gap-1.5">
                    <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-blue-400"></i> Sync Profile
                </a>
                <a href="{linkedin_url}" target="_blank" class="px-4 py-2 rounded-full bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs transition shadow-lg shadow-blue-600/30 flex items-center gap-2">
                    <i data-lucide="linkedin" class="w-4 h-4"></i> Connect
                </a>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative pt-24 pb-20 px-6 glow overflow-hidden">
        <div class="max-w-4xl mx-auto text-center">
            <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-6">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                Open to Opportunities & Collaborations
            </div>
            <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.15] mb-6">
                Hi, I'm <span class="bg-gradient-to-r from-blue-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">{name}</span>.
            </h1>
            <p class="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
                {headline} {f'— based in {location}' if location else ''}
            </p>
            <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
                <a href="#projects" class="w-full sm:w-auto px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm transition shadow-xl shadow-blue-600/25 flex items-center justify-center gap-2">
                    <i data-lucide="folder-git-2" class="w-4 h-4"></i> View Featured Projects
                </a>
                <a href="{linkedin_url}" target="_blank" class="w-full sm:w-auto px-8 py-4 rounded-xl glass-card hover:bg-slate-800 text-slate-200 font-semibold text-sm transition border border-slate-700/60 flex items-center justify-center gap-2">
                    <i data-lucide="external-link" class="w-4 h-4"></i> LinkedIn Profile
                </a>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="py-20 px-6 border-t border-slate-800/80 bg-slate-900/40">
        <div class="max-w-4xl mx-auto">
            <div class="text-center mb-12">
                <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">Background & Philosophy</h2>
                <h3 class="text-3xl font-bold tracking-tight">About Me</h3>
            </div>
            <div class="glass-card p-8 sm:p-10 rounded-3xl border border-slate-800 space-y-4 text-slate-300 leading-relaxed text-base">
                <p>{about}</p>
            </div>
        </div>
    </section>

    <!-- Experience Section -->
    <section id="experience" class="py-20 px-6 border-t border-slate-800">
        <div class="max-w-4xl mx-auto">
            <div class="text-center mb-16">
                <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">Career Journey</h2>
                <h3 class="text-3xl font-bold tracking-tight">Professional Experience</h3>
            </div>
            <div class="max-w-2xl mx-auto">
                {experience_html}
            </div>
        </div>
    </section>

    <!-- Featured Projects Grid -->
    <section id="projects" class="py-20 px-6 border-t border-slate-800 bg-slate-900/30">
        <div class="max-w-5xl mx-auto">
            <div class="text-center mb-16">
                <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">Proven Track Record</h2>
                <h3 class="text-3xl font-bold tracking-tight">Featured Engineering Projects</h3>
            </div>
            <div class="grid md:grid-cols-2 gap-6">
                <!-- Project 1 -->
                <div class="glass-card p-7 rounded-3xl border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-xs font-bold px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">Autonomous Agentic Systems</span>
                            <i data-lucide="layers" class="w-5 h-5 text-blue-400"></i>
                        </div>
                        <h4 class="text-xl font-bold text-white mb-2">Multi-Agent VentureOS Studio</h4>
                        <p class="text-sm text-slate-400 mb-4 leading-relaxed">
                            A production-grade multi-agent autonomous venture factory operating across 7 departments and 34 specialized roles using LangGraph, mem0, and Crawl4AI.
                        </p>
                        <div class="flex flex-wrap gap-2 mb-6 text-xs text-slate-400">
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">Python</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">LangGraph</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">FastAPI</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">Crawl4AI</span>
                        </div>
                    </div>
                </div>

                <!-- Project 2 -->
                <div class="glass-card p-7 rounded-3xl border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between">
                    <div>
                        <div class="flex justify-between items-center mb-4">
                            <span class="text-xs font-bold px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">E-Commerce Intelligence</span>
                            <i data-lucide="activity" class="w-5 h-5 text-indigo-400"></i>
                        </div>
                        <h4 class="text-xl font-bold text-white mb-2">BuyBox Sentinel Radar</h4>
                        <p class="text-sm text-slate-400 mb-4 leading-relaxed">
                            Continuous 24/7 price undercutting and unauthorized Buy Box hijacker detection engine for Amazon & Meesho sellers with automated Telegram push alerts.
                        </p>
                        <div class="flex flex-wrap gap-2 mb-6 text-xs text-slate-400">
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">FastAPI</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">Pydantic</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">Telegram Bot</span>
                            <span class="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800">SQLite</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Education Section -->
    <section id="education" class="py-20 px-6 border-t border-slate-800">
        <div class="max-w-4xl mx-auto">
            <div class="text-center mb-16">
                <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">Academic Background</h2>
                <h3 class="text-3xl font-bold tracking-tight">Education & Degrees</h3>
            </div>
            <div class="grid sm:grid-cols-2 gap-4 max-w-2xl mx-auto">
                {education_html}
            </div>
        </div>
    </section>

    <!-- Skills & Tech Stack -->
    <section id="skills" class="py-20 px-6 border-t border-slate-800 bg-slate-900/40">
        <div class="max-w-4xl mx-auto">
            <div class="text-center mb-16">
                <h2 class="text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">Core Competencies</h2>
                <h3 class="text-3xl font-bold tracking-tight">Skills & Technologies</h3>
            </div>
            <div class="flex flex-wrap justify-center gap-3 max-w-3xl mx-auto mb-16">
                {skills_chips}
            </div>
            <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div class="glass-card p-5 rounded-2xl text-center">
                    <i data-lucide="code-2" class="w-6 h-6 text-blue-400 mx-auto mb-2"></i>
                    <div class="font-bold text-sm">Python / FastAPI</div>
                    <div class="text-xs text-slate-500 mt-1">Backend & APIs</div>
                </div>
                <div class="glass-card p-5 rounded-2xl text-center">
                    <i data-lucide="layout" class="w-6 h-6 text-indigo-400 mx-auto mb-2"></i>
                    <div class="font-bold text-sm">React / Tailwind</div>
                    <div class="text-xs text-slate-500 mt-1">Frontend & UI</div>
                </div>
                <div class="glass-card p-5 rounded-2xl text-center">
                    <i data-lucide="cpu" class="w-6 h-6 text-purple-400 mx-auto mb-2"></i>
                    <div class="font-bold text-sm">LangGraph & AI</div>
                    <div class="text-xs text-slate-500 mt-1">Agentic Pipelines</div>
                </div>
                <div class="glass-card p-5 rounded-2xl text-center">
                    <i data-lucide="database" class="w-6 h-6 text-emerald-400 mx-auto mb-2"></i>
                    <div class="font-bold text-sm">PostgreSQL / Redis</div>
                    <div class="text-xs text-slate-500 mt-1">Databases & Caching</div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer & Contact -->
    <footer id="contact" class="py-16 px-6 border-t border-slate-800 text-center">
        <div class="max-w-xl mx-auto space-y-6">
            <h3 class="text-2xl font-bold text-white">Let's Build Something Great Together</h3>
            <p class="text-sm text-slate-400">Available for innovative software development, consulting, and autonomous agent engineering.</p>
            <div class="flex justify-center gap-4">
                <a href="{linkedin_url}" target="_blank" class="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs transition shadow-lg shadow-blue-600/30 flex items-center gap-2">
                    <i data-lucide="linkedin" class="w-4 h-4"></i> Message on LinkedIn
                </a>
            </div>
            <p class="text-xs text-slate-600 pt-8">© 2026 {name}. Designed with VentureOS Autonomous Studio.</p>
        </div>
    </footer>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""

    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path

if __name__ == "__main__":
    profile_file = "build/profile/extracted_linkedin.json"
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "name": "Muhammad Hudaifah Mubarak",
            "headline": "Full-Stack Software Engineer & AI Systems Architect",
            "url": "https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279"
        }
    path = build_portfolio(data)
    print("Portfolio generated at:", path)
