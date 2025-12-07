"""
Test script for Clinic API endpoints on PRODUCTION
Run with: python test_clinic_production.py
"""
import requests
import json

# Configuration
BASE_URL = "https://fammo.ai/api/v1"
TEST_EMAIL = "ibadoyos@gmail.com"
TEST_PASSWORD = "Ali5522340731"

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_result(test_name, success, details=""):
    status = f"{GREEN}✓ PASS{RESET}" if success else f"{RED}✗ FAIL{RESET}"
    print(f"{status} {test_name}")
    if details:
        print(f"  {YELLOW}{details}{RESET}")

def get_auth_token():
    """Get JWT token for authentication"""
    print(f"{YELLOW}Attempting to authenticate with {TEST_EMAIL}...{RESET}")
    response = requests.post(f"{BASE_URL}/auth/token/", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    if response.status_code == 200:
        return response.json()["access"]
    else:
        print(f"{RED}Authentication failed: {response.status_code}{RESET}")
        print(f"{RED}Response: {response.text}{RESET}")
    return None

def test_list_clinics():
    """Test GET /api/v1/clinics/"""
    response = requests.get(f"{BASE_URL}/clinics/")
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    if success:
        data = response.json()
        if isinstance(data, list):
            details += f", Found {len(data)} active clinics"
        else:
            details += f", Response: {data}"
    else:
        details += f", Error: {response.text[:200]}"
    print_result("List All Active Clinics", success, details)
    return success

def test_list_all_clinics():
    """Test GET /api/v1/clinics/?show_all=true"""
    response = requests.get(f"{BASE_URL}/clinics/?show_all=true")
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    if success:
        data = response.json()
        if isinstance(data, list):
            details += f", Found {len(data)} total clinics (including pending)"
        else:
            details += f", Response: {data}"
    else:
        details += f", Error: {response.text[:200]}"
    print_result("List All Clinics (show_all=true)", success, details)
    return success

def test_my_clinic(token):
    """Test GET /api/v1/clinics/my/"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/clinics/my/", headers=headers)
    success = response.status_code in [200, 404]
    details = f"Status: {response.status_code}"
    
    if response.status_code == 200:
        data = response.json()
        details += f", Clinic: {data.get('name', 'N/A')}"
        details += f", ID: {data.get('id', 'N/A')}"
        details += f", Email Confirmed: {data.get('email_confirmed', False)}"
        details += f", Admin Approved: {data.get('admin_approved', False)}"
        return success, data
    elif response.status_code == 404:
        details += ", No clinic registered"
        print_result("Get My Clinic", success, details)
        return success, None
    else:
        details += f", Error: {response.text[:200]}"
        print_result("Get My Clinic", success, details)
        return success, None
    
    print_result("Get My Clinic", success, details)
    return success, None

def test_clinic_detail(clinic_id):
    """Test GET /api/v1/clinics/<id>/"""
    if not clinic_id:
        print_result("Get Clinic Detail", False, "No clinic_id provided")
        return False
    
    response = requests.get(f"{BASE_URL}/clinics/{clinic_id}/")
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    
    if success:
        data = response.json()
        details += f", Clinic: {data.get('name', 'N/A')}"
        details += f", City: {data.get('city', 'N/A')}"
        details += f", Email Confirmed: {data.get('email_confirmed', False)}"
        details += f", Admin Approved: {data.get('admin_approved', False)}"
        details += f", Lat: {data.get('latitude', 'N/A')}, Long: {data.get('longitude', 'N/A')}"
        
        # Show working hours
        wh = data.get('working_hours_schedule', [])
        if wh:
            details += f", Working Hours: {len(wh)} days configured"
        
        # Show vet profile
        vet = data.get('vet_profile')
        if vet:
            details += f", Vet: {vet.get('vet_name', 'N/A')}"
        
        # Show referral code
        ref_code = data.get('active_referral_code')
        if ref_code:
            details += f", Referral Code: {ref_code}"
            
        print(f"\n{BLUE}Full Clinic Data:{RESET}")
        print(json.dumps(data, indent=2))
        print()
    else:
        details += f", Error: {response.text[:200]}"
    
    print_result("Get Clinic Detail", success, details)
    return success

def test_working_hours(clinic_id):
    """Test GET /api/v1/clinics/<id>/working-hours/"""
    if not clinic_id:
        print_result("Get Working Hours", False, "No clinic_id provided")
        return False
    
    response = requests.get(f"{BASE_URL}/clinics/{clinic_id}/working-hours/")
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    
    if success:
        data = response.json()
        if isinstance(data, list):
            details += f", Found {len(data)} days configured"
            if data:
                print(f"\n{BLUE}Working Hours:{RESET}")
                for day in data:
                    print(f"  {day.get('day_name', 'N/A')}: ", end="")
                    if day.get('is_closed'):
                        print("Closed")
                    else:
                        print(f"{day.get('open_time', 'N/A')} - {day.get('close_time', 'N/A')}")
                print()
    else:
        details += f", Error: {response.text[:200]}"
    
    print_result("Get Working Hours", success, details)
    return success

def test_vet_profile(clinic_id):
    """Test GET /api/v1/clinics/<id>/vet-profile/"""
    if not clinic_id:
        print_result("Get Vet Profile", False, "No clinic_id provided")
        return False
    
    response = requests.get(f"{BASE_URL}/clinics/{clinic_id}/vet-profile/")
    success = response.status_code in [200, 404]
    details = f"Status: {response.status_code}"
    
    if response.status_code == 200:
        data = response.json()
        details += f", Vet: {data.get('vet_name', 'N/A')}"
        details += f", Degrees: {data.get('degrees', 'N/A')}"
        details += f", Certifications: {data.get('certifications', 'N/A')}"
    elif response.status_code == 404:
        details += ", No vet profile found"
    else:
        details += f", Error: {response.text[:200]}"
    
    print_result("Get Vet Profile", success, details)
    return success

def test_search_clinics():
    """Test POST /api/v1/clinics/search/"""
    search_data = {
        "search": "clinic"
    }
    response = requests.post(f"{BASE_URL}/clinics/search/", json=search_data)
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    
    if success:
        data = response.json()
        details += f", Found {data.get('count', 0)} clinics matching 'clinic'"
    else:
        details += f", Error: {response.text[:200]}"
    
    print_result("Search Clinics", success, details)
    return success

def test_update_clinic(token, clinic_id):
    """Test PATCH /api/v1/clinics/<id>/"""
    if not clinic_id:
        print_result("Update Clinic", False, "No clinic_id provided")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "bio": "Updated via API test - Production deployment test"
    }
    response = requests.patch(
        f"{BASE_URL}/clinics/{clinic_id}/",
        json=update_data,
        headers=headers
    )
    success = response.status_code == 200
    details = f"Status: {response.status_code}"
    
    if success:
        data = response.json()
        details += f", Updated clinic: {data.get('name', 'N/A')}"
    else:
        details += f", Error: {response.text[:200]}"
    
    print_result("Update Clinic", success, details)
    return success

def main():
    print(f"\n{BLUE}{'='*60}")
    print(f"Testing Clinic API Endpoints - PRODUCTION")
    print(f"Server: {BASE_URL}")
    print(f"{'='*60}{RESET}\n")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print(f"{RED}Failed to get authentication token. Cannot proceed.{RESET}")
        return
    print(f"{GREEN}✓ Authentication successful{RESET}\n")
    
    # Track results
    results = []
    clinic_data = None
    
    # Test endpoints
    print(f"{BLUE}{'='*60}")
    print(f"Testing Clinic Endpoints")
    print(f"{'='*60}{RESET}\n")
    
    results.append(test_list_clinics())
    results.append(test_list_all_clinics())
    
    success, clinic_data = test_my_clinic(token)
    results.append(success)
    
    clinic_id = clinic_data.get('id') if clinic_data else None
    
    if clinic_id:
        print(f"\n{YELLOW}Using clinic ID {clinic_id} for remaining tests{RESET}\n")
        results.append(test_clinic_detail(clinic_id))
        results.append(test_working_hours(clinic_id))
        results.append(test_vet_profile(clinic_id))
        results.append(test_update_clinic(token, clinic_id))
    else:
        print(f"\n{YELLOW}No clinic found for this user. Skipping detail tests.{RESET}\n")
    
    results.append(test_search_clinics())
    
    # Summary
    print(f"\n{BLUE}{'='*60}")
    print(f"Test Summary")
    print(f"{'='*60}{RESET}")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    if passed == total:
        print(f"{GREEN}✓ All tests passed! ({passed}/{total}){RESET}")
    else:
        print(f"{YELLOW}⚠ {passed}/{total} tests passed ({percentage:.1f}%){RESET}")
    
    print()

if __name__ == "__main__":
    main()
