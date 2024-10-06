from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from renew_book import Renew



def lambda_handler(event=None, context=None):
	Renew().run()
