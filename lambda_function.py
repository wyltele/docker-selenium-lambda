from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from Books2 import Renew



def lambda_handler(event, context):
    # TODO implement	

	Renew().run()
    # page_data = ""
    # if 'url' in event.keys():
        # driver.get(event['url'])
        # page_data = driver.page_source
        # print(page_data)
    # driver.close()
    # return page_data
