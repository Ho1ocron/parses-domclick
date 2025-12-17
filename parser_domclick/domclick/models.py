from typing import Optional, Union

from pydantic import BaseModel, Field


class Offer(BaseModel):
    """Model representing a real estate offer from the parser."""

    offer_id: int = Field(..., description="Unique identifier of the offer")
    type: Optional[str] = Field(
        None, description="Property type (e.g., 'Продажа офиса')"
    )
    area: float = Field(..., description="Area in square meters")
    possible_purpose: Optional[str] = Field(
        None, description="Possible purpose of the property"
    )
    building_class: Optional[str] = Field(None, description="Building class")
    metro: Optional[str] = Field(
        None, description="Nearest metro station with distance"
    )
    address: Optional[str] = Field(None, description="Full address of the property")
    building: Optional[str] = Field(None, description="Building information")
    floor: Optional[str] = Field(None, description="Floor information (e.g., '-1/6')")
    ceiling_height_m: Optional[float] = Field(
        None, description="Ceiling height in meters"
    )
    price: float = Field(..., description="Price in currency specified")
    contract_type: Optional[str] = Field(
        None, description="Contract type (e.g., 'переуступка прав аренды')"
    )
    phones: Optional[Union[int, str]] = Field(None, description="Contact phone number")
    description: Optional[str] = Field(None, description="Property description")
    layout: Optional[str] = Field(None, description="Layout information")
    listing_url: Optional[str] = Field(None, description="URL to the listing")
    area_units: Optional[str] = Field(None, description="Area units (e.g., ' м2')")
    currency: Optional[str] = Field(None, description="Currency (e.g., 'руб')")
    payment_type: Optional[str] = Field(None, description="Payment type")
    prepayment: Optional[str] = Field(None, description="Prepayment information")
    tax: Optional[str] = Field(None, description="Tax system (e.g., ' УСН')")
