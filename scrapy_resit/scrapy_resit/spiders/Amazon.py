
# ! AMAZON UK SCRAPER


########################################################################################################################################################

# Import all necessary modules and libraries
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from scrapy.selector import Selector

########################################################################################################################################################

# ! Before you begin, update the path to chromedriver as noted on line 48.
# Open your terminal and change the directory with the command ‘cd group_scrape’.
# To start the spider, type 'scrapy crawl amazon-UK-bot -o output.csv'.

# For proxy functionality, download the proxy manager from the following link:
# [Luminati Proxy Manager](https://github.com/luminati-io/luminati-proxy?tab=readme-ov-file).
# After downloading, start the proxy by running the command: proxy-manager.
# Upon successful launch, you should see a message similar to:

# SYSTEM: WEBSRV: Proxy Manager is running
# |================================================|
# |                                                |
# |                                                |
# |              Open admin browser:               |
# |            http://127.0.0.1:22999              |
# |                ver. 1.421.780                  |
# |                                                |
# |   Do not close the process while using the     |
# |   Proxy Manager                                |
# |                                                |
# |                                                |
# |================================================|

# Remember to keep the proxy manager running while your spider is active.
# ! To stop the proxy manager, simply press 'ctrl + c'.

########################################################################################################################################################

# * Define the AmazonBotSpider class
class AmazonBotSpider(scrapy.Spider):
    # Spider configuration
    name = 'amazon-i'
    allowed_domains = ['amazon.co.uk']

    def start_requests(self):
        # Base URL for different categories
        #base_url = 'https://www.amazon.co.uk/s?i=mi&rh=n%3A{}&fs=true&page={}&qid={}&ref=sr_pg_{}'
        base_url = 'https://www.amazon.co.uk/s?i=mi&rh=n%3A{}&page={}&c=ts&qid={}&ts_id={}&ref=sr_pg_{}'
        
        categories = [
            ('406550031', '1705518929'),  # Guitars & Gear, IDs are hardcoded to match the category
            ('406552031', '1705523745'),  # Keyboards & Pianos, IDs are hardcoded to match the category
            ('406555031', '1705523873'),  # Live Sound & Recording, IDs are hardcoded to match the category
            ('407674031', '1705523968'),  # DJ & Party, IDs are hardcoded to match the category
            ('5496113031', '1705524039'), # Drums & Percussion, IDs are hardcoded to match the category
            ('406557031', '1705524099')   # Band & Orchestra, IDs are hardcoded to match the category
        ]
        pages_per_category = 1 
        #  >>> Set the total number of pages you want to scrape, 24 results per page <<<

        # Iterate through the pages as the base_url stays the same, increasing the number in the page={} by one each time
        for category, qid in categories:
            for page in range(1, pages_per_category + 1):
                url = base_url.format(category, page, qid, category, page)
                yield scrapy.Request(url=url, callback=self.parse)

######################################################################################

    # * Define certain parameters for the crawler such as headless Chrome driver, User agent and Proxy
    def __init__(self, *args, **kwargs):
        ## Implement Chrome driver ##
        # >>> Download the Chrome driver from here 'https://googlechromelabs.github.io/chrome-for-testing/'. Version 120 should be fine. <<<
        chrome_options = Options()
        proxy_url = "127.0.0.1:24000" 
        chrome_options.add_argument(f'--proxy-server={proxy_url}') # Connect to the proxy server
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"')
        chrome_options.add_argument('--ignore-ssl-errors=yes') # Ignore errors to enter product page
        chrome_options.add_argument('--ignore-certificate-errors') # Ignore certificates to enter product page

        chrome_service = Service('/Users/sandervanduin/Desktop/HVA weekly /Online data mining 1/chromedriver-mac-arm64/chromedriver') # >>> Update PATH to the correct Chrome driver <<<
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

######################################################################################

    # * Main parse method, this is the entry point of the spider
    def parse(self, response):
        # Scrape product links and follow each link
        self.driver.get(response.url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal"))
        )
        sel = Selector(text=self.driver.page_source)
        product_links = sel.css('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal::attr(href)').getall()
    # Create a for loop to iterate through all the product links
        for href in product_links:
            url = response.urljoin(href)
            yield response.follow(url, self.parse_product_page)

######################################################################################

    # * Method to parse individual product pages
    def parse_product_page(self, response):
        ## Product price ##
        # Scrape the price elements (symbol, whole, decimal) and merge it into one value
        price_elements = response.css('.reinventPricePriceToPayMargin span::text').getall()
        full_price = ''.join([elem.strip() for elem in price_elements])

        ## Product description ##
        # The product description is in a bullet point list, therefore we strip it so it becomes one string, useful for sentiment analysis
        product_description = ' '.join([desc.strip() for desc in response.css('div.a-spacing-medium.a-spacing-top-small ::text').getall()])
        
        ## Product ASIN ##
        # Check if ASIN element is present before trying to access its text content, if not present, leave blank
        product_details_ASIN_element = response.css('tr:contains("ASIN") td') # Scrape ASIN if it is part of a table on the product page
        product_details_ASIN = product_details_ASIN_element.css('::text').get().strip() if product_details_ASIN_element else ''

        ## Product listing date ##
        # Check if other elements are present before trying to access their text content, if not present, leave blank
        product_listing_date_element = response.css('tr:contains("Date First Available") td') # Scrape date if it is part of a table on the product page
        product_listing_date = product_listing_date_element.css('::text').get().strip() if product_listing_date_element else ''

        ## Product brand ##
        # Check if other elements are present before trying to access their text content, if not present, leave blank
        product_details_brand_element = response.css('a#bylineInfo ::text')
        product_details_brand = product_details_brand_element.get().strip() if product_details_brand_element else ''

        ## Product specifics ##
        # In some edge cases, the product ASIN and listing date are in a bullet point list instead of in a table on the product page
        # Therefore, we scrape the entire list that is under Product Specifics and parse the ASIN and product listing date later
        product_specifics = response.css('div#a-section div#detailBullets_feature_div ::text').getall()

        ## Product returns policy
        product_returns_policy_element = response.css('#returnsInfoFeature_feature_div span.offer-display-feature-text-message')
        product_returns_policy = product_returns_policy_element.get().strip() if product_returns_policy_element else ''

        ## Product reviews ##
        product_review_amount_element = response.css('#averageCustomerReviews span#acrCustomerReviewText')
        product_review_amount = product_review_amount_element.get().strip() if product_review_amount_element else ''
        product_review_rating_element = response.css('#averageCustomerReviews span.a-color-base')
        product_review_rating = product_review_rating_element.get().strip() if product_review_rating_element else ''

######################################################################################

        # * Final list of details to extract from the individual product page
        yield {
            'product_title': response.css('span.product-title-word-break ::text').get().strip(), # Scraped as full product title
            'product_full-price': full_price, # Scraped as "£1,675.00" with the pound symbol, comma to separate thousands and period to separate decimals (2 decimals only)
            'product_description-text': product_description, # Scraped as the full product description
            'product_specifics_list': product_specifics, # Product specifics like dimension, but includes ASIN and listing date as well, saved as one string
            'product_details_ASIN': product_details_ASIN, # Scraped as "B0768J69M4", always 10 decimals (if ASIN is not in table format, parse it from product_specifics
            'product_details_brand': product_details_brand, # Scraped as "Brand: [name]" or "Visit the [brand] store"
            'product_listing_date': product_listing_date, # Scraped as "7 Oct. 2017", might need parsing to be set as datatype 'datetime' for analytical purposes
            'review_amount': product_review_amount, # Scraped as "7,663 ratings", comma to separate thousands
            'review_rating': product_review_rating, # Scraped as "4.3", period to separate decimals, goes from 1.0 to 5.0
            'product_return_policy': product_returns_policy # Scraped as "Returnable within 30 days of receipt" if return policy is applicable
        }

######################################################################################

# * Define the closed method for cleaning up resources when the spider is closed
    def closed(self, reason):
        # Close the driver when the spider is closed
        if self.driver:
            self.driver.quit()
