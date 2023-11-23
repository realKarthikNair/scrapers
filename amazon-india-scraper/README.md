# AmazonScraper by realkarthiknair

## Description

Scrape Amazon product data from search results and save it to a CSV file. The script is designed to work specifically with Amazon India (amazon.in).

## Pre-requisites (as Tested)

- Python 3.10.x or above
- requests 2.31.0*
- beautifulsoup4 4.12.2*
- pandas 2.0.3*
- urllib3 1.26.16*

_* will be installed automatically if not already installed_

## Usage

1. Clone or download this repository.

```
git clone https://github.com/realKarthikNair/amazon-scrapper
```

2. Open a terminal and navigate to the project directory.

```
cd amazon-scrapper
```

3. Run the script using the following command:

   ```bash
   python amazon_scraper.py -u <base_url> -n <num_pages> -a <user_agent> -f <csv_file_name>
    ```

[This](products_data.csv) file is the output of

```
python main.py -u "https://www.amazon.in/s?k=mouse&crid=39QCIRY4VLJHD&sprefix=mouse%2Caps%2C208&ref=nb_sb_noss_1" -n 3
```

## Things to Remember

- The script is designed to work with Amazon India (amazon.in) only.
- Amazon technically does not allow web scraping. But you can scrape as long as you don't make too many requests in a short period of time or do not scrape off an unreasonable amount of data. If you do so, Amazon could block your IP address, terminate your account, or worst of all, take legal action against you (which is highly unlikely). Just be careful. 


>Made with Love™ ❤️ <br>
>by Karthik Nair 

## How to reach me? 

<p align="left">
    <a href="https://www.instagram.com/karthiknair.sh" alt="instagram">
        <img src="https://img.shields.io/badge/Instagram-%F0%9F%91%A8%E2%80%8D%F0%9F%92%BB-yellowgreen" /></a>
    <a href="https://www.telegram.me/realkarthiknair" alt="Telegram">
        <img src="https://img.shields.io/badge/Telegram-%F0%9F%91%A8%E2%80%8D%F0%9F%92%BB-orange" /></a>
    <a href="https://www.twitter.com/realkarthiknair" alt="twitter">
        <img src="https://img.shields.io/badge/Twitter-%F0%9F%91%A8%E2%80%8D%F0%9F%92%BB-orange" /></a>
</p>

## If you want to buy me a coffee!

<a  href="https://coindrop.to/realkarthiknair" target="_blank"><img  src="https://coindrop.to/embed-button.png" style="border-radius: 10px; height: 114px !important;width: 458px !important;" alt="Coindrop.to me"></img></a>
<br>
Crypto? 

Send ETH

```0x9EcA8Bd2139e95BFbBd18CC557054C3736f5fD5e```

Send BTC
```bc1qh20ghe9nlvns6td77wj539hf87kjglyfpslh28```


