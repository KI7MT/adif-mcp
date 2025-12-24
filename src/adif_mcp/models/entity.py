"""ADIF Entity (DXCC) Model definition."""

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Represents a DXCC Entity or Country."""

    name: str = Field(..., description="Entity Name (e.g. United States)")
    primary_prefix: str = Field(..., description="Primary Prefix (e.g. K)")
    continent: str = Field(..., description="Continent Abbreviation (e.g. NA)")
    cq_zone: int = Field(..., description="CQ Zone")
    itu_zone: int = Field(..., description="ITU Zone")
