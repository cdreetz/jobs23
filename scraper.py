import json
from Bot import Bot
from selenium.webdriver.common.by import By
from time import sleep
import itertools
import urllib
from selenium.common.exceptions import NoSuchElementException
import os
from random import shuffle
import csv


class StackScraper(Bot):
    def __init__(self):
        super().__init__(verbose=True)

        role_names = [
            "data scientist",
            "data analyst",
            "data engineer",
            "machine learning engineer"
        ]
        companies = [
            "apple",
            "google",
            "microsoft",
            "meta",
            "tesla",
            "amazon",
            "heb",
            "usaa",
            "frost",
            #"UT Health Science Center at San Antonio",
            #"HEB"
        ]
        shuffle(role_names)
        self.driver.get("https://www.google.com")
        for role_name, company in itertools.product(role_names, companies):
            self.get_all_jobs(role_name, company)

    def get_all_jobs(self, role_name, company):
        query = f"https://www.google.com/search?q={role_name} {company}&ibp=htl;jobs#htivrt=jobs".replace(
            ' ', '+')
        print(query)
        self.driver.get(query)
        listings = self.driver.find_elements(
            By.XPATH, "//div[@class='PwjeAc']")
        print(f"Number of listings found: {len(listings)}")
        sleep(1)
        for idx, listing in enumerate(listings):
            self.scroll_into_view(listing)

            try:
                listing.click()
                sleep(0.5)
                job = self._get_job()
                self.save_job(job, role_name, company)

            except (NoSuchElementException, selenium.common.exceptions.ElementClickInterceptedException) as e:
                print(f"Error while processing listing {idx}: {e}")
                continue


    def scroll_into_view(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        except Exception as e:
            print(f"Error while scrolling to element: {e}")
                
        
    def _get_job(self):
        print("Getting job details")
        return {
            "id": self._get_job_id(),
            "company": self._get_company(),
            "description": self._get_job_description()
        }
    
    def _get_job_id(self):
        parsed_url = urllib.parse.urlparse(self.driver.current_url)
        id = urllib.parse.parse_qs(parsed_url.fragment)['htidocid'][0]
        return id
    
    def _get_company(self):
        job_container = self.driver.find_element(
            By.XPATH, '//div[@class="whazf bD1FPe"]') 
        company = job_container.find_element(
            By.XPATH, './/div[@class="nJlQNd sMzDkb"]'
            ).text
        return company
    
    def _get_job_description(self):
        job_container = self.driver.find_element(
            By.XPATH, '//div[@class="whazf bD1FPe"]')
        try:
            expand_description_button = job_container.find_element(
                By.XPATH, 'div/div/div/div/div/div/div[@class="CdXzFe j4kHIf"]')
            self.scroll_into_view(expand_description_button)
            expand_description_button.click()
        except NoSuchElementException:
            pass
        description = job_container.find_element(
            By.XPATH, ".//span[@class='HBvzbc']").text
        # By.XPATH "div/div/div/div/div/span[@class=']".text
        return description
    
    def save_job(self, job, role_name, company_name):
        csv_file_path = 'jobs.csv'
        fieldnames = ['job_id', 'role_name', 'company_name', 'description']

        try:
            if os.path.exists(csv_file_path):
                with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    if any(row['job_id'] == job["id"] for row in reader):
                        if self.verbose:
                            print(f"Job ID: {job['id']} already exists")
                        return

            if self.verbose:
                print(f"Saving job: {job['id']} - {role_name} at {company_name}")

            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow({'job_id': job["id"], 'role_name': role_name, 'company_name': company_name, 'description': job["description"]})

        except Exception as e:
            if self.verbose:
                print(f"Error occured while saving job {job['id']} to csv. Error: {e}")




if __name__ == '__main__':
    StackScraper()

