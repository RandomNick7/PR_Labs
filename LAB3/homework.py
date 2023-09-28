import requests
from bs4 import BeautifulSoup
from pprint import pprint as pp
import json
import re

def scrape(url):
    data = []
    data_dict = {}
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')

    # Get basic info regarding the product
    data_dict['title'] = soup.find('h1', attrs={'itemprop':'name'}).text.strip()
    data_dict['price'] = soup.find('span', attrs={'itemprop':'price'}).text.strip()
    data_dict['seller'] = soup.find('a', attrs={"class":"buyer_experiment"}).text.strip()

    location = soup.find('span', attrs={"class":"adPage__aside__address-feature__text"})
    if location is not None:
        data_dict['location'] = location.text
    else:
        data_dict['location'] = ''

    # Get all the characteristics listed at the bottom of the page
    characteristics = {}
    for prop in soup.find('div', attrs={"class":"adPage__content__features"}).find_all('li', attrs={"itemprop":"additionalProperty"}):
        name = prop.find('span', attrs={"itemprop":"name"})
        value = prop.find('span', attrs={"itemprop":"value"})
        if name is not None:
            if value is None:
                characteristics[name.text.strip()] = ''
            else:
                characteristics[name.text.strip()] = value.text.strip()
    data_dict['characteristics'] = characteristics
    data.append(data_dict)

    # Get any phone numbers listed (it's not *actually* hidden on the site)
    nums = []
    contacts = soup.find('dl', attrs={"class":"adPage__content__phone"})
    if contacts is not None:
        contacts = contacts.find_all('a')
        for tel in contacts:
            nums.append(tel['href'])
    data_dict['contacs'] = nums

    return data


print("Enter a link to scrape:")

# With all the links in hand, it's time to extract some of their data
data = scrape(input())

# Write the output to a JSON file
with open('data.json','w',encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("Scraping done! Check 'data.json' in the same directory as this script")
