from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime,timedelta
from tempfile import mkdtemp
import requests
import time
import os
import sys

class Renew:
	def __init__(self):
		self.driver=None
		self.result=''
		self.env=os.environ
		
	def run(self):
		options = webdriver.ChromeOptions()
		service = webdriver.ChromeService("/opt/chromedriver")

		options.binary_location = '/opt/chrome/chrome'
		options.add_argument("--headless=new")
		options.add_argument('--no-sandbox')
		options.add_argument("--disable-gpu")
		options.add_argument("--window-size=1280x1696")
		options.add_argument("--single-process")
		options.add_argument("--disable-dev-shm-usage")
		options.add_argument("--disable-dev-tools")
		options.add_argument("--no-zygote")
		options.add_argument(f"--user-data-dir={mkdtemp()}")
		options.add_argument(f"--data-path={mkdtemp()}")
		options.add_argument(f"--disk-cache-dir={mkdtemp()}")
		options.add_argument("--remote-debugging-port=9222")

		self.driver = webdriver.Chrome(options=options, service=service)
		
		
		env_vars = ['CREDENTIALS','URL','MAILKEY','SANDBOX','FROMEMAIL','TOEMAIL']
		if not all(x in self.env for x in env_vars):
			print('missing environment variables, exit....')
			sys.exit()
			
		credentials=os.environ['CREDENTIALS'].split(',')
		for credential in credentials:
			time.sleep(1)
			user=credential.split()[0]
			passwd=credential.split()[1]
			results=self.run_user(user,passwd)
			if results[0]:
				self.result=self.result+'user '+user+' has items renewed, the list is:\n\n'
				for item in results[1]:
					self.result=self.result+item+'\n'
					self.result=self.result+'*******************\n'
				self.result=self.result+'\n'
			else:
				self.result=self.result+'user '+user+' has no item renewed\n\n'
			if len(results[2])>0:				
				self.result=self.result+'WARNING: there is(are) weekday renewable items:\n\n'
				for item in results[2]:
					self.result=self.result+item+'\n'
					self.result=self.result+'*******************\n'
				self.result=self.result+'\n'
			if len(results[3])>0:
				self.result=self.result+'WARNING: those items cannot be renewed when due:\n\n'
				for item in results[3]:
					self.result=self.result+item+'\n'			
					self.result=self.result+'*******************\n'
				self.result=self.result+'\n'
			self.result=self.result+'\n\n'
		
		self.sendemail()
		
	def run_user(self,user,passwd):
		print('start working on '+user+':\n')		
		renewed=False
		weekday_renew_list=[]
		renewed_list=[]
		norenew_list=[]
		self.driver.get(self.env['URL'])
		print(self.env['URL'])
		el=self.wait_and_get("//input[@name='code']")
		el.clear()
		el.send_keys(user)
		el=self.driver.find_element(By.XPATH, "//input[@name='pin']")
		el.clear()
		el.send_keys(passwd)
		el.send_keys(u'\ue007')
		self.wait_and_get("//img[@alt='Your Wish Lists']")
		rows=self.driver.find_elements(By.CLASS_NAME, 'patFuncEntry')
		for row in rows:
			status=row.find_element(By.CLASS_NAME, 'patFuncStatus').text
			fields=status.split()
			if(len(fields)>3):
				if fields[3] == '3':
					norenew_list.append(row.text)					
			tdate=datetime.strptime(fields[1],'%y-%m-%d')
			if tdate.weekday()!= 5 and tdate.weekday()!=6:
				weekday_renew_list.append(row.text)
			if tdate<datetime.today():
				renewed=True
				row.find_element(By.XPATH, ".//input[@type='checkbox']").click()	
				
		if renewed==True:
			self.wait_and_get("//img[@alt='RENEW SELECTED ITEMS']").click()
			self.wait_and_get("//input[@value='YES']").click()
			self.wait_and_get("//img[@alt='RENEW SELECTED ITEMS']")

		rows=self.driver.find_elements(By.CLASS_NAME, 'patFuncEntry')
		for row in rows:
			status=row.find_element(By.CLASS_NAME, 'patFuncStatus').text
			fields=status.split()
			tdate=datetime.strptime(fields[1],'%y-%m-%d')
			if tdate<datetime.today():
				renewed_list.append(row.text)
		self.wait_and_get("//img[@alt='Log Out']").click()
		self.wait_and_get("//img[@alt='Advanced Search']")
		return [renewed, renewed_list,weekday_renew_list,norenew_list]
		
	def sendemail(self):
		request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(self.env['SANDBOX'])
		request = requests.post(request_url, auth=('api', self.env['MAILKEY']), data={
			'from': self.env['FROMEMAIL'],
			'to': self.env['TOEMAIL'],
			'subject': 'Renew Notification',
			'text': self.result
		})
		
	def wait_and_get(self,xpath):
		element=None
		while True:
			try:
				element = WebDriverWait(self.driver, 10).until(
					EC.presence_of_element_located((By.XPATH, xpath))
				)
				break
			except:
				self.driver.refresh()
		return element
