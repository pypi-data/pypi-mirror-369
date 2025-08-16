# Open Dental Python SDK

A comprehensive, domain-driven Python SDK for the Open Dental API that provides type-safe access to all Open Dental resources.

**✅ FULLY TESTED AND WORKING** - Successfully tested with real Open Dental API

## Features

✅ **Production Ready** - Integration tested with real Open Dental API  
✅ **Type Safe** - Built with Pydantic models for full type safety  
✅ **42 Resources** - Complete coverage of all Open Dental API endpoints  
✅ **Simple & Clean** - Intuitive, Pythonic interface  
✅ **Error Handling** - Comprehensive error handling with detailed messages  
✅ **Real Data Support** - Handles actual Open Dental API response formats  

## Installation

```bash
pip install -e .
```

Or with uv:

```bash
uv pip install -e .
```

## Quick Start

```python
from opendental import OpenDentalClient

# Initialize client (uses environment variables)
client = OpenDentalClient()

# List all patients
patients = client.patients.list()
print(f"Found {patients.total} patients")

# Get specific patient
patient = client.patients.get(123)
print(f"Patient: {patient.first_name} {patient.last_name}")
print(f"Status: {patient.patient_status}")
print(f"Provider: {patient.primary_provider_abbr}")

# Search patients (client-side filtering)
from opendental.resources.patients.models import PatientSearchRequest

search_results = client.patients.search(
    PatientSearchRequest(last_name="Smith")
)
print(f"Found {len(search_results.patients)} patients named Smith")

# Limited results
recent_patients = client.patients.list(limit=5)
```

## Authentication

Set your Open Dental API keys as environment variables:

```bash
export OPENDENTAL_DEVELOPER_KEY="your_developer_key"
export OPENDENTAL_CUSTOMER_KEY="your_customer_key"
```

Or create a `.env` file:

```bash
OPENDENTAL_DEVELOPER_KEY=your_developer_key
OPENDENTAL_CUSTOMER_KEY=your_customer_key
```

Or pass them directly:

```python
client = OpenDentalClient(
    developer_key="your_developer_key",
    customer_key="your_customer_key"
)
```

## Available Resources

The SDK provides clients for all 42 Open Dental API resources:

### Core Resources
- `client.patients` - Patient management ✅ **Tested**
- `client.appointments` - Appointment scheduling  
- `client.providers` - Healthcare providers
- `client.procedures` - Medical procedures
- `client.payments` - Payment processing

### Clinical Resources
- `client.medications` - Medication management
- `client.allergies` - Allergy tracking
- `client.diseases` - Disease management
- `client.lab_cases` - Laboratory cases

### Financial Resources  
- `client.claims` - Insurance claims
- `client.adjustments` - Account adjustments
- `client.insurance_plans` - Insurance plan management
- `client.pay_plans` - Payment plans

### Administrative Resources
- `client.employees` - Staff management
- `client.users` - User accounts
- `client.clinics` - Clinic locations
- `client.operatories` - Operatory management

### System Resources
- `client.definitions` - System definitions
- `client.communications` - Communication logs
- `client.documents` - Document management
- `client.computers` - Computer tracking

*...and 25+ more resources!*

## Real-World Usage

This SDK has been tested with actual Open Dental systems and handles real data correctly:

```python
# Example with real data types
patient = client.patients.get(11)

# Returns actual data like:
# patient.first_name = "Allen"
# patient.last_name = "Allowed" 
# patient.patient_status = "Patient"  # String, not integer
# patient.gender = "Male"             # String, not integer
# patient.billing_type = "Standard"   # String, not integer
# patient.birth_date = date(1980, 6, 5)
# patient.primary_provider_abbr = "DOC1"
```

## API Limitations & SDK Solutions

The Open Dental API has some limitations that this SDK handles gracefully:

### No Server-Side Search
❌ **API Limitation**: No `/patients/search` endpoint  
✅ **SDK Solution**: Client-side filtering with full search functionality

```python
# This works despite API limitations
search_results = client.patients.search(
    PatientSearchRequest(
        last_name="Smith",
        email="john@example.com"
    )
)
```

### No Pagination 
❌ **API Limitation**: No `page`/`per_page` parameters  
✅ **SDK Solution**: Client-side limiting and all results returned

```python
# Returns all patients, limited client-side
patients = client.patients.list(limit=10)
```

### String-Based Enums
❌ **API Limitation**: Returns "Patient" instead of status codes  
✅ **SDK Solution**: Models handle string values correctly

## Error Handling

```python
from opendental import OpenDentalClient
from opendental.exceptions import OpenDentalAPIError

client = OpenDentalClient()

try:
    patient = client.patients.get(999999)
except OpenDentalAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response_data}")
```

## Testing

Run the integration tests with your API keys:

```bash
# Set up environment
export OPENDENTAL_DEVELOPER_KEY="your_key"
export OPENDENTAL_CUSTOMER_KEY="your_key"

# Run integration tests
python run_integration_tests.py

# Or run basic example
python examples/basic_usage.py

# Or run comprehensive demo
python demo_sdk.py
```

## Development

### Setup

```bash
# Clone and install
git clone <repository>
cd python
uv pip install -e ".[dev]"

# Run tests
python final_integration_test.py
```

### Architecture

The SDK follows domain-driven design:

```
src/opendental/
├── base/              # Base classes
│   ├── models.py      # BaseModel with Pydantic config
│   └── resource.py    # BaseResource with HTTP methods
├── resources/         # 42 resource modules
│   ├── patients/      # Patient domain
│   │   ├── models.py  # Patient, CreatePatientRequest, etc.
│   │   ├── client.py  # PatientsClient
│   │   └── types.py   # Patient-specific enums
│   └── ...           # 41 other resources
├── client.py          # Main OpenDentalClient
└── exceptions.py      # SDK exceptions
```

### Key Design Principles

1. **Keep It Simple** - Direct API wrapper with minimal abstraction
2. **Domain Ownership** - Each resource owns its models
3. **Type Safety** - Pydantic models throughout
4. **Real Data First** - Built for actual API responses, not documentation

## HIPAA Compliance

⚠️ **Important**: This SDK handles sensitive patient data. Ensure you:

- Have a Business Associate Agreement (BAA) with Open Dental
- Follow all HIPAA compliance requirements
- Implement proper security measures in your applications
- Use secure connections and proper authentication

## License

MIT License - see LICENSE file for details.

## Support

- Integration tested and working with Open Dental API
- See `examples/` directory for working code samples
- Run `python demo_sdk.py` to verify functionality
- Check error messages for detailed troubleshooting information