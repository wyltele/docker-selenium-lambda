from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from Books2 import Renew



def lambda_handler(event, context):
	Renew().run()
