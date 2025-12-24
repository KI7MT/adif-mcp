"""Stub implementation for QRZ.com integration tools."""

from typing import TypedDict


class QrzBio(TypedDict):
    """Shape of a QRZ.com bio/station report."""

    callsign: str
    name: str
    grid: str
    country: str
    license_class: str
    qsl_mgr: str
    image_url: str


def fetch_bio(callsign: str) -> QrzBio:
    """
    Simulates fetching QRZ.com bio data for a given callsign.
    """
    return {
        "callsign": callsign.upper(),
        "name": "Jane Doe",
        "grid": "FN20",
        "country": "United States",
        "license_class": "Extra",
        "qsl_mgr": "BURO",
        "image_url": "https://files.qrz.com/x/k1jt/primary.jpg",
    }
