import json
from Bot import Bot
from selenium.webdriver.common.by import By
from time import sleep
import itertools
import urllib
from selenium.common.exceptions import NoSuchElementException
import os
from random import shuffle
from app2 import db, Job


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
        try:
            # Check if job already exists in the database
            existing_job = Job.query.filter_by(job_id=job["id"]).first()

            if existing_job:
                if self.verbose:
                    print(f"Job ID: {job['id']} already exists. Skipping...")
                return  # if job already exists, just return and continue on

            if self.verbose:
                print(f"Saving job: {job['id']} - {role_name} at {company_name}")

            new_job = Job(
                job_id=job["id"],
                role_name=role_name,
                company_name=company_name,
                description=job["description"]
            )
            db.session.add(new_job)
            db.session.commit()

        except IntegrityError:  
            db.session.rollback()  # Rollback the session to a clean state
            if self.verbose:
                print(f"Integrity error occurred while saving job {job['id']}. Job might already exist or another constraint was violated.")

        except Exception as e:  # Catching generic exception for any other unexpected errors
            if self.verbose:
                print(f"Error occurred while saving job {job['id']}. Error: {e}")




if __name__ == '__main__':
    from app2 import app
    with app.app_context():
        StackScraper()

