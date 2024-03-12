# Scrapy settings for group_scrape project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "scrapy_resit"

SPIDER_MODULES = ["scrapy_resit.spiders"]
NEWSPIDER_MODULE = "scrapy_resit.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "group_scrape (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1000.0
# Enable showing throttling stats for every response received:
AUTOTHROTTLE_DEBUG = False

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Add Scrapy-Selenium middleware
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 543,
    'group_scrape.middlewares.CustomProxyMiddleware': 1
}

# Set the Selenium driver options
SELENIUM_DRIVER_ARGUMENTS = [] 
SELENIUM_DRIVER_NAME = 'chrome'  # or 'firefox
SELENIUM_DRIVER_EXECUTABLE_PATH = None # or '/path/to/geckodriver'

#ITEM_PIPELINES = {
    #'your_project_name.pipelines.PostgresPipeline': 300,
#}