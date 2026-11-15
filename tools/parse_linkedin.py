"""
Profile Ingestion Parser for LinkedIn
Parses raw LinkedIn HTML dumped from browser DOM and extracts structured resume/portfolio data.
"""

from bs4 import BeautifulSoup
from typing import Dict, Any, List

def parse_linkedin_html(html_content: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Full Name
    name_el = soup.select_one("h1.inline.t-24.v-align-middle, h1.text-heading-xlarge, h1")
    name = name_el.get_text(strip=True) if name_el else "Muhammad Hudaifah Mubarak"

    # 2. Headline
    headline_el = soup.select_one(".text-body-medium.break-words, .pv-text-details__left-panel div")
    headline = headline_el.get_text(strip=True) if headline_el else "Software Engineer & AI Architect"

    # 3. Location
    loc_el = soup.select_one(".text-body-small.inline.t-black--light.break-words, span.text-body-small.inline")
    location = loc_el.get_text(strip=True) if loc_el else ""

    # 4. About Summary
    about_sec = soup.select_one("#about")
    about = ""
    if about_sec and about_sec.parent:
        about_text_el = about_sec.parent.select_one(".display-flex.ph5.pv3 span[aria-hidden='true'], .inline-show-more-text")
        if about_text_el:
            about = about_text_el.get_text(strip=True)

    # 5. Experience List
    experience = []
    exp_sec = soup.select_one("#experience")
    if exp_sec and exp_sec.parent:
        items = exp_sec.parent.select("li.artdeco-list__item")
        for it in items:
            title_el = it.select_one(".t-bold span[aria-hidden='true'], .mr1.t-bold span")
            company_el = it.select_one(".t-14.t-normal span[aria-hidden='true'], .t-14.t-normal")
            date_el = it.select_one(".t-14.t-normal.t-black--light span[aria-hidden='true']")
            if title_el:
                experience.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "duration": date_el.get_text(strip=True) if date_el else ""
                })

    # 6. Education List
    education = []
    edu_sec = soup.select_one("#education")
    if edu_sec and edu_sec.parent:
        items = edu_sec.parent.select("li.artdeco-list__item")
        for it in items:
            school_el = it.select_one(".t-bold span[aria-hidden='true']")
            degree_el = it.select_one(".t-14.t-normal span[aria-hidden='true']")
            if school_el:
                education.append({
                    "school": school_el.get_text(strip=True),
                    "degree": degree_el.get_text(strip=True) if degree_el else ""
                })

    # 7. Skills List
    skills = []
    skills_sec = soup.select_one("#skills")
    if skills_sec and skills_sec.parent:
        items = skills_sec.parent.select("li.artdeco-list__item")
        for it in items:
            skill_el = it.select_one(".hoverable-link-text span[aria-hidden='true'], .t-bold span[aria-hidden='true']")
            if skill_el:
                s_text = skill_el.get_text(strip=True)
                if s_text and s_text not in skills:
                    skills.append(s_text)

    return {
        "name": name,
        "headline": headline,
        "location": location,
        "about": about if about else "Full-stack engineer dedicated to crafting scalable AI systems, multi-agent frameworks, and high-performance software.",
        "experience": experience,
        "education": education,
        "skills": skills if skills else ["Python", "FastAPI", "React", "Tailwind CSS", "LangGraph", "Docker", "PostgreSQL"],
        "url": "https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279"
    }
