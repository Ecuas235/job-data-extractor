from fastapi import FastAPI, HTTPException
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd
import os
from fastapi.responses import StreamingResponse

app = FastAPI()


class Crawler:
    def __init__(self, query: str, pages: int, location: str, max_entries: int = -1):
        self.browser = None
        self.page = None

        self.query = query
        self.pages = pages
        self.location = location

        self.today = datetime.today().date()

    async def setup(self, stream: bool = False, indexer: int = 0):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            if stream:
                job_data = await self._scrape_indeed_stream(indexer)
            else:
                job_data = await self._scrape_indeed()  # Scraping process starts here
                await self.browser.close()

            return job_data

    async def _load_page(self):
        await self.page.goto("https://in.indeed.com/")
        await self.page.wait_for_selector("input#text-input-what")
        await self.page.fill("input#text-input-what", self.query)
        await self.page.fill("input#text-input-where", self.location)
        await self.page.click("button.yosegi-InlineWhatWhere-primaryButton")

        await self.page.click("span#dateLabel")
        await self.page.wait_for_timeout(2000)

    async def _scrape_indeed(self):
        await self._load_page()

        job_data = []

        for _ in range(self.pages):
            job_elements = await self.page.query_selector_all(
                ".jobTitle.css-198pbd.eu4oa1w0"
            )
            for job in job_elements:
                await job.click(timeout=120000)
                await self.page.wait_for_timeout(5000)

                job_title_element = await self.page.query_selector(
                    "h2.jobsearch-JobInfoHeader-title"
                )
                job_title = (
                    await job_title_element.inner_text() if job_title_element else "N/A"
                )

                company_name_element = await self.page.query_selector(
                    'div[data-company-name="true"]'
                )
                company_name = (
                    await company_name_element.inner_text()
                    if company_name_element
                    else "N/A"
                )

                location_element = await self.page.query_selector(
                    'div[data-testid="inlineHeader-companyLocation"]'
                )
                location = (
                    await location_element.inner_text() if location_element else "N/A"
                )

                job_description_element = await self.page.query_selector(
                    "div.jobsearch-JobComponent-description"
                )
                job_description = (
                    await job_description_element.inner_text()
                    if job_description_element
                    else None
                )

                job_data.append(
                    {
                        "Title": job_title,
                        "Company": company_name,
                        "Location": location,
                        "Description": job_description,
                    }
                )
                break

            if self.pages > 1:
                next_button = await self.page.query_selector(
                    'a[data-testid="pagination-page-next"]'
                )
                if next_button:
                    await next_button.click()
                    await self.page.wait_for_timeout(5000)
                else:
                    break

        df = pd.DataFrame(job_data)
        os.makedirs("./data", exist_ok=True)
        file_path = f"./data/Jobs_indeed_{self.today}.csv"
        df.to_csv(file_path)
        return job_data

    async def _scrape_indeed_stream(self, indexer: int = 0):
        await self._load_page()
        # for _ in range(self.pages):

        job_elements = await self.page.query_selector_all(
            ".jobTitle.css-198pbd.eu4oa1w0"
        )

        if not indexer < len(job_elements):
            return {
                "Title": "",
                "Company": "",
                "Location": "",
                "Description": "",
                "Stream": 0,
            }

        job = job_elements[indexer]

        await job.click(timeout=120000)
        await self.page.wait_for_timeout(5000)

        job_title_element = await self.page.query_selector(
            "h2.jobsearch-JobInfoHeader-title"
        )
        job_title = await job_title_element.inner_text() if job_title_element else "N/A"

        company_name_element = await self.page.query_selector(
            'div[data-company-name="true"]'
        )
        company_name = (
            await company_name_element.inner_text() if company_name_element else "N/A"
        )

        location_element = await self.page.query_selector(
            'div[data-testid="inlineHeader-companyLocation"]'
        )
        location = await location_element.inner_text() if location_element else "N/A"

        job_description_element = await self.page.query_selector(
            "div.jobsearch-JobComponent-description"
        )
        job_description = (
            await job_description_element.inner_text()
            if job_description_element
            else None
        )

        response = {
            "Title": job_title,
            "Company": company_name,
            "Location": location,
            "Description": job_description,
            "Stream": 1,
        }

        if response["Stream"] == 0:
            self.browser.close()

        return response


@app.get("/scrape_indeed")
async def scrape_indeed(
    query: str, pages: int = 1, location: str = "India", max_entries: int = -1
):
    try:
        crawler = Crawler(query, pages, location, max_entries)
        job_data = await crawler.setup()
        return job_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/scrape_indeed_stream")
async def scrape_indeed_stream(
    query: str,
    pages: int = 1,
    location: str = "India",
    max_entries: int = -1,
    index: int = 0,
):
    try:
        crawler = Crawler(query, pages, location, max_entries)
        job_data = await crawler.setup(stream=True, indexer=index)
        return job_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
