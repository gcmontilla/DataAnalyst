from lxml import html
import csv, os, json
import requests
import unicodecsv as csv
from time import sleep


def amazon_parser(asin):
    debug = True

    url = "http://www.amazon.com/dp/" + asin

    print("Processing: " + url)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }
    page = requests.get(url, headers=headers)

    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)

            XPATH_NAME = '//h1[@id="title"]//text()'
            XPATH_SALE_PRICE = '//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()'
            XPATH_ORIGINAL_PRICE = '//td[contains(text(),"List Price") or contains(text(),"M.R.P") or contains(text(),"Price")]/following-sibling::td/text()'
            XPATH_CATEGORY = '//a[@class="a-link-normal a-color-tertiary"]//text()'
            XPATH_AVAILABILITY = '//div[@id="availability"]//text()'


            RAW_NAME = doc.xpath(XPATH_NAME)
            RAW_SALE_PRICE = doc.xpath(XPATH_SALE_PRICE)
            RAW_CATEGORY = doc.xpath(XPATH_CATEGORY)
            RAW_ORIGINAL_PRICE = doc.xpath(XPATH_ORIGINAL_PRICE)
            RAW_AVAILABILITY = doc.xpath(XPATH_AVAILABILITY)


            NAME = ' '.join(''.join(RAW_NAME).split()) if RAW_NAME else None
            SALE_PRICE = ' '.join(''.join(RAW_SALE_PRICE).split()).strip() if RAW_SALE_PRICE else None
            CATEGORY = ' > '.join([i.strip() for i in RAW_CATEGORY]) if RAW_CATEGORY else None
            ORIGINAL_PRICE = ''.join(RAW_ORIGINAL_PRICE).strip() if RAW_ORIGINAL_PRICE else None
            AVAILABILITY = ''.join(RAW_AVAILABILITY).strip() if RAW_AVAILABILITY else None
            SELLERS = grab_sellers(url)

            if not ORIGINAL_PRICE:
                ORIGINAL_PRICE = SALE_PRICE

            STATUS = define_status(ORIGINAL_PRICE, SALE_PRICE)

            if debug:
                print(SALE_PRICE)
                print(ORIGINAL_PRICE)
               
            if page.status_code != 200:
                raise ValueError('captcha')
            data = {
                'NAME': NAME,
                'SALE_PRICE': SALE_PRICE,
                'CATEGORY': CATEGORY,
                'ORIGINAL_PRICE': ORIGINAL_PRICE,
                'STATUS': STATUS,
                'AVAILABILITY': AVAILABILITY,
                'SELLER': SELLERS,
                'URL': url
            }

            return data

        except Exception as e:
            print(e)


def define_status(current, sale):
    current = float(current[1:])
    if sale is not None:
        sale = float(sale[1:])

    if current == sale:
        return "LOWEST PRICE"
    else:
        return "NO SALE"


def grab_sellers(asin):
    url = "https://www.amazon.com/gp/offer-listing/" + asin + "/ref=dp_olp_0?ie=UTF8&condition=all"

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'
    }
    page = requests.get(url, headers=headers)

    while True:
        sleep(3)
        try:
            doc = html.fromstring(page.content)

            XPATH_SELLERS = '//a[contains(@href,"olp_merch_name")]/text()'
            RAW_SELLERS = doc.xpath(XPATH_SELLERS)
            return RAW_SELLERS

        except Exception as e:
            print(e)


def to_csv(data):
    with open('data.csv', 'wb') as csvfile:
        fieldnames = ["NAME", "CATEGORY", "ORIGINAL_PRICE", "SALE_PRICE", "STATUS", "SELLER", "AVAILABILITY", "URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for d in data:
            writer.writerow(d)


def read_asin(asin=None):
    # AsinList = csv.DictReader(open(os.path.join(os.path.dirname(__file__),"Asinfeed.csv")))
    AsinList = ['B0194WDVHI',
                # 'B00JGTVU5A',
                # 'B00GJYCIVK',
                # 'B00EPGK7CQ',
                # 'B00EPGKA4G',
                # 'B00YW5DLB4',
                # 'B00KGD0628',
                # 'B00O9A48N2',
                # 'B00O9A4MEW',
                # 'B00UZKG8QU',
                ]

    extracted_data = []
    for i in AsinList:
        extracted_data.append(amazon_parser(i))
        sleep(5)

    # f = open('data.json', 'w')
    # json.dump(extracted_data, f, indent=4)
    to_csv(extracted_data)


if __name__ == "__main__":
    read_asin()
