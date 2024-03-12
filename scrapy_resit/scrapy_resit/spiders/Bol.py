# ! BOL.COM SCRAPER


########################################################################################################################################################

# * Import all necessary modules and libraries

import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from scrapy.selector import Selector
from scrapy.exceptions import CloseSpider
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import logging
import time

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

# * Define the BolNLBotSpider class
class BolNLBotSpider(scrapy.Spider):
    name = 'bol-b'
    allowed_domains = ['bol.com']

    # Define the start_requests method for initiating the spider
    def start_requests(self):
        base_url = 'https://www.bol.com/nl/nl/l/muziekwinkel/64510/?page={}'
        total_pages = 3 # Set the total number of pages you want to scrape

        for page in range(1, total_pages + 1):
            url = base_url.format(page)
            yield scrapy.Request(url=url, callback=self.parse)

######################################################################################

    # * Define the __init__ method for initializing the spider with Selenium and logging
    def __init__(self, *args, **kwargs):
        chrome_options = Options()
        # Uncomment the line below if you want to run Chrome headlessly
        # chrome_options.add_argument("--headless")

        proxy_url = "127.0.0.1:24000"
        chrome_options.add_argument(f'--proxy-server={proxy_url}')
        chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"')
        chrome_options.add_argument('--ignore-ssl-errors=yes')
        chrome_options.add_argument('--ignore-certificate-errors')

        chrome_url = '/Users/sandervanduin/Desktop/HVA weekly /Online data mining 1/chromedriver-mac-arm64/chromedriver'
        chrome_service = Service(chrome_url)
        self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Enable JavaScript execution
        self.driver.execute_script("return navigator.webdriver = false")

        # Logging
        self.logger.info('-------Chrome driver initialized-------')
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.info('This is an -----INFO---- message')
        logging.debug('This is a -----DEBUG----- message')
        logging.error('This is an -----ERROR----- message')

######################################################################################

    # * Define the parse method for handling the initial response
    def parse(self, response):
        self.driver.get(response.url)

        try:
            # Find and click the "Alles accepteren" button for cookies
            cookies_button = self.driver.find_element(By.XPATH, '//button[@id="js-first-screen-accept-all-button" and @data-test="consent-modal-ofc-confirm-btn"]')
            cookies_button.click()
            time.sleep(3)

            # Get the top-left corner of the browser window
            top_left_corner = (0, 0)

            # Simulate a click on the top-left corner to close the modal
            action = ActionChains(self.driver)
            action.move_by_offset(*top_left_corner).click().perform()

        except NoSuchElementException:
            self.logger.info('Cookies button not found. Continuing without accepting.')
            raise CloseSpider('Cookies button not found')

        # Extract the page source and create a new Selector
        new_sel = Selector(text=self.driver.page_source)

        # Extract the links and follow them
        product_links = new_sel.css('a.product-title.px_list_page_product_click.list_page_product_tracking_target::attr(href)').getall()
        for href in product_links:
            url = response.urljoin(href)
            yield scrapy.Request(url, self.parse_product_page)

######################################################################################

    # * Define the parse_product_page method for parsing individual product pages
    def parse_product_page(self, response):
        logging.debug(f'------PROCESSING PRODUCT PAGE-----: %s {response.url}')

        # Extract product specifics
        product_title = response.css('.page-heading span::text').get()
        product_category = response.css('ul.specs__categories li.specs__category a::text').getall()
        product_brand = response.css('div.pdp-header__meta-item.links-inline a::text').get()
        product_description = ' '.join([desc.strip() for desc in response.css('div[data-test=\'product-description\'] ::text').getall()])
        product_ean = response.xpath('//dt[contains(text(), "EAN")]/following-sibling::dd/text()').get()
        product_price_whole = response.css('span.promo-price::text').get()
        product_price_fraction = response.css('sup.promo-price__fraction::text').get()
        product_price = f"{product_price_whole}.{product_price_fraction}" if product_price_whole and product_price_fraction else None
        product_review_score = response.css('div.reviews-summary__avg-score::text').get()
        product_review_amount = response.css('div.reviews-summary__total-reviews::text').get()

        # Yield the final details extracted from the product page
        yield {
            'product_title': product_title.strip() if product_title else None,
            'product_category': product_category if product_category else None,
            'product_brand': product_brand.strip() if product_brand else None,
            'product_description': product_description.strip() if product_description else None,
            'product_ean': product_ean.strip() if product_ean else None,
            'product_price': product_price.strip() if product_price else None,
            'product_review_score': product_review_score.strip() if product_review_score else None,
            'product_review_amount': product_review_amount.strip() if product_review_amount else None,
        }

######################################################################################

    # * Define the closed method for cleaning up resources when the spider is closed
    def closed(self, reason):
        if self.driver:
            self.driver.quit()