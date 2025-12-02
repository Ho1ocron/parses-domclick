if __name__ == "__main__":
    # TODO: Add main functionality here
    # TODO: add META_PAYLOAD serialized to parser
    from cian.cian import CianParser

    parser = CianParser()
    print(f"CianParser initialized with API_URL: {parser.API_URL} and DEBUG: {parser.DEBUG}")