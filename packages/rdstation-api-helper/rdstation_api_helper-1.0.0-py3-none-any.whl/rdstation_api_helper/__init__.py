"""
RD Station API Helper
"""
from .client import RDStationAPI
from .dataclasses import (
    Segmentation,
    SegmentationContact,
    Contact,
    ContactFunnelStatus,
    ConversionEvents,
    Lead,
)
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    DataProcessingError,
    ValidationError,
)

# Main exports
__all__ = [
    "RDStationAPI",
    # Exceptions
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "DataProcessingError",
    "ConfigurationError",
    # Dataclasses
    "Segmentation",
    "SegmentationContact",
    "Contact",
    "ContactFunnelStatus",
    "ConversionEvents",
    "Lead",
]
