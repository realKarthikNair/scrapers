import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin


class AmazonScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

    def get_soup(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
            return BeautifulSoup(response.content, 'html.parser')
        except ConnectionError as e:
            print("Connection Error:", e)
            return None
        except requests.exceptions.RequestException as e:
            print("Request Exception:", e)
            return None

    
    def scrape_product_listing_page(self, page_num):
        url = f"{self.base_url}&page={page_num}"
        soup = self.get_soup(url)
        product_urls = []

        for item in soup.find_all('a', {'class': ['a-link-normal', 's-underline-text', 's-underline-link-text', 's-link-style', 'a-text-normal']}):
            if 'href' in item.attrs and 'aria-hidden' not in item.attrs:
                product_url = item.attrs['href']
                full_product_url = urljoin('https://www.amazon.in/', product_url)
                product_urls.append(full_product_url)

        return product_urls

    
    def scrape_product_page(self, url):
        soup = self.get_soup(url)

        if not soup:
            return None

        product_name_elem = soup.find('span', {'id': 'productTitle'})
        product_name = product_name_elem.get_text().strip() if product_name_elem else None

        product_price_elem = soup.find('span', {'id': 'priceblock_ourprice'})
        product_price = product_price_elem.get_text().strip() if product_price_elem else None

        rating_elem = soup.find('span', {'class': 'a-icon-alt'})
        rating = rating_elem.get_text().strip().split()[0] if rating_elem else None

        num_reviews_elem = soup.find('span', {'id': 'acrCustomerReviewText'})
        num_reviews = num_reviews_elem.get_text().strip().split()[0] if num_reviews_elem else None

        description_elem = soup.find('div', {'id': 'productDescription'})
        description = description_elem.get_text().strip() if description_elem else None

        asin_elem = soup.find('th', string='ASIN')
        asin = asin_elem.find_next('td').get_text().strip() if asin_elem else None

        manufacturer_elem = soup.find('th', string='Manufacturer')
        manufacturer = manufacturer_elem.find_next('td').get_text().strip() if manufacturer_elem else None

        return {
            #'Product URL': url,
            'Product Name': product_name,
            'Product Price': product_price,
            'Rating': rating,
            'Number of Reviews': num_reviews,
            'Description': description,
            'ASIN': asin,
            'Manufacturer': manufacturer
        }


def scrape_and_save_data(base_url, num_pages):
    all_data = []

    amazon_scraper = AmazonScraper(base_url)

    for page_num in range(1, num_pages + 1):
        product_urls = amazon_scraper.scrape_product_listing_page(page_num)

        for product_url in product_urls:
            product_data = amazon_scraper.scrape_product_page(product_url)
            all_data.append(product_data)
            
            print(f"Scraped {product_url}")
            # time.sleep(1)
            if len(all_data)>20:
                break

    df = pd.DataFrame(all_data)
    df.to_csv('amazon_products_data.csv', index=False)
    print("Data scraped and saved successfully.")


if __name__ == "__main__":
    base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1'
    num_pages = 20
    scrape_and_save_data(base_url, num_pages)