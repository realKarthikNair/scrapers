import subprocess
import json
import argparse
import os

def install_requirements(requirements_file):
    try:
        subprocess.check_call(['pip', 'install', '-r', requirements_file])
        print("Requirements installed successfully.")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install requirements.")

class AmazonScraper:

    def __init__(self, base_url, user_agent):
        self.base_url = base_url
        self.headers = {
            'User-Agent': user_agent
        }

    def get_soup(self, url):
        """
        Returns BeautifulSoup object for a given URL
        """
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
            return BeautifulSoup(response.content, 'html.parser')
        except ConnectionError as e:
            print(f'''Can't connect to {url}.split('/')[2]
            What you can do:
            - Check your internet connection
            - Try changing the user agent string [--user-agent or -a argument
            - If you are using a VPN or proxy, try turning it off
            ''')
            return None
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return None



    def scrape_product_listing_page(self, page_num, sno):
        """
        Scrapes a product listing page and returns a list of product info and product URLs
        """
        url = f"{self.base_url}&page={page_num}"
        soup = self.get_soup(url)
        products = []

        for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
            product = {}

            product['sno'] = sno
            sno += 1

            title_tag = item.find('h2', class_='a-size-mini')
            if title_tag:
                product['url'] = "https://www.amazon.in" + title_tag.find('a', class_='a-link-normal')['href']
                product['name'] = title_tag.find('span', class_='a-text-normal').text.strip()

            rating_tag = item.find('span', class_='a-icon-alt')
            if rating_tag:
                product['rating'] = rating_tag.text.split()[0]

            price_tag = item.find('span', class_='a-price')
            if price_tag:
                product['price'] = price_tag.find('span', class_='a-offscreen').text.replace('\u20b9', '').strip()

            num_reviews_tag = item.find('span', class_='a-size-base')
            if num_reviews_tag:
                product['num_reviews'] = num_reviews_tag.text.strip()

            products.append(product)

        # with open('products.json', 'w') as f:
        #     json.dump(products, f, indent=4)

        return products, sno

    
    def scrape_product_page(self, url):
        """
        Scrapes a product page and returns a dictionary of product info
        """
        soup = self.get_soup(url)

        if not soup:
            return None
        
        # Find ASIN
        asin_elem = soup.find('div', {'id': 'acBadge_feature_div'})
        asin = None
        if asin_elem:
            script_tag = asin_elem.find('script', type='a-state')
            if script_tag:
                script_content = script_tag.contents[0].strip()
                asin = script_content.split('{"acAsin":"')[-1].split('"}')[0]
            else:
                asin = None
        else:
            asin = None

        # Find Description
        description_elem = soup.find('div', {'id': 'productDescription'})
        if description_elem:
            description = description_elem.get_text().strip()
        else:
            description = None

        # Find Manufacturer
        # title_block_left_section = soup.find('div', {'id': 'titleBlockLeftSection'})
        # if title_block_left_section:
        #     manufacturer_elem = title_block_left_section.find('a', {'id': 'bylineInfo'})
        #     manufacturer = manufacturer_elem.get_text().strip().replace('Brand: ', '') if manufacturer_elem else None
        # else:
        #     manufacturer = None

        # esired_div = soup.find('div', {'id': 'productDetails_feature_div'})

        desired_table = soup.find('table', {'class': 'a-keyvalue prodDetTable'})
        desired_div = soup.find('ul', {'class': 'a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list'})
        if desired_table:
            all_rows = desired_table.find_all('tr')
            for row in all_rows:
                th = row.find('th', {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
                if th and th.text.strip() == 'Manufacturer':
                    desired_tr = row
                    break
            td_value = desired_tr.find('td', {'class': 'a-size-base prodDetAttrValue'}).get_text(strip=True)
            if td_value:
                manufacturer = td_value.split(",")[0]
        
        elif desired_div:
            all_li = desired_div.find_all('li')
            for li in all_li:
                text_span = li.find('span', {'class': 'a-text-bold'})
                if text_span and 'Manufacturer' in text_span.get_text():
                    manufacturer_span = li.find('span', {'class': 'a-list-item'})
                    if manufacturer_span:
                        manufacturer = re.sub(r'\s+', ' ', manufacturer_span.get_text()).strip()
                        break
            else:
                manufacturer = None
            if manufacturer:
                manufacturer = manufacturer[19:]
        else:
            manufacturer = None

        return {
            'Description': description,
            'ASIN': asin,
            'Manufacturer': manufacturer
        }


def scrape_and_save_data(base_url, num_pages, user_agent, file_name):
    """
    Scrapes and saves data to a CSV file
    """

    if not file_name:
        # if products_data.csv already exists, append number to it, repeat until a file name is found
        file_name = "products_data.csv"
        i = 1
        while os.path.exists(file_name):
            file_name = f"products_data({i}).csv"
            i += 1

    amazon_scraper = AmazonScraper(base_url, user_agent)
    all_data = [] 
    sno = 1
    for page_num in range(1, num_pages + 1):
        products_data = amazon_scraper.scrape_product_listing_page(page_num, sno)
        sno = products_data[1]

        # products_data is a list with each element being a dictionary of product info. url key has the product URL
        count = 0
        for i in products_data[0]:

            try: 
                if i['num_reviews'] == "M.R.P:": 
                    i['num_reviews'] = None
            except:
                i['num_reviews'] = None

            try:
                if i['price'] != None:
                    i['price'] = int(i['price'].replace(',', ''))
            except:
                i['price'] = None

            product_url = i['url']
            product_data = amazon_scraper.scrape_product_page(product_url)
            product_data['url'] = product_url
            all_data.append({**{k: v for k, v in i.items() if k in ['sno','name', 'rating', 'price', 'num_reviews']}, **product_data})
            for key, value in all_data[-1].items():
                if value == '':
                    all_data[-1][key] = None
            
            print(f"Scraped {product_url}")
            df = pd.DataFrame(all_data)
            df.to_csv(file_name, index=False, mode='a', header=not os.path.exists(file_name))
            count+= 1
            all_data = []
            print(f"Page: {page_num}, Product: {count}/{len(products_data[0])}")


if __name__ == "__main__":
    print("<< Welcome to AmazonScraper by realkarthiknair >>")
    parser = argparse.ArgumentParser(description = "Scrape Amazon products data from search results and dump to a CSV file")
    parser.add_argument('-u', '--url', help="Base URL for product search results \n e.g. https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1") # required = True
    parser.add_argument('-n', '--num-pages', help="Number of pages to scrap")
    parser.add_argument('-a', '--user-agent', help="user agent string to use for scraping \n default is Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    parser.add_argument('-f', '--file', help="File name to save scraped data to \n default is products_data.csv")
    args = parser.parse_args()

    requirements_file = "requirements.txt"
    import re
    has_strs = lambda string: all(qstr in string for qstr in ["s?k", "&crid", "&sprefix", "&ref"])
    RePattern = r'^https://www.amazon.in/s\?k=[a-zA-Z0-9+%]+(?:&(?:crid=[a-zA-Z0-9]+|sprefix=[a-zA-Z0-9%_+]+|ref=[a-zA-Z0-9%_]+|qid=[0-9]+))*$'
    base_url = args.url 
    while True:
        if not base_url:
            base_url = input("Enter base URL for product search results: ")
        if base_url:
            if (not has_strs(base_url)) or (not re.match(RePattern, base_url)):
                print("Please enter a valid URL")
                base_url = None
            else:
                break

    if install_requirements(requirements_file):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import time
        from urllib.parse import urljoin
        if not args.user_agent:
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        else:
            user_agent = args.user_agent
        if not args.num_pages:
            while True:
                try:
                    num_pages = int(input("Enter number of pages to scrape: "))
                    break
                except ValueError:
                    print("Please enter a valid number")
        else:
            num_pages = int(args.num_pages)
        scrape_and_save_data(base_url, num_pages, user_agent, args.file)
    else:
        print("Failed to install requirements. Exiting.")
        exit(1)