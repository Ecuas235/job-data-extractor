from fastapi import FastAPI, HTTPException
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd
import os
from fastapi.responses import StreamingResponse
import json

app = FastAPI()


class Crawler:
    def __init__(self, config):
        self.browser = None
        self.page = None

        self.query = config["query"]
        self.pages = config["pages"]
        self.location = config["location"]

        self.today = datetime.today().date()

    async def _load_page(self):
        await self.page.goto("https://in.indeed.com/")
        await self.page.wait_for_selector("input#text-input-what")
        await self.page.fill("input#text-input-what", self.query)
        await self.page.fill("input#text-input-where", self.location)
        await self.page.click("button.yosegi-InlineWhatWhere-primaryButton")

        await self.page.click("span#dateLabel")
        await self.page.wait_for_timeout(2000)

    async def scrape_indeed_stream(self):
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
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
                        await job_title_element.inner_text()
                        if job_title_element
                        else "N/A"
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
                        await location_element.inner_text()
                        if location_element
                        else "N/A"
                    )

                    job_description_element = await self.page.query_selector(
                        "div.jobsearch-JobComponent-description"
                    )
                    job_description = (
                        await job_description_element.inner_text()
                        if job_description_element
                        else None
                    )

                    scraped_job = {
                        "Title": job_title,
                        "Company": company_name,
                        "Location": location,
                        "Description": job_description,
                    }

                    job_data.append(scraped_job)

                    yield f"{scraped_job}"

                if self.pages > 1:
                    next_button = await self.page.query_selector(
                        'a[data-testid="pagination-page-next"]'
                    )
                    if next_button:
                        await next_button.click()
                        await self.page.wait_for_timeout(5000)
                    else:
                        break

            # Logging
            df = pd.DataFrame(job_data)
            os.makedirs("./data", exist_ok=True)
            file_path = f"./data/Jobs_indeed_{self.today}.csv"
            df.to_csv(file_path)

            await self.browser.close()


@app.get("/stream-indeed")
async def stream_indeed():
    config_path = "./config/config.json"
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = json.load(file)
        print("Config loaded:", config)
    else:
        print(f"Config file {config_path} does not exist.")
    crawler = Crawler(config)

    return StreamingResponse(
        crawler.scrape_indeed_stream(), media_type="text/event-stream"
    )
