import requests
from bs4 import BeautifulSoup

url = 'https://www.reg.uci.edu/perl/WebSoc'

# Fetch the page content
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

dropdown = soup.find('select', {'name': 'Dept'})

options = dropdown.find_all('option')[1:]

list = []

if options:

    for option in options:
        text = option.text.strip()
        dept_codes = text.split(' .')[0]
        list.append(dept_codes)
        print(f'"{dept_codes}":,')  
else:
    print("No options found in the dropdown.")
