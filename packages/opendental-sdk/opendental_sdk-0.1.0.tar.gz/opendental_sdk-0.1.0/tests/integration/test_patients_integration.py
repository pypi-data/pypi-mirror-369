"""
Integration tests for the Open Dental SDK - Patients resource.

These tests require actual API keys and will make real requests to the Open Dental API.
Set your OPENDENTAL_DEVELOPER_KEY and OPENDENTAL_CUSTOMER_KEY environment variables.
"""

import os
import pytest
from datetime import date, datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from opendental import OpenDentalClient
from opendental.resources.patients.models import (
    Patient, 
    CreatePatientRequest, 
    UpdatePatientRequest,
    PatientSearchRequest
)
from opendental.exceptions import OpenDentalAPIError


class TestPatientsIntegration:
    """Integration tests for Patients API."""
    
    @classmethod
    def setup_class(cls):
        """Set up the test class with API client."""
        # Check for required environment variables
        developer_key = os.getenv("OPENDENTAL_DEVELOPER_KEY")
        customer_key = os.getenv("OPENDENTAL_CUSTOMER_KEY")
        
        if not developer_key or not customer_key:
            pytest.skip("Missing Open Dental API keys. Set OPENDENTAL_DEVELOPER_KEY and OPENDENTAL_CUSTOMER_KEY environment variables.")
        
        if developer_key == "your_developer_key_here" or customer_key == "your_customer_key_here":
            pytest.skip("Please update the .env file with your actual Open Dental API keys.")
        
        # Initialize client
        cls.client = OpenDentalClient(
            developer_key=developer_key,
            customer_key=customer_key,
            debug=True  # Enable debug logging for integration tests
        )
        
        print(f"Initialized Open Dental client with base URL: {cls.client.base_url}")
        print(f"Using developer key: {developer_key[:8]}...")
        print(f"Using customer key: {customer_key[:8]}...")
    
    def test_client_initialization(self):
        """Test that the client initializes correctly."""
        assert self.client is not None
        assert self.client.patients is not None
        assert hasattr(self.client, 'developer_key')
        assert hasattr(self.client, 'customer_key')
        assert self.client.base_url == "https://api.opendental.com/api/v1"
    
    def test_patient_list(self):
        """Test listing patients."""
        try:
            print("\n=== Testing Patient List ===")
            result = self.client.patients.list(page=1, per_page=5)
            
            assert result is not None
            print(f"Retrieved {len(result.patients)} patients")
            print(f"Total patients: {result.total}")
            
            if result.patients:
                first_patient = result.patients[0]
                print(f"First patient: {first_patient.first_name} {first_patient.last_name} (ID: {first_patient.id})")
                
                # Verify patient model structure
                assert hasattr(first_patient, 'id')
                assert hasattr(first_patient, 'first_name')
                assert hasattr(first_patient, 'last_name')
            else:
                print("No patients found in the system")
        
        except OpenDentalAPIError as e:
            print(f"API Error during list operation: {e}")
            print(f"Status code: {e.status_code}")
            print(f"Response data: {e.response_data}")
            raise
        except Exception as e:
            print(f"Unexpected error during list operation: {e}")
            raise
    
    def test_patient_get_by_id(self):
        """Test getting a specific patient by ID."""
        try:
            print("\n=== Testing Patient Get by ID ===")
            
            # First get a list to find a valid patient ID
            patients_list = self.client.patients.list(page=1, per_page=1)
            
            if not patients_list.patients:
                pytest.skip("No patients available to test get by ID")
            
            patient_id = patients_list.patients[0].id
            print(f"Testing get with patient ID: {patient_id}")
            
            # Get the specific patient
            patient = self.client.patients.get(patient_id)
            
            assert patient is not None
            assert patient.id == patient_id
            print(f"Retrieved patient: {patient.first_name} {patient.last_name}")
            print(f"Email: {patient.email}")
            print(f"Phone: {patient.home_phone}")
            print(f"Birth date: {patient.birth_date}")
            
        except OpenDentalAPIError as e:
            print(f"API Error during get operation: {e}")
            print(f"Status code: {e.status_code}")
            print(f"Response data: {e.response_data}")
            raise
        except Exception as e:
            print(f"Unexpected error during get operation: {e}")
            raise
    
    def test_patient_search(self):
        """Test patient search functionality."""
        try:
            print("\n=== Testing Patient Search ===")
            
            # First get a patient to search for
            patients_list = self.client.patients.list(page=1, per_page=1)
            
            if not patients_list.patients:
                pytest.skip("No patients available to test search")
            
            sample_patient = patients_list.patients[0]
            
            # Test search by last name
            if sample_patient.last_name:
                print(f"Searching for patients with last name: {sample_patient.last_name}")
                search_request = PatientSearchRequest(
                    last_name=sample_patient.last_name,
                    page=1,
                    per_page=10
                )
                
                search_result = self.client.patients.search(search_request)
                
                assert search_result is not None
                print(f"Found {len(search_result.patients)} patients with last name '{sample_patient.last_name}'")
                
                # Verify the original patient is in the results
                found_original = any(p.id == sample_patient.id for p in search_result.patients)
                assert found_original, f"Original patient (ID: {sample_patient.id}) should be in search results"
            
            # Test search by first name if available
            if sample_patient.first_name:
                print(f"Searching for patients with first name: {sample_patient.first_name}")
                search_request = PatientSearchRequest(
                    first_name=sample_patient.first_name,
                    page=1,
                    per_page=10
                )
                
                search_result = self.client.patients.search(search_request)
                print(f"Found {len(search_result.patients)} patients with first name '{sample_patient.first_name}'")
                
        except OpenDentalAPIError as e:
            print(f"API Error during search operation: {e}")
            print(f"Status code: {e.status_code}")
            print(f"Response data: {e.response_data}")
            raise
        except Exception as e:
            print(f"Unexpected error during search operation: {e}")
            raise
    
    def test_patient_create_update_delete(self):
        """Test patient create, update, and delete operations."""
        try:
            print("\n=== Testing Patient Create/Update/Delete ===")
            
            # Create a test patient
            create_request = CreatePatientRequest(
                first_name="Test",
                last_name="Integration",
                email="test.integration@example.com",
                home_phone="555-123-4567",
                birth_date=date(1990, 1, 15),
                gender="Male",
                address="123 Test Street",
                city="Test City",
                state="CA",
                zip="90210"
            )
            
            print("Creating test patient...")
            created_patient = self.client.patients.create(create_request)
            
            assert created_patient is not None
            assert created_patient.first_name == "Test"
            assert created_patient.last_name == "Integration"
            print(f"Created patient with ID: {created_patient.id}")
            
            # Update the patient
            update_request = UpdatePatientRequest(
                first_name="Updated Test",
                email="updated.test.integration@example.com",
                cell_phone="555-987-6543"
            )
            
            print(f"Updating patient ID {created_patient.id}...")
            updated_patient = self.client.patients.update(created_patient.id, update_request)
            
            assert updated_patient is not None
            assert updated_patient.first_name == "Updated Test"
            assert updated_patient.email == "updated.test.integration@example.com"
            print("Patient updated successfully")
            
            # Delete the patient
            print(f"Deleting patient ID {created_patient.id}...")
            delete_result = self.client.patients.delete(created_patient.id)
            
            assert delete_result is True
            print("Patient deleted successfully")
            
            # Verify deletion by trying to get the patient (should fail)
            with pytest.raises(OpenDentalAPIError):
                self.client.patients.get(created_patient.id)
            print("Confirmed patient was deleted")
                
        except OpenDentalAPIError as e:
            print(f"API Error during create/update/delete operation: {e}")
            print(f"Status code: {e.status_code}")
            print(f"Response data: {e.response_data}")
            
            # If we created a patient but failed later, try to clean up
            if 'created_patient' in locals():
                try:
                    print(f"Attempting to clean up patient ID {created_patient.id}...")
                    self.client.patients.delete(created_patient.id)
                except:
                    pass  # Cleanup failed, but that's ok
            raise
        except Exception as e:
            print(f"Unexpected error during create/update/delete operation: {e}")
            raise
    
    def test_patient_helper_methods(self):
        """Test helper methods like get_by_email, get_by_phone, get_by_name."""
        try:
            print("\n=== Testing Patient Helper Methods ===")
            
            # Get a sample patient first
            patients_list = self.client.patients.list(page=1, per_page=5)
            
            if not patients_list.patients:
                pytest.skip("No patients available to test helper methods")
            
            # Find a patient with email
            patient_with_email = None
            for patient in patients_list.patients:
                if patient.email:
                    patient_with_email = patient
                    break
            
            if patient_with_email:
                print(f"Testing get_by_email with: {patient_with_email.email}")
                email_results = self.client.patients.get_by_email(patient_with_email.email)
                
                assert isinstance(email_results, list)
                print(f"Found {len(email_results)} patients with email {patient_with_email.email}")
                
                # Verify our patient is in the results
                found_patient = any(p.id == patient_with_email.id for p in email_results)
                assert found_patient
            
            # Test get_by_name
            sample_patient = patients_list.patients[0]
            if sample_patient.last_name:
                print(f"Testing get_by_name with last_name: {sample_patient.last_name}")
                name_results = self.client.patients.get_by_name(last_name=sample_patient.last_name)
                
                assert isinstance(name_results, list)
                print(f"Found {len(name_results)} patients with last name {sample_patient.last_name}")
                
        except OpenDentalAPIError as e:
            print(f"API Error during helper methods test: {e}")
            print(f"Status code: {e.status_code}")
            print(f"Response data: {e.response_data}")
            raise
        except Exception as e:
            print(f"Unexpected error during helper methods test: {e}")
            raise
    
    def test_error_handling(self):
        """Test error handling with invalid requests."""
        try:
            print("\n=== Testing Error Handling ===")
            
            # Test getting a non-existent patient
            print("Testing get with invalid patient ID...")
            with pytest.raises(OpenDentalAPIError) as exc_info:
                self.client.patients.get(999999999)  # Very unlikely to exist
            
            error = exc_info.value
            print(f"Got expected error: {error}")
            print(f"Status code: {error.status_code}")
            
        except Exception as e:
            print(f"Unexpected error during error handling test: {e}")
            raise


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v", "-s"])