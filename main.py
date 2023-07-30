import subprocess
import json
import argparse

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



    def scrape_product_listing_page(self, page_num):
        """
        Scrapes a product listing page and returns a list of product info and product URLs
        """
        url = f"{self.base_url}&page={page_num}"
        soup = self.get_soup(url)
        products = []

        for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
            product = {}

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

        return products

    
    def scrape_product_page(self, url):
        """
        Scrapes a product page and returns a dictionary of product info
        """
        soup = self.get_soup(url)

        if not soup:
            return None

        # description_elem = soup.find('div', {'id': 'productDescription'})
        # description = description_elem.get_text().strip() if description_elem else None

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
        title_block_left_section = soup.find('div', {'id': 'titleBlockLeftSection'})
        if title_block_left_section:
            manufacturer_elem = title_block_left_section.find('a', {'id': 'bylineInfo'})
            manufacturer = manufacturer_elem.get_text().strip().replace('Brand: ', '') if manufacturer_elem else None
        else:
            manufacturer = None

        return {
            'Description': description,
            'ASIN': asin,
            'Manufacturer': manufacturer
        }


def scrape_and_save_data(base_url, num_pages):
    """
    Scrapes and saves data to a CSV file
    """

    amazon_scraper = AmazonScraper(base_url, user_agent)
    all_data = [] 
    for page_num in range(1, num_pages + 1):
         
        products_data = amazon_scraper.scrape_product_listing_page(page_num)

        # product_data is a list with each element being a dictionary of product info. url key has the product URL
        
        for i in products_data:

            if i['num_reviews'] == "M.R.P:": 
                i['num_reviews'] = None
            
            if i['price'] != None:
                i['price'] = int(i['price'].replace(',', ''))

            product_url = i['url']
            product_data = amazon_scraper.scrape_product_page(product_url)
            all_data.append({**i, **product_data})
            # replace any empty values with None
            for key, value in all_data[-1].items():
                if value == '':
                    all_data[-1][key] = None
            
            print(f"Scraped {product_url}")
            
        df = pd.DataFrame(all_data)
   

    df.to_csv('products_data.csv', index=False)

# This function will be replaced with regex later
# def check_url(url):
#     # add https if not present
#     if not url.startswith('https://'):
#         url = 'https://' + url
#     url_b = url1.split("&")[0].split("/")
#     url_c = url1.split("&")[1].split("&")
#     if url_b[2] == "www.amazon.in":
#         if url_b[3][3:].isalphanum() and url_b[3][:2] == "s?":
#             if url
  


if __name__ == "__main__":
    print("<< Welcome to AmazonScraper by realkarthiknair >>")
    parser = argparse.ArgumentParser(description = "Scrape Amazon products data from search results and dump to a CSV file")
    parser.add_argument('-u', '--url', help="Base URL for product search results \n e.g. https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1") # required = True
    parser.add_argument('-n', '--num-pages', help="Number of pages to scrap")
    parser.add_argument('-a', '--user-agent', help="user agent string to use for scraping \n default is Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    parser.add_argument('-f', '--file', help="File name to save scraped data to \n default is products_data.csv")
    args = parser.parse_args()
    requirements_file = "requirements.txt"
    # if args.url:
    #     base_url = args.url
    # else:
    #     while True:
    #         base_url = input("Enter base URL for product search results: ")
    #         # check if base URL is in format https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1
    #         # if not check_url(base_url):
    #         #     print("Please enter a valid URL")
    #         if not base_url:
    #             print("Please enter a valid URL")

    if install_requirements(requirements_file):
        import requests
        from bs4 import BeautifulSoup
        import pandas as pd
        import time
        from urllib.parse import urljoin
        base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        num_pages = 2
        scrape_and_save_data(base_url, num_pages)
    else:
        print("Failed to install requirements. Exiting.")
        exit(1)