from typing import Any, Dict, List, Optional, Union
from parser_domclick.domclick.models import Offer

import logging


class Parser:
    logger: logging.Logger

    def __init__(self, response: Dict) -> None:
        self.response = response

    def to_offers(self) -> List[Offer]:
        self.logger = logging.getLogger(__name__)
        items = self.response.get("items", [])
        offers: List[Offer] = []

        for item in items:
            try:
                offers.append(self._item_to_offer(item))
                self.logger.debug(f"Appending offers.")
            except Exception as e:
                print(f"Error: {e}")
                self.logger.exception(f"Error during converting offers.", exc_info=True)
                continue

        return offers

    def _item_to_offer(self, item: Dict[str, Any]) -> Offer:
        return Offer(
            offer_id=item.get("id"),
            type=self._property_type(item),
            area=self._area(item),
            possible_purpose=self._possible_purpose(item),
            building_class=self._building_class(item),
            metro=self._metro(item),
            address=self._address(item),
            building=self._building(item),
            floor=self._floor(item),
            ceiling_height_m=self._ceiling_height(item),
            price=self._price(item),
            contract_type=self._contract_type(item),
            phones=self._phones(item),
            description=item.get("description"),
            layout=item.get("layout"),
            listing_url=self._listing_url(item),
            area_units="м2",
            currency=self._currency(item),
            payment_type=self._payment_type(item),
            prepayment=self._prepayment(item),
            tax=self._tax(item),
        )

    def _property_type(self, item: Dict[str, Any]) -> Optional[str]:
        deal = item.get("dealType")
        offer = item.get("offerType")
        if deal and offer:
            return f"{deal.capitalize()} {offer}"
        return offer

    def _area(self, item: Dict[str, Any]) -> float:
        area = item.get("area")
        if isinstance(area, dict):
            return float(area.get("value", 0))
        return float(area or 0)

    def _possible_purpose(self, item: Dict[str, Any]) -> Optional[str]:
        purposes = item.get("possiblePurposes")
        if isinstance(purposes, list) and purposes:
            return ", ".join(p.get("name") for p in purposes if "name" in p)
        return None

    def _building_class(self, item: Dict[str, Any]) -> Optional[str]:
        building = item.get("building")
        if isinstance(building, dict):
            return building.get("class")
        return None

    def _metro(self, item: Dict[str, Any]) -> Optional[str]:
        undergrounds = item.get("undergrounds")
        if isinstance(undergrounds, list) and undergrounds:
            metro = undergrounds[0]
            name = metro.get("name")
            time = metro.get("time")
            transport = metro.get("transportType")
            if name and time:
                return f"{name} — {time} мин ({transport})"
            return name
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
        floor = item.get("floor")
        floors = item.get("floors")
        if floor is not None and floors is not None:
            return f"{floor}/{floors}"
        return None

    def _ceiling_height(self, item: Dict[str, Any]) -> Optional[float]:
        height = item.get("ceilingHeight")
        return float(height) if height is not None else None

    def _price(self, item: Dict[str, Any]) -> float:
        price = item.get("price")
        if isinstance(price, dict):
            return float(price.get("value", 0))
        return float(price or 0)

    def _contract_type(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("contractType")

    def _phones(self, item: Dict[str, Any]) -> Optional[Union[int, str]]:
        phones = item.get("phones")
        if isinstance(phones, list) and phones:
            phone = phones[0]
            return phone.get("number") or phone.get("formatted")
        return None

    def _listing_url(self, item: Dict[str, Any]) -> Optional[str]:
        path = item.get("path")
        if path:
            return f"https://www.cian.ru{path}"
        return None

    def _currency(self, item: Dict[str, Any]) -> Optional[str]:
        currency = item.get("currency")
        if currency == "RUB":
            return "руб"
        return currency

    def _payment_type(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("paymentType")

    def _prepayment(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("prepayment")

    def _tax(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("taxSystem")