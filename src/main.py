from asyncio import run

from cian import CianParser
from constants import META_PAYLOAD


async def main():
    # TODO: Add main functionality here
    # TODO: add META_PAYLOAD serialized to parser

    parser = CianParser(meta_payload=META_PAYLOAD)
    print(f"CianParser initialized with API_URL: {parser.API_URL} and DEBUG: {parser.DEBUG}")


if __name__ == "__main__":
    run(main())