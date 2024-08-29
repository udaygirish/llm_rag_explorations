import os
import sys
import time
import requests
from typing import list, dict
import yaml
import sys 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from utilities.logger import logger

# Selenium and Beautiful Soup Details
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


# ToDo:
# Have to improve this class a lot
# to handle more websites


# Scraping Class
class Scraper:
    def __init__(self, classes: list = []) -> None:
        self.classes_list = classes
        self.config = yaml.safe_load(open("config/scraping_config.yaml"))
        if self.classes_list == []:
            self.classes_list = self.config["websites"][2]
        self.description = "Scraping Class for Different Websites"
        # Ideal Class List  should be [Title, info, List of Classes]
        self.bs4_classes = [
            "brief-title",
            "info-provided-title",
            "Brief Summary",
            "Detailed Description",
            "Official Title",
            "study-overview-item-title",
        ]

        self.default_scraper = "selenium"  # Change this if BS4 is required
        self.selenium_wait_time = 5  # Seconds for loading the Webpage in headless
        # Above 5 seconds is ideal for most of the websites depends on Internet speed and many factors

    def scraper(self, url: str) -> str:
        if self.default_scraper == "selenium":
            return self.selenium_scraper(url)
        else:
            return self.bs4_scraper(url)

    def bs4_scraper(self, url: str) -> str:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            total_data = ""

            title_tag = soup.find("h2", class_=self.bs4_classes[0])
            if title_tag:
                title = title_tag.get_text(strip=True)
                total_data += "Title: " + title + "\n"
            else:
                logger.debug("Title not found")
                total_data += "Title: Not Found\n"

            info_tag = soup.find("div", class_=self.bs4_classes[1])
            if info_tag:
                info = info_tag.get_text(strip=True)
                total_data += "Info: " + info + "\n"
            else:
                logger.debug("Info not found")
                total_data += "Info: Not Found\n"

            for content_class in self.bs4_classes[2:]:
                content_tag = soup.find("div", class_=content_class)
                if content_tag:
                    content = content_tag.get_text(strip=True)
                    total_data += content + "\n"
                else:
                    logger.debug(f"{content_class} not found")
                    total_data += f"{content_class}: Not Found\n"

            return total_data
        else:
            logger.error("Error in fetching the URL")
            return "NO DATA FETCHED"

    def selenium_scraper(self, url: str) -> str:
        # Setup Selenium Options
        chrome_options = Options()
        # Preffered to Run in Headless mode for Scraping Applications
        # For Visual View to Debug you can comment the below line
        # HEADLESS - No GUI
        chrome_options.add_argument("--headless")

        # Setup the Web Driver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        # Navigate to the URL
        driver.get(url)

        # Wait for the Page to Load
        driver.implicitly_wait(self.selenium_wait_time)

        total_data = ""

        # ToDO:
        # Upgrade this code to avoid Multiple Try Except
        # But for Experimentation Purposes we are using them now

        try:
            try:
                title = driver.find_element(By.CLASS_NAME, self.classes_list[0]).text
                total_data += "Title: " + title + "\n"
            except Exception as e:
                logger.debug("Title not found")
                total_data += "Title: Not Found\n"
                pass

            try:
                info = driver.find_element(By.CLASS_NAME, self.classes_list[1]).text
                total_data += "Info: " + info + "\n"
            except Exception as e:
                logger.debug("Info not found")
                total_data += "Info: Not Found\n"
                pass

            try:
                study_overview = driver.find_elements(
                    By.CLASS_NAME, self.classes_list[2]
                )
            except Exception as e:
                study_overview = []
                logger.debug("Study Overview not found")
                pass

            try:
                text_overview = driver.find_elements(
                    By.CLASS_NAME, self.classes_list[3]
                )
            except Exception as e:
                text_overview = []
                logger.debug("Text Overview not found")
                pass

            range_traversal = min(len(study_overview), len(text_overview))

            for i in range(range_traversal):
                total_data += (
                    study_overview[i].text + ": " + text_overview[i].text + "\n"
                )

        except Exception as e:
            logger.error("Error in Scraping")
            total_data += "NO DATA FETCHED"

        # Close the Driver
        driver.quit()

        # Return the Extracted Content

        return total_data
