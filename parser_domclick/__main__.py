import logging

from parser_domclick.cian import CianBrowser

logging.basicConfig(level=logging.INFO)


def main():
    from pprint import pprint

    browser = CianBrowser()
    offers = browser.search("Москва", "1000000", "2000000", "50", "100")

    pprint(offers)


if __name__ == "__main__":
    main()
