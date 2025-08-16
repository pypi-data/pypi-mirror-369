"""Benefits models for Open Dental SDK."""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from ...base.models import BaseModel


class Benefit(BaseModel):
    """Benefit model."""
    
    # Primary identifiers
    id: int
    benefit_num: int
    
    # Plan association
    plan_num: int
    patient_num: Optional[int] = None
    
    # Benefit details
    code_num: Optional[int] = None
    procedure_code: Optional[str] = None
    coverage_level: Optional[str] = None
    
    # Financial limits
    annual_max: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    deductible_family: Optional[Decimal] = None
    
    # Percentages
    percent: Optional[int] = None  # 0-100
    coinsurance: Optional[int] = None  # 0-100
    
    # Time limits
    benefit_year: Optional[int] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    
    # Frequency limits
    quantity: Optional[int] = None
    time_period: Optional[str] = None  # "year", "month", "week", etc.
    
    # Age limits
    age_limit: Optional[int] = None
    
    # Coverage type
    coverage_type: Optional[str] = None
    benefit_type: Optional[str] = None
    
    # Timestamps
    date_created: Optional[datetime] = None
    date_modified: Optional[datetime] = None


class CreateBenefitRequest(BaseModel):
    """Request model for creating a new benefit."""
    
    # Required fields
    plan_num: int
    
    # Optional fields
    patient_num: Optional[int] = None
    code_num: Optional[int] = None
    procedure_code: Optional[str] = None
    coverage_level: Optional[str] = None
    
    # Financial limits
    annual_max: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    deductible_family: Optional[Decimal] = None
    
    # Percentages
    percent: Optional[int] = None
    coinsurance: Optional[int] = None
    
    # Time limits
    benefit_year: Optional[int] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    
    # Frequency limits
    quantity: Optional[int] = None
    time_period: Optional[str] = None
    
    # Age limits
    age_limit: Optional[int] = None
    
    # Coverage type
    coverage_type: Optional[str] = None
    benefit_type: Optional[str] = None


class UpdateBenefitRequest(BaseModel):
    """Request model for updating an existing benefit."""
    
    # All fields are optional for updates
    plan_num: Optional[int] = None
    patient_num: Optional[int] = None
    code_num: Optional[int] = None
    procedure_code: Optional[str] = None
    coverage_level: Optional[str] = None
    
    # Financial limits
    annual_max: Optional[Decimal] = None
    deductible: Optional[Decimal] = None
    deductible_family: Optional[Decimal] = None
    
    # Percentages
    percent: Optional[int] = None
    coinsurance: Optional[int] = None
    
    # Time limits
    benefit_year: Optional[int] = None
    effective_date: Optional[date] = None
    expiration_date: Optional[date] = None
    
    # Frequency limits
    quantity: Optional[int] = None
    time_period: Optional[str] = None
    
    # Age limits
    age_limit: Optional[int] = None
    
    # Coverage type
    coverage_type: Optional[str] = None
    benefit_type: Optional[str] = None


class BenefitListResponse(BaseModel):
    """Response model for benefit list operations."""
    
    benefits: List[Benefit]
    total: int
    page: Optional[int] = None
    per_page: Optional[int] = None


class BenefitSearchRequest(BaseModel):
    """Request model for searching benefits."""
    
    plan_num: Optional[int] = None
    patient_num: Optional[int] = None
    procedure_code: Optional[str] = None
    coverage_level: Optional[str] = None
    benefit_type: Optional[str] = None
    benefit_year: Optional[int] = None
    
    # Pagination
    page: Optional[int] = 1
    per_page: Optional[int] = 50