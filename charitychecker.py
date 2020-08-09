from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pdftables_api
import requests


# def request_handler(request):
# 	if request['method'] == 'POST':
		
# site_url = request['form']['site_url']



def get_name_property(soup):
	return soup.find('meta', property = 'og:site_name') or soup.find('meta', attrs = {'name': 'og:site'}) \
	or soup.find('meta', property = 'og:title') or soup.find('meta', attrs = {'name':'keywords'}) 

def get_ein(charity):
	api_url = 'https://projects.propublica.org/nonprofits/api/v2/search.json?q={}'.format(charity)
	req = requests.get(url = api_url)
	data = req.json()
	organizations = data['organizations']
	if organizations != []:
		ein =  organizations[0]['ein']
		api_url = 'https://projects.propublica.org/nonprofits/api/v2/organizations/{}.json'.format(ein)
		req = requests.get(url = api_url)
		data = req.json()
		return data
	return None

def get_ein_with_state(charity, place):
	api_url = 'https://projects.propublica.org/nonprofits/api/v2/search.json?q={}&state%5Bid%5D={}'.format(charity, place)
	req = requests.get(url = api_url)
	data = req.json()
	organizations = data['organizations']
	if organizations == []:
		possible_ein = get_ein(charity)
		if possible_ein:
			return possible_ein
		else:
			'This organization cannot be found.'
	else:
		return organizations[0]['ein']

def domain_search(site):
	domain = site
	if 'https://www.' in domain:
		domain = domain.replace('https://www.', '')
	lookup_header = {'Authorization': '4tHJgUBeWJqLjtiBLuOUMw:2U8ojUeN7K5eE7ZcUrJJtp'}
	req = requests.get(url = "https://company.bigpicture.io/v1/companies/find?domain={}".format(domain), headers=lookup_header)
	status = req.status_code
	if status == 200:
		return req.json()['geo']['stateCode'], req.json()['geo']['subPremise']
	return None

def get_rating(ein):
	header = {'Accept': 'application/json'}
	api_url = 'https://api.data.charitynavigator.org/v2/Organizations/{}?app_id=b66e5d67&app_key=995575c382aeed66712c6cb725f5db7c'.format(ein)
	req = requests.get(url = api_url, headers=header)
	status = req.status_code
	if status == 200:
		if 'currentRating' in req.json():
			return req.json()['currentRating']['rating']
	return None

def get_irs_rating(ein):
	irs_url = 'https://apps.irs.gov/app/eos/lettersSearch.do?ein1={}&dispatchMethod=searchDeterminationLetters'.format(ein)
	print(irs_url)
	# req  = requests.get(url = irs_url)
	driver = webdriver.Chrome(executable_path = '/Users/alexn/Downloads/chromedriver')
	driver.get(irs_url)
	html = driver.page_source
	html = WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR,"div.results-body-row")))
	print(html)
	print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAA')
	soup = BeautifulSoup(html, 'lxml')
	print(soup)
	if soup.find('ul', class_ =  'views-row'):
		return 'A'
	else:
		return 'B'
# <ul class="views-row"></ul>

def pdf_to_xml(pdf_link):
	c = pdftables_api.Client('my-api-key')
	c.xml(pdf_link, 'output') 

def get_charity_status(site):
	driver = webdriver.Chrome(executable_path = '/Users/alexn/Downloads/chromedriver')
	driver.get(site)
	html = driver.page_source
	driver.quit()
	# headers = {
 #    	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
	# }
	# req = requests.get(url=site, headers=headers)
	soupy = BeautifulSoup(html, 'lxml')
	tag = get_name_property(soupy)
	domain_lookup = domain_search(site)
	if domain_lookup:
		state, name = domain_lookup
	else:
		state = None

	if tag:
		title = tag.get('content', None)
	elif domain_lookup:
		title = name if name != 'None' else print('No name found.')
	else:
		print('No name found.')

	if state:
		ein_number = get_ein_with_state(title, state)
	else:
		ein_number = get_ein(title)

	print(ein_number)
	print(get_rating(ein_number))

	charity_rating = get_rating(ein_number)

	if charity_rating:
		return charity_rating
	else:
		print(get_irs_rating(ein_number))

# <meta property="og:site_name" content="Black Lives Matter">
# <meta property="og:site_name" content="Children's Wish Foundation International">



site_url = 'https://blacklivesmatter.com'
# site_url = 'https://www.redcross.org'
print(get_ein("Black Lives Matter Foundation"))

#https://apps.irs.gov/app/eos/lettersSearch.do?ein1=474143254&dispatchMethod=searchDeterminationLetters&submitName=Search


#https://apps.irs.gov/app/eos/lettersSearch.do?ein1=95-4242541&dispatchMethod=searchDeterminationLetters
