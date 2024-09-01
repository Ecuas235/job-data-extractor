import requests
import time
import os
import json

import pandas as pd

from bs4 import BeautifulSoup
from tqdm import tqdm

from warnings import filterwarnings
from playwright.sync_api import sync_playwright
from datetime import datetime
filterwarnings('ignore')

class Crawler:
    def __init__(self, config):
        self.browser = None
        self.page = None
        
        self.query = config['query']
        self.pages = config['pages']
        self.location = config['location']
        
        self.today = datetime.today().date()
        
    def setup(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            self.page = browser.new_page()
            self.scrape_indeed()
            self.scrape_foundit()
            input("Press Enter to close the browser...")
    

            
    def scrape_indeed(self):
        self.page.goto('https://in.indeed.com/')
        self.page.wait_for_selector('input#text-input-what')
        self.page.fill('input#text-input-what', self.query)
        self.page.fill('input#text-input-where', self.location)
        self.page.click('button.yosegi-InlineWhatWhere-primaryButton')
        
        self.page.click('span#dateLabel')
        self.page.wait_for_timeout(2000) 
        
        job_data = []
        for _ in range(self.pages): 
            #self.page.wait_for_selector('.jobTitle.css-198pbd.eu4oa1w0', timeout=120000)
            job_elements = self.page.query_selector_all('.jobTitle.css-198pbd.eu4oa1w0')
            for job in tqdm(job_elements):
                job.click(timeout=120000)
                self.page.wait_for_timeout(5000)

                job_title = self.page.query_selector('h2.jobsearch-JobInfoHeader-title')
                if job_title:
                    job_title  = job_title.inner_text().strip()
                company_name = self.page.query_selector('div[data-company-name="true"]').inner_text().strip()
                #company_rating = self.page.query_selector('span.css-ppxtlp.e1wnkr790').inner_text().strip()
                location = self.page.query_selector('div[data-testid="inlineHeader-companyLocation"]').inner_text().strip()
                job_description = self.page.query_selector('div.jobsearch-JobComponent-description').inner_text().strip()
                
                job_data.append({
                    'Title': job_title,
                    'Company': company_name,
                    #'Rating': company_rating,
                    'Location': location,
                    'Description': job_description,
                })
            
            # Create a DataFrame
            next_button = self.page.query_selector('a[data-testid="pagination-page-next"]')
            if next_button:
                next_button.click()
                self.page.wait_for_timeout(5000)  # Wait for the next page to load
            else:
                break
        df = pd.DataFrame(job_data)
        os.makedirs('./data', exist_ok=True)
        df.to_csv(f'./data/Jobs_indeed_{self.today}.csv')
        
    def scrape_foundit(self):
        self.page.goto(url='https://www.foundit.in/')
        self.page.fill('input#heroSectionDesktop-skillsAutoComplete--input', self.query)
        self.page.fill('input#heroSectionDesktop-locationAutoComplete--input', self.location)
        self.page.click('#heroSectionDesktop-expAutoComplete')
        self.page.wait_for_selector('.dropDown_options')
        fresher_option = self.page.query_selector('li:has-text("Fresher")')
        fresher_option.click()
        
        self.page.click('.search_submit_btn')
        
        job_data = []
        for _ in range(self.pages):
            #time.sleep(5000)
            self.page.wait_for_selector('.srpResultCardContainer')
            job_containers = self.page.query_selector_all('.cardContainer')
            for job in tqdm(job_containers):
                
                job.click(timeout=120000)
                self.page.wait_for_timeout(2000)
                
                self.page.wait_for_selector('#srpJdContainerTop')
                job_title = self.page.query_selector('.jdTitle span')
                if job_title:
                    job_title = job_title.inner_text().strip()
                
                company_name = self.page.query_selector('.jdCompanyName p')
                if company_name:
                    company_name = company_name.inner_text().strip()
                    
                location = self.page.query_selector('.jobHighlights .bodyRow .details')
                if location:
                    location = location.inner_text().strip()
                job_description = self.page.query_selector('.jobDescriptionContainer .jobDescription')
                if job_description:
                    job_description = job_description.inner_text().strip()
                
                
                job_data.append({
                        'Title': job_title,
                        'Company': company_name,
                        #'Rating': company_rating,
                        'Location': location,
                        'Description': job_description,
                    })
            self.page.wait_for_selector('.pagination')
            if not self.page.query_selector('.arrow.arrow-right.disabled'):
                self.page.click('.arrow.arrow-right')
                self.page.wait_for_timeout(5000)

        df = pd.DataFrame(job_data)
        os.makedirs('./data', exist_ok=True)
        df.to_csv(f'./data/Jobs_foundit_{self.today}.csv')
            
if __name__ == '__main__':
    config_path = './config/config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
        print("Config loaded:", config)
    else:
        print(f"Config file {config_path} does not exist.")
    crawler = Crawler(config)
    crawler.setup()