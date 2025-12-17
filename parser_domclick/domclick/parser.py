from typing import Any, Dict, List, Optional, Union
from parser_domclick.domclick.models import Offer

import logging


class Parser:
    logger: logging.Logger
    response: dict[str, dict]

    def __init__(self, response: Dict) -> None:
        self.response = response
        self.logger = logging.getLogger(__name__)

    def to_offers(self) -> List[Offer]:
        items = self.response["result"].get("items", [])
        offers: List[Offer] = []
        self.logger.info(f"Appending offers.")
        for item in items:
            try:
                offers.append(self._item_to_offer(item))
                
            except Exception as e:
                self.logger.exception(f"Error during converting offers.", exc_info=True)
                continue

        return offers
    
    def _pagination(self) -> Dict[str, Any]:
        pagination = self.response["result"].get("pagination", {})
        return pagination
    
    @property
    def get_offset(self) -> int:
        offset = self.response["result"]["pagination"]["offset"]
        return offset
    
    @property
    def get_total(self) -> int:
        total = self.response["result"]["pagination"]["limit"]
        return total

    def _item_to_offer(self, item: Dict) -> Offer:
        return Offer(
            offer_id=item.get("id"),  # type: ignore
            type=self._property_type(item),
            area=self._area(item),
            metro=self._metro(item),
            address=self._address(item),
            building=self._building(item),
            floor=self._floor(item),
            price=self._price(item),
            description=item.get("description"),
            layout=item.get("layout"),
            listing_url=self._listing_url(item),
            area_units="м2",
        )

    def _property_type(self, item: Dict[str, Any]) -> Optional[str]:
        deal = item.get("dealType")
        offer = item.get("offerType")
        if deal and offer:
            return f"{deal.capitalize()} {offer}"
        return offer

    def _area(self, item: Dict[str, Any]) -> float:
        objectInfo: dict[str, float] = item["objectInfo"]
        area = objectInfo.get("area")

        if isinstance(area, dict):
            return float(area.get("value", 0))
        return float(area or 0)
    
    def _metro(self, item: Dict[str, Dict[str, Any]]) -> Optional[str]:
        address: Dict[str, list[str]] = item["address"]
        if isinstance(address, dict):
            metro: list[str] = address["subways"]
            if metro:
                return metro[0]
        return None

    def _address(self, item: Dict[str, Any]) -> Optional[str]:
        address = item.get("address")
        if isinstance(address, dict):
            return address.get("displayName")
        return None

    def _building(self, item: Dict[str, Any]) -> Optional[str]:
        building = item.get("building")
        if isinstance(building, dict):
            return building.get("name")
        return None

    def _floor(self, item: Dict[str, Any]) -> Optional[str]:
        objectInfo: dict[str, float] = item["objectInfo"]
        floor = objectInfo.get("floor", 10)
        if floor is not None:
            return f"{floor}"
        return None

    def _price(self, item: Dict[str, Any]) -> float:
        price = item.get("price")
        if isinstance(price, dict):
            return float(price.get("value", 0))
        return float(price or 0)
    
    def _listing_url(self, item: Dict[str, Any]) -> Optional[str]:
        path = item.get("path")
        if path:
            return path
        return None