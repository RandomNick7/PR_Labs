import requests
from bs4 import BeautifulSoup
from pprint import pprint as pp
from urllib.parse import urljoin
import re

# The function that performs the crawling itself, done recursively
# Stops when reaching max_count or when page runs out of links
def crawl(url, link_list, num, max_count, soup):
    if max_count >= 0 and max_count == len(link_list):
        return link_list

    if(num<len(soup)):
        path = soup[num].get('href')
        if path and path.startswith('/'):
            path = urljoin(url, path)

            if re.match('https://999.md/r[ou]/[0-9]+', path):
                if(path not in link_list):
                    link_list.append(path)
        crawl(url,link_list, num+1, max_count, soup)
    return link_list

def main():
    # Get desired input
    print("Enter URL:")
    url = input()
    print("Enter page count: (-1 for all pages)")
    max_count = int(input())

    # Get the links off of the given page
    soup = BeautifulSoup(requests.get(url).text, 'html.parser').find_all('a')
    total_list = []

    # Get all the links on the current page
    link_list = crawl(url,[],0,max_count,soup)
    total_list += link_list

    # If on a site with multiple pages...
    if re.match('https://999.md/r[ou]/list/', url):
        page_count = 2
        # While there are still items on other pages and the link limit wasn't reached, scrape the pages
        while(len(link_list)>0 and len(total_list)<max_count or len(link_list)>0 and max_count < 0):
            link_list = []
            page = url + "?%3Fpage%3D2&page=" + str(page_count)
            soup = BeautifulSoup(requests.get(page).text, 'html.parser').find_all('a')
            link_list = crawl(page, link_list, 0, max_count - len(total_list), soup)
            total_list += link_list
            page_count += 1

    f = open('links.txt','w')
    for link in total_list:
        f.write(link+'\n')
    f.close()

    print("Done! Check 'links.txt' in the same directory as this script")

    return total_list

main()
