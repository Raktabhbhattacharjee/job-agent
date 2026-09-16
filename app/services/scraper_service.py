import html
import re
import unicodedata
from typing import Any
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session

from app.services.groq_service import GroqService
from app.services.job_service import JobService


class ScraperService:
    BASE_URL = "https://remoteok.com/api"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }

    @classmethod
    def clean_html(cls, raw_html: str | None) -> str:
        """Convert scraped HTML into readable, normalized plain text."""
        if not raw_html:
            return ""
        clean_text = html.unescape(raw_html)
        clean_text = re.sub(r"<[^>]+>", " ", clean_text)
        clean_text = unicodedata.normalize("NFKC", clean_text)
        clean_text = re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]", "", clean_text)
        if any(marker in clean_text for marker in ("Ã", "Â", "â")):
            try:
                repaired_text = clean_text.encode("latin-1").decode("utf-8")
                if repaired_text:
                    clean_text = repaired_text
            except UnicodeError:
                pass
        return " ".join(clean_text.split())

    @classmethod
    def clean_text(cls, value: Any, fallback: str = "") -> str:
        """Normalize titles and metadata without assuming they contain HTML."""
        if value is None:
            return fallback
        cleaned = cls.clean_html(str(value)) or fallback
        if cleaned.isupper() and len(cleaned) > 3:
            cleaned = cleaned.title()
        return cleaned

    @classmethod
    def validate_api_response(cls, response: httpx.Response) -> list[dict[str, Any]]:
        """Reject throttling/block pages instead of silently saving no jobs."""
        if response.status_code != 200:
            raise RuntimeError(
                f"RemoteOK returned HTTP {response.status_code}; retry later or use method='playwright'."
            )
        try:
            raw_data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                "RemoteOK returned a non-JSON response, likely a block or rate-limit page."
            ) from exc
        if not isinstance(raw_data, list):
            raise RuntimeError("RemoteOK returned an unexpected response format.")
        return raw_data

    # ==========================================
    # METHOD 1: Fast HTTP API Scraper
    # ==========================================
    @classmethod
    def fetch_jobs_from_remoteok(cls, tag: str | None = None) -> list[dict[str, Any]]:
        """
        Hits RemoteOK's public JSON API to pull tech jobs.
        Ultra-fast (sub-second) and returns full job descriptions.
        """
        url = f"{cls.BASE_URL}?tag={tag.lower().strip()}" if tag else cls.BASE_URL

        with httpx.Client(headers=cls.HEADERS, timeout=15) as client:
            response = client.get(url)
            raw_data = cls.validate_api_response(response)

        # The first element in RemoteOK's array is legal metadata, so skip it
        jobs_raw = (
            raw_data[1:]
            if len(raw_data) > 1
            and isinstance(raw_data[0], dict)
            and "legal" in raw_data[0]
            else raw_data
        )

        parsed_jobs = []
        for item in jobs_raw:
            if not isinstance(item, dict):
                continue

            position = item.get("position")
            url = item.get("url") or item.get("apply_url")
            if not position or not url:
                continue

            # Format salary if present
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            salary_str = None
            if salary_min and salary_max:
                salary_str = f"${int(salary_min):,} - ${int(salary_max):,}"
            elif salary_min:
                salary_str = f"From ${int(salary_min):,}"

            # Guess job type from tags
            tags = [t.lower() for t in (item.get("tags") or [])]
            job_type = "Full-time"
            if "intern" in tags or "internship" in tags:
                job_type = "Internship"
            elif "contract" in tags or "freelance" in tags:
                job_type = "Contract"
            elif "part-time" in tags or "part time" in tags:
                job_type = "Part-time"

            parsed_jobs.append(
                {
                    "title": cls.clean_text(position),
                    "company": cls.clean_text(item.get("company"), "Unknown"),
                    "location": cls.clean_text(item.get("location"), "Remote"),
                    "job_type": job_type,
                    "salary": salary_str,
                    "description": cls.clean_html(item.get("description")),
                    "skills": item.get("tags") or [],
                    "url": cls.clean_text(url),
                    "source": "remoteok_api",
                    "posted_at": item.get("date"),
                }
            )

        return parsed_jobs

    # ==========================================
    # METHOD 2: Real Browser Playwright Scraper
    # ==========================================
    @classmethod
    def scrape_remoteok_with_playwright(
        cls,
        tag: str | None = None,
        max_jobs: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Launches a headless Chromium browser with Playwright, navigates to the official
        RemoteOK website, waits for JavaScript hydration, and extracts job cards from DOM.
        """
        from playwright.sync_api import sync_playwright

        url = (
            f"https://remoteok.com/remote-{tag.lower().strip()}-jobs"
            if tag
            else "https://remoteok.com"
        )
        parsed_jobs = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=cls.HEADERS["User-Agent"])
            page.goto(url, wait_until="domcontentloaded", timeout=25000)

            page_text = page.locator("body").inner_text(timeout=5000).lower()
            block_markers = (
                "access denied",
                "rate limit",
                "captcha",
                "too many requests",
            )
            if any(marker in page_text for marker in block_markers):
                raise RuntimeError(
                    "RemoteOK returned a block or rate-limit page; wait and retry with method='api'."
                )

            # Query all table rows representing jobs
            job_rows = page.query_selector_all("tr[data-id]")
            for row in job_rows[:max_jobs]:
                rel_url = row.get_attribute("data-url")
                company = row.get_attribute("data-company") or "Unknown"
                h2 = row.query_selector("h2")
                title = cls.clean_text(h2.inner_text()) if h2 else None

                if not title or not rel_url:
                    continue

                full_url = (
                    f"https://remoteok.com{rel_url}"
                    if rel_url.startswith("/")
                    else rel_url
                )

                # Extract skills / tags
                tags = [
                    cls.clean_text(t.inner_text())
                    for t in row.query_selector_all(".tag h3")
                    if cls.clean_text(t.inner_text())
                ]

                # Extract location and salary badges
                location = "Remote"
                salary_str = None
                for loc_el in row.query_selector_all(".location"):
                    text = cls.clean_text(loc_el.inner_text())
                    if "$" in text:
                        salary_str = text
                    elif text and not text.startswith("💰"):
                        location = text

                time_el = row.query_selector("time")
                posted_at = time_el.get_attribute("datetime") if time_el else None

                job_type = "Full-time"
                lower_tags = [t.lower() for t in tags]
                if "intern" in lower_tags or "internship" in lower_tags:
                    job_type = "Internship"
                elif "contract" in lower_tags or "freelance" in lower_tags:
                    job_type = "Contract"

                parsed_jobs.append(
                    {
                        "title": title,
                        "company": cls.clean_text(company, "Unknown"),
                        "location": cls.clean_text(location, "Remote"),
                        "job_type": job_type,
                        "salary": salary_str,
                        "description": f"Live posting on RemoteOK for {title} at {company}. Skills: {', '.join(tags)}",
                        "skills": tags,
                        "url": full_url,
                        "source": "remoteok_playwright",
                        "posted_at": posted_at,
                    }
                )

            browser.close()

        return parsed_jobs

    # ==========================================
    # METHOD 3: LinkedIn India Guest Scraper
    # ==========================================
    @classmethod
    def scrape_linkedin_india(
        cls,
        keywords: str = "python internship",
        location: str = "India",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Scrapes live internships in India from LinkedIn's public guest endpoint (no login required).
        Fetches job details, runs Groq to analyze role expectations and DSA requirement level.
        """
        import time
        from urllib.parse import quote

        headers = {
            "User-Agent": cls.HEADERS["User-Agent"],
            "Accept-Language": "en-US,en;q=0.9",
        }

        query_encoded = quote(keywords or "python internship")
        loc_encoded = quote(location or "India")

        jobs = []
        seen_urls = set()
        start = 0

        # Tech skill keywords to auto-detect
        TECH_SKILLS = [
            "python", "react", "javascript", "typescript", "fastapi", "django",
            "flask", "node.js", "express", "sql", "postgresql", "mongodb", "mysql",
            "docker", "aws", "git", "rest api", "graphql", "tailwind", "html", "css",
            "data structures", "algorithms", "machine learning", "pandas", "numpy"
        ]

        with httpx.Client(headers=headers, timeout=15) as client:
            while len(jobs) < limit and start < 50:
                url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query_encoded}&location={loc_encoded}&start={start}"
                try:
                    res = client.get(url)
                    if res.status_code != 200:
                        break
                    soup = BeautifulSoup(res.text, "html.parser")
                    cards = soup.find_all("li")
                    if not cards:
                        break

                    for li in cards:
                        if len(jobs) >= limit:
                            break

                        title_el = li.find("h3", class_="base-search-card__title")
                        company_el = li.find("h4", class_="base-search-card__subtitle")
                        loc_el = li.find("span", class_="job-search-card__location")
                        link_el = li.find("a", class_="base-card__full-link")

                        if not title_el or not link_el or not link_el.has_attr("href"):
                            continue

                        raw_url = link_el["href"].split("?")[0]
                        if raw_url in seen_urls:
                            continue
                        seen_urls.add(raw_url)

                        title = cls.clean_text(title_el.get_text(strip=True))
                        company = cls.clean_text(company_el.get_text(strip=True) if company_el else "Unknown")
                        job_location = cls.clean_text(loc_el.get_text(strip=True) if loc_el else location)

                        # Extract job id from url or data-entity-urn
                        job_id_match = re.search(r"-(\d{8,})", raw_url) or re.search(r"jobPosting:(\d+)", str(li))
                        job_id = job_id_match.group(1) if job_id_match else None

                        description = f"Internship opportunity for {title} at {company} ({job_location})."
                        if job_id:
                            try:
                                detail_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
                                detail_res = client.get(detail_url, timeout=8)
                                if detail_res.status_code == 200:
                                    detail_soup = BeautifulSoup(detail_res.text, "html.parser")
                                    desc_el = detail_soup.find("div", class_="show-more-less-html__markup")
                                    if desc_el:
                                        description = cls.clean_html(desc_el.get_text(separator=" ", strip=True))
                            except Exception:
                                pass

                        lower_desc = (title + " " + description).lower()
                        extracted_skills = [
                            skill.title() for skill in TECH_SKILLS if skill in lower_desc
                        ]
                        if not extracted_skills:
                            extracted_skills = ["Python", "Problem Solving"]

                        # Analyze DSA level and Company Expectations via Groq
                        analysis = GroqService.analyze_job_expectations_and_dsa(
                            title=title,
                            company=company,
                            description=description,
                        )

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": job_location,
                            "job_type": "Internship",
                            "salary": "Stipend Provided" if "stipend" in lower_desc else None,
                            "description": description,
                            "skills": extracted_skills,
                            "url": raw_url,
                            "source": "linkedin_india",
                            "dsa_level": analysis.get("dsa_level", "Moderate"),
                            "dsa_reason": analysis.get("dsa_reason"),
                            "expectations": analysis.get("expectations", []),
                            "company_intel": analysis.get("company_intel"),
                            "posted_at": "Recent",
                        })

                    start += 10
                    time.sleep(0.4)
                except Exception as err:
                    print(f"Error fetching LinkedIn India jobs: {err}")
                    break

        return jobs

    # ==========================================
    # METHOD 4: Internshala Scraper (Top Indian Internships)
    # ==========================================
    @classmethod
    def scrape_internshala(
        cls,
        keywords: str = "python",
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        """
        Scrapes live internships from Internshala for the given keyword.
        Pulls company name, title, stipend (in INR), location, and analyzes DSA expectations with Groq.
        """
        clean_kw = re.sub(r"[^a-zA-Z0-9]+", "-", (keywords or "python").lower().strip().replace("internship", "").strip())
        if not clean_kw or clean_kw == "-":
            clean_kw = "python"

        url = f"https://internshala.com/internships/{clean_kw}-internship/"
        headers = {
            "User-Agent": cls.HEADERS["User-Agent"],
            "Accept-Language": "en-US,en;q=0.9",
        }

        jobs = []
        TECH_SKILLS = [
            "python", "react", "javascript", "typescript", "fastapi", "django",
            "flask", "node.js", "express", "sql", "postgresql", "mongodb", "mysql",
            "docker", "aws", "git", "rest api", "graphql", "tailwind", "html", "css",
            "data structures", "algorithms", "machine learning", "pandas", "numpy"
        ]

        try:
            with httpx.Client(headers=headers, timeout=15) as client:
                res = client.get(url, follow_redirects=True)
                if res.status_code != 200:
                    return []

                soup = BeautifulSoup(res.text, "html.parser")
                cards = soup.find_all("div", class_="individual_internship")

                for c in cards[:limit]:
                    title_el = c.find("a", class_="job-title-href")
                    company_el = c.find("p", class_="company-name")
                    stipend_el = c.find("span", class_="stipend")
                    loc_el = c.find("a", class_="location_link")

                    if not title_el or not title_el.has_attr("href"):
                        continue

                    title = cls.clean_text(title_el.get_text(strip=True))
                    company = cls.clean_text(company_el.get_text(strip=True) if company_el else "Unknown")
                    href = title_el["href"]
                    full_url = f"https://internshala.com{href}" if href.startswith("/") else href

                    stipend = None
                    if stipend_el:
                        raw_stipend = stipend_el.get_text(strip=True)
                        stipend = raw_stipend.replace("\u20b9", "Rs. ")

                    loc_text = cls.clean_text(loc_el.get_text(strip=True) if loc_el else "Work from home / India")

                    description = f"Internship opportunity for {title} at {company}. Location: {loc_text}. Stipend: {stipend or 'Competitive'}."
                    lower_text = (title + " " + description).lower()
                    extracted_skills = [
                        s.title() for s in TECH_SKILLS if s in lower_text
                    ]
                    if not extracted_skills:
                        extracted_skills = [clean_kw.title(), "Problem Solving"]

                    analysis = GroqService.analyze_job_expectations_and_dsa(
                        title=title,
                        company=company,
                        description=description,
                    )

                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": loc_text,
                        "job_type": "Internship",
                        "salary": stipend,
                        "description": description,
                        "skills": extracted_skills,
                        "url": full_url,
                        "source": "internshala",
                        "dsa_level": analysis.get("dsa_level", "Low"),
                        "dsa_reason": analysis.get("dsa_reason"),
                        "expectations": analysis.get("expectations", []),
                        "company_intel": analysis.get("company_intel"),
                        "posted_at": "Recent",
                    })
        except Exception as e:
            print(f"Error scraping Internshala: {e}")

        return jobs

    # ==========================================
    # Unified Ingestion & Deduplication
    # ==========================================
    @classmethod
    def scrape_and_save(
        cls,
        db: Session,
        tag: str | None = None,
        source: str = "linkedin_india",
        method: str = "api",
        location: str = "India",
        max_jobs: int = 25,
    ) -> dict[str, Any]:
        """
        Unified method to scrape jobs from Indian portals (LinkedIn India + Internshala) or RemoteOK,
        enrich with DSA & expectations analysis, and save into PostgreSQL.
        """
        jobs = []
        clean_tag = tag.strip() if tag else ""

        if source in ["linkedin_india", "india_all"]:
            keywords = f"{clean_tag} internship" if clean_tag and "intern" not in clean_tag.lower() else (clean_tag or "python internship")
            li_limit = max(5, max_jobs // 2)
            ishala_limit = max(5, max_jobs - li_limit)

            li_jobs = cls.scrape_linkedin_india(keywords=keywords, location=location, limit=li_limit)
            ishala_jobs = cls.scrape_internshala(keywords=clean_tag or "python", limit=ishala_limit)
            jobs = li_jobs + ishala_jobs
            source_label = "india_portals"
            used_method = "live_scrape"
        elif source == "internshala":
            jobs = cls.scrape_internshala(keywords=clean_tag or "python", limit=max_jobs)
            source_label = "internshala"
            used_method = "web"
        elif method.lower() == "playwright":
            jobs = cls.scrape_remoteok_with_playwright(tag=clean_tag, max_jobs=max_jobs)
            source_label = "remoteok_playwright"
            used_method = "playwright"
        else:
            jobs = cls.fetch_jobs_from_remoteok(tag=clean_tag)
            source_label = "remoteok_api"
            used_method = "api"

        saved_count = JobService.bulk_save_jobs(db=db, jobs_list=jobs)
        return {
            "source": source_label,
            "method": used_method,
            "tag_searched": clean_tag or "all",
            "total_fetched": len(jobs),
            "total_saved": saved_count,
        }
