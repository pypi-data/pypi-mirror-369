"""Patients client for Open Dental SDK."""

from typing import List, Optional, Union
from ...base.resource import BaseResource
from .models import (
    Patient,
    CreatePatientRequest,
    UpdatePatientRequest,
    PatientListResponse,
    PatientSearchRequest
)


class PatientsClient(BaseResource):
    """Client for managing patients in Open Dental."""
    
    def __init__(self, client):
        """Initialize the patients client."""
        super().__init__(client, "patients")
    
    def get(self, patient_id: Union[int, str]) -> Patient:
        """
        Get a patient by ID.
        
        Args:
            patient_id: The patient ID
            
        Returns:
            Patient: The patient object
        """
        patient_id = self._validate_id(patient_id)
        endpoint = self._build_endpoint(patient_id)
        response = self._get(endpoint)
        return self._handle_response(response, Patient)
    
    def list(self, limit: Optional[int] = None) -> PatientListResponse:
        """
        List all patients.
        
        Args:
            limit: Optional limit on number of results returned (applied client-side)
            
        Returns:
            PatientListResponse: List of patients
        """
        endpoint = self._build_endpoint()
        response = self._get(endpoint)
        
        if isinstance(response, dict):
            return PatientListResponse(**response)
        elif isinstance(response, list):
            # Apply client-side limit if specified
            patients_data = response[:limit] if limit else response
            return PatientListResponse(
                patients=[Patient(**item) for item in patients_data],
                total=len(response)  # Total available, not limited
            )
        else:
            return PatientListResponse(patients=[], total=0)
    
    def create(self, patient_data: CreatePatientRequest) -> Patient:
        """
        Create a new patient.
        
        Args:
            patient_data: The patient data to create
            
        Returns:
            Patient: The created patient object
        """
        endpoint = self._build_endpoint()
        data = patient_data.model_dump()
        response = self._post(endpoint, json_data=data)
        return self._handle_response(response, Patient)
    
    def update(self, patient_id: Union[int, str], patient_data: UpdatePatientRequest) -> Patient:
        """
        Update an existing patient.
        
        Args:
            patient_id: The patient ID
            patient_data: The patient data to update
            
        Returns:
            Patient: The updated patient object
        """
        patient_id = self._validate_id(patient_id)
        endpoint = self._build_endpoint(patient_id)
        data = patient_data.model_dump()
        response = self._put(endpoint, json_data=data)
        return self._handle_response(response, Patient)
    
    def delete(self, patient_id: Union[int, str]) -> bool:
        """
        Delete a patient.
        
        Args:
            patient_id: The patient ID
            
        Returns:
            bool: True if deletion was successful
        """
        patient_id = self._validate_id(patient_id)
        endpoint = self._build_endpoint(patient_id)
        response = self._delete(endpoint)
        return response is None or response.get("success", True)
    
    def search(self, search_params: PatientSearchRequest) -> PatientListResponse:
        """
        Search for patients (client-side filtering).
        
        Note: Open Dental API doesn't support server-side search.
        This method fetches all patients and filters them client-side.
        
        Args:
            search_params: Search parameters
            
        Returns:
            PatientListResponse: List of matching patients
        """
        # Get all patients and filter client-side
        all_patients = self.list()
        filtered_patients = []
        
        for patient in all_patients.patients:
            match = True
            
            if search_params.first_name:
                if not patient.first_name or search_params.first_name.lower() not in patient.first_name.lower():
                    match = False
                    
            if search_params.last_name:
                if not patient.last_name or search_params.last_name.lower() not in patient.last_name.lower():
                    match = False
                    
            if search_params.email:
                if not patient.email or search_params.email.lower() not in patient.email.lower():
                    match = False
                    
            if search_params.phone:
                # Check all phone fields
                phone_match = False
                for phone_field in [patient.home_phone, patient.work_phone, patient.cell_phone]:
                    if phone_field and search_params.phone in phone_field:
                        phone_match = True
                        break
                if not phone_match:
                    match = False
                    
            if search_params.birth_date:
                if patient.birth_date != search_params.birth_date:
                    match = False
                    
            if search_params.chart_number:
                if not patient.chart_number or patient.chart_number != search_params.chart_number:
                    match = False
            
            if match:
                filtered_patients.append(patient)
        
        return PatientListResponse(
            patients=filtered_patients,
            total=len(filtered_patients)
        )
    
    def get_by_email(self, email: str) -> List[Patient]:
        """
        Get patients by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            List[Patient]: List of patients with matching email
        """
        search_params = PatientSearchRequest(email=email)
        result = self.search(search_params)
        return result.patients
    
    def get_by_phone(self, phone: str) -> List[Patient]:
        """
        Get patients by phone number.
        
        Args:
            phone: Phone number to search for
            
        Returns:
            List[Patient]: List of patients with matching phone
        """
        search_params = PatientSearchRequest(phone=phone)
        result = self.search(search_params)
        return result.patients
    
    def get_by_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> List[Patient]:
        """
        Get patients by name.
        
        Args:
            first_name: First name to search for
            last_name: Last name to search for
            
        Returns:
            List[Patient]: List of patients with matching name
        """
        search_params = PatientSearchRequest(
            first_name=first_name,
            last_name=last_name
        )
        result = self.search(search_params)
        return result.patients