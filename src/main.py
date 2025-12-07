from asyncio import run

from cian import CianParser, CianBrowser
from constants import META_PAYLOAD, HEADERS


def main():    
    browser = CianBrowser()
    browser.search(
        query="Санкт-Петербург",
        price_gte="1000000",
        price_lte="100000000",
        area_gte="10",
        area_lte="10000",
    )
    parser = CianParser(meta_payload=META_PAYLOAD)
    offers = parser.read_offers_from_file()

    print(offers)


if __name__ == "__main__":
    main()