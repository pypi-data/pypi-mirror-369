"""Benefits client for Open Dental SDK."""

from typing import List, Optional, Union
from ...base.resource import BaseResource
from .models import (
    Benefit,
    CreateBenefitRequest,
    UpdateBenefitRequest,
    BenefitListResponse,
    BenefitSearchRequest
)


class BenefitsClient(BaseResource):
    """Client for managing benefits in Open Dental."""
    
    def __init__(self, client):
        """Initialize the benefits client."""
        super().__init__(client, "benefits")
    
    def get(self, benefit_id: Union[int, str]) -> Benefit:
        """
        Get a benefit by ID.
        
        Args:
            benefit_id: The benefit ID
            
        Returns:
            Benefit: The benefit object
        """
        benefit_id = self._validate_id(benefit_id)
        endpoint = self._build_endpoint(benefit_id)
        response = self._get(endpoint)
        return self._handle_response(response, Benefit)
    
    def list(self, page: int = 1, per_page: int = 50) -> BenefitListResponse:
        """
        List all benefits.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50)
            
        Returns:
            BenefitListResponse: List of benefits with pagination info
        """
        params = {
            "page": page,
            "per_page": per_page
        }
        endpoint = self._build_endpoint()
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return BenefitListResponse(**response)
        elif isinstance(response, list):
            return BenefitListResponse(
                benefits=[Benefit(**item) for item in response],
                total=len(response),
                page=page,
                per_page=per_page
            )
        else:
            return BenefitListResponse(benefits=[], total=0, page=page, per_page=per_page)
    
    def create(self, benefit_data: CreateBenefitRequest) -> Benefit:
        """
        Create a new benefit.
        
        Args:
            benefit_data: The benefit data to create
            
        Returns:
            Benefit: The created benefit object
        """
        endpoint = self._build_endpoint()
        data = benefit_data.model_dump()
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Benefit)
    
    def update(self, benefit_id: Union[int, str], benefit_data: UpdateBenefitRequest) -> Benefit:
        """
        Update an existing benefit.
        
        Args:
            benefit_id: The benefit ID
            benefit_data: The benefit data to update
            
        Returns:
            Benefit: The updated benefit object
        """
        benefit_id = self._validate_id(benefit_id)
        endpoint = self._build_endpoint(benefit_id)
        data = benefit_data.model_dump()
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, Benefit)
    
    def delete(self, benefit_id: Union[int, str]) -> bool:
        """
        Delete a benefit.
        
        Args:
            benefit_id: The benefit ID
            
        Returns:
            bool: True if deletion was successful
        """
        benefit_id = self._validate_id(benefit_id)
        endpoint = self._build_endpoint(benefit_id)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def search(self, search_params: BenefitSearchRequest) -> BenefitListResponse:
        """
        Search for benefits.
        
        Args:
            search_params: Search parameters
            
        Returns:
            BenefitListResponse: List of matching benefits
        """
        endpoint = self._build_endpoint("search")
        params = search_params.model_dump()
        response = self._get(endpoint, params=params)
        
        if isinstance(response, dict):
            return BenefitListResponse(**response)
        elif isinstance(response, list):
            return BenefitListResponse(
                benefits=[Benefit(**item) for item in response],
                total=len(response),
                page=search_params.page,
                per_page=search_params.per_page
            )
        else:
            return BenefitListResponse(
                benefits=[], 
                total=0, 
                page=search_params.page, 
                per_page=search_params.per_page
            )
    
    def get_by_plan(self, plan_num: int) -> List[Benefit]:
        """
        Get benefits by plan number.
        
        Args:
            plan_num: Plan number
            
        Returns:
            List[Benefit]: List of benefits for the plan
        """
        search_params = BenefitSearchRequest(plan_num=plan_num)
        result = self.search(search_params)
        return result.benefits
    
    def get_by_patient(self, patient_num: int) -> List[Benefit]:
        """
        Get benefits by patient number.
        
        Args:
            patient_num: Patient number
            
        Returns:
            List[Benefit]: List of benefits for the patient
        """
        search_params = BenefitSearchRequest(patient_num=patient_num)
        result = self.search(search_params)
        return result.benefits
    
    def get_by_procedure_code(self, procedure_code: str) -> List[Benefit]:
        """
        Get benefits by procedure code.
        
        Args:
            procedure_code: Procedure code
            
        Returns:
            List[Benefit]: List of benefits for the procedure code
        """
        search_params = BenefitSearchRequest(procedure_code=procedure_code)
        result = self.search(search_params)
        return result.benefits