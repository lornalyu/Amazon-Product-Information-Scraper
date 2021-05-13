import time
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, WebDriverException

"""
    Step1: Open the brower
    Step2: Search for the product 
    Step3: Extract the html content of all the products
    Step4: Extract the product description, price, ratings, reviews count and URL
    Step5: Record the product information in a product record list
    Step6: Repeat for all the pages
    Step7: Close the browser
    Step8: Write all the product's information in the product record list in the spreadsheet
"""


class AmazonProductScraper:
    def __init__(self):
        self.driver = None

    def open_browser(self):
        url = "https://www.amazon.in/"
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # Website URL
        self.driver.get(url)
        print("Browser is open")
        print(requests.get(url))
        # Wait till the page has been loaded
        time.sleep(3)

    def get_product_url(self, search_product_name):
        # This is the product url format for all products
        product_url = "https://www.amazon.in/s?k={}&ref=nb_sb_noss"
        # Replace the spaces with + signs to create a valid searchable url
        search_product_name = search_product_name.replace(" ", "+")
        product_url = product_url.format(search_product_name)
        # Go to the product webpage
        self.driver.get(product_url)
        # To be used later while navigating to different pages
        return product_url

    def extract_webpage_information(self):
        # Parsing through the webpage
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # List of all the html information related to the product
        search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        return search_results

    def extract_product_information(self, search_results):
        temporary_record = []
        for i in range(len(search_results)):
            item = search_results[i]

            # Find the a tag of the item
            atag_item = item.h2.a

            # Name of the item
            description = atag_item.text.strip()

            # Get the url of the item
            product_url = "https://www.amazon.in/" + atag_item.get('href')

            # Get the price of the product
            try:
                product_price_location = item.find('span', 'a-price')
                product_price = product_price_location.find('span', 'a-offscreen').text
            except AttributeError:
                product_price = "N/A"

            # Get product reviews
            try:
                product_review = item.i.text.strip()
            except AttributeError:
                product_review = "N/A"

            # Get number of reviews
            try:
                review_number = item.find('span', {'class': 'a-size-base', 'dir': 'auto'}).text
            except AttributeError:
                review_number = "N/A"

            # Store the product information in a tuple
            product_information = (description,  product_price[1:], product_review, review_number, product_url)

            # Store the information in a temporary record
            temporary_record.append(product_information)
    
        return temporary_record

    def navigate_to_other_pages(self, search_product_name):
        # Contains the list of all the product's information
        records = []

        print("Page 1 - webpage information extracted")

        for i in range(2, 20):
            # Goes to next page
            next_page_url = self.get_product_url(search_product_name) + "&page=" + str(i)
            self.driver.get(next_page_url)

            # Webpage information is stored in search_results
            search_results = self.extract_webpage_information()
            temporary_record = self.extract_product_information(search_results)

            extraction_information = "Page {} - webpage information extracted"
            print(extraction_information.format(i))

            for i in temporary_record:
                records.append(i)

        self.driver.close()

        return records

    def product_information_spreadsheet(self, records):

        for _ in records:
            file_name = "product_info.csv"
            with open(file_name, "w", newline='', encoding='utf-8') as f:

                try:
                    writer = csv.writer(f)
                    # Column names
                    writer.writerow(['Description', 'Price', 'Rating', 'Review Count', 'Product URL'])
                    writer.writerows(records)
                except UnicodeEncodeError:
                    continue

            f.close()


search_product_name = input("Enter the product to be searched: ")
my_amazon_bot = AmazonProductScraper()

my_amazon_bot.open_browser()

start_time = datetime.now()

my_amazon_bot.get_product_url(search_product_name)

my_amazon_bot.extract_product_information(my_amazon_bot.extract_webpage_information())

my_amazon_bot.product_information_spreadsheet(my_amazon_bot.navigate_to_other_pages(search_product_name))

end_time = datetime.now()

print("Total time taken: " + str((end_time - start_time).total_seconds()) + " seconds")
