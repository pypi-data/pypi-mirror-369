"""Benefits types and enums for Open Dental SDK."""

from enum import Enum


class BenefitType(str, Enum):
    """Benefit type enum."""
    LIMITATION = "limitation"
    DEDUCTIBLE = "deductible"
    COINSURANCE = "coinsurance"
    COPAY = "copay"
    EXCLUSION = "exclusion"
    WAITING_PERIOD = "waiting_period"


class CoverageLevel(str, Enum):
    """Coverage level enum."""
    INDIVIDUAL = "individual"
    FAMILY = "family"
    NONE = "none"


class CoverageType(str, Enum):
    """Coverage type enum."""
    PREVENTIVE = "preventive"
    BASIC = "basic"
    MAJOR = "major"
    ORTHODONTIC = "orthodontic"
    EMERGENCY = "emergency"
    DIAGNOSTIC = "diagnostic"


class TimePeriod(str, Enum):
    """Time period enum."""
    YEAR = "year"
    MONTH = "month"
    WEEK = "week"
    DAY = "day"
    LIFETIME = "lifetime"