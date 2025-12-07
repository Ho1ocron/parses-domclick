from typing import Optional
from pydantic import BaseModel, Field, computed_field, field_validator


class Offer(BaseModel):
    listing_id: int
    type: Optional[str]
    area: Optional[float]
    possible_purpose: Optional[str]
    building_class: Optional[str]
    metro: Optional[str]
    address: Optional[str]
    building: Optional[str]
    floor: Optional[str]
    ceiling_height_m: Optional[str]
    price: Optional[str]
    rent_type: Optional[str]
    phones: Optional[str]
    description: Optional[str]
    parking: Optional[str]
    layout: Optional[str]
    entrance: Optional[str]
    access: Optional[str]
    additional: Optional[str]
    elevator: Optional[str]
    listing_url: Optional[str]
