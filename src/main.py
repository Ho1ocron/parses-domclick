from asyncio import run

from cian import CianParser
from constants import META_PAYLOAD, HEADERS


async def main():
    # TODO: Add main functionality here
    # TODO: add META_PAYLOAD serialized to parser

    parser = CianParser(meta_payload=META_PAYLOAD)
    await parser.parse()
    print(f"CianParser initialized with API_URL: {parser.API_URL} and DEBUG: {parser.DEBUG}")


def test_api():
    import requests
    response = requests.post(
        url="https://api.cian.ru/search-offers-index/v2/get-meta/",
        json=META_PAYLOAD,
        headers=HEADERS,
        proxies={
            "117.250.3.58": "8080"
        }
    )
    print(response.status_code)
    print(response.text)

if __name__ == "__main__":
    test_api()
    # run(main())