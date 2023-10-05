import socket
import re
import json
from bs4 import BeautifulSoup

# This TCP scraper is capable of retrieving all the data of the server it was made to target

HOST = '127.0.0.1'
TARGET = 6090

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Connect to host and send a request for the page
client.connect((HOST,TARGET))
print(f"Connected to {HOST}:{TARGET}")

# While there are pages to visit, keep parsing
visited_pages = []
discovered_pages = ["/"]
page_types = ["html"]
index = 0

# Products - list of dicts containing the item information
products = []

while len(visited_pages) < len(discovered_pages):
    # Request the page from the server...
    page = discovered_pages[index]
    request = f"GET {page} HTTP/1.1"
    client.send(request.encode('utf-8'))
    data = client.recv(2048).decode('utf-8')
    data = data[data.find('\n'):]

    soup = BeautifulSoup(data, "html.parser")
    #If we're currently scraping an html page...
    if page_types[index] == "html":

        # Find the addresses to other pages inside the resulting string
        addr_list = soup.find_all("a")

        for addr in addr_list:
            a = "/"
            if addr['href'] != "/":
                a += addr['href']
            # Ignoring hrefs with special purpose...
            if a[:5] != "/tel:" and a[:8] != "/mailto:":
                if a not in discovered_pages:
                    discovered_pages.append(a)
                    page_types.append("html")

        # Find JS code too, The products listings is generated using that
        src_list = soup.find_all("script")
        for script in src_list:
            if '/'+script['src'] not in discovered_pages:
                discovered_pages.append('/'+script['src'])
                page_types.append("js")

        # Save the pages as HTML files
        if(page != '/'):
            f = open(f"./data/{page}.html","w")
        else:
            f = open(f"./data/index.html","w")
        f.write(data)

    # The below is needed for the fact that all of the products are generated by JS code

    # If scraping a js file...
    elif page_types[index] == "js":
        # Find mentions of .json files and get those too
        match = re.search(r"'.*\.json'", soup.text).group()[1:-1]
        if match not in discovered_pages:
            discovered_pages.append('/'+match)
            page_types.append("json")


        f = open(f"./data/{page}.js","w")
        f.write(data)

    # With direct access to the json file, splkit it into indiviual items and store their relevant data
    elif page_types[index] == "json":
        json_list = json.loads(soup.text)
        i = 1

        for product in json_list:
            products.append(product)
            f = open(f"./data/jsons/item{i}.json","w")
            f.write(json.dumps(product))
            i+=1


    visited_pages.append(page)
    index+=1;

    #print(discovered_pages)
    #print(visited_pages)

print("Scraped the data, check /data directory")
client.close()
