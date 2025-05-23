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

        list.append(option.text.strip())
        print(option.text.strip()+" - " + option['value'])  
else:
    print("No options found in the dropdown.")
