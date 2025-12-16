import logging

from parser_domclick.domclick.browser import DomClickBrowser

logging.basicConfig(level=logging.INFO)


def main():
    from pprint import pprint

    browser = DomClickBrowser()
    offers = browser.search("Москва", "1000000", "2000000", "50", "100")

    pprint(offers)


if __name__ == "__main__":
    main()
