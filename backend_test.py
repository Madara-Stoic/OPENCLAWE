#!/usr/bin/env python3

import requests
import json
import sys
from datetime import datetime
from typing import List, Dict, Any

class OmniHealthAPITester:
    def __init__(self, base_url="https://omni-health-ai.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name: str, success: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {details}")
        
        self.test_results.append({
            'name': name,
            'success': success,
            'details': details
        })

    def test_api_endpoint(self, method: str, endpoint: str, expected_status: int = 200, 
                         data: Dict = None, test_name: str = None) -> tuple:
        """Generic API test method"""
        if test_name is None:
            test_name = f"{method} {endpoint}"
        
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            else:
                response = self.session.request(method, url, json=data)
            
            success = response.status_code == expected_status
            response_data = {}
            
            if success:
                try:
                    response_data = response.json()
                except:
                    response_data = {"raw_response": response.text}
                self.log_test(test_name, True)
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details.get('detail', '')}"
                except:
                    error_msg += f" - {response.text[:100]}"
                self.log_test(test_name, False, error_msg)
            
            return success, response_data
            
        except Exception as e:
            self.log_test(test_name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test API root endpoint"""
        return self.test_api_endpoint('GET', '/', test_name="API Root Endpoint")

    def test_auth_login(self):
        """Test authentication login"""
        login_data = {
            'email': 'test.patient@omnihealth.io',
            'name': 'Test Patient',
            'role': 'patient'
        }
        success, data = self.test_api_endpoint('POST', '/auth/login', data=login_data, 
                                             test_name="Auth Login")
        
        if success and data.get('user') and data.get('wallet'):
            self.log_test("Auth Response Structure", True)
            return True, data
        elif success:
            self.log_test("Auth Response Structure", False, "Missing user or wallet data")
        
        return success, data

    def test_patients_endpoints(self):
        """Test patient-related endpoints"""
        # Get all patients
        success, patients_data = self.test_api_endpoint('GET', '/patients', 
                                                       test_name="Get All Patients")
        
        if success and isinstance(patients_data, list):
            patient_count = len(patients_data)
            self.log_test(f"Patients Count ({patient_count})", patient_count >= 10, 
                         f"Expected at least 10, got {patient_count}")
            
            if patient_count > 0:
                # Test individual patient endpoint
                patient_id = patients_data[0]['id']
                self.test_api_endpoint('GET', f'/patients/{patient_id}', 
                                     test_name="Get Individual Patient")
                
                # Test patient readings
                self.test_api_endpoint('GET', f'/patients/{patient_id}/readings', 
                                     test_name="Get Patient Readings")
                
                # Test patient alerts
                self.test_api_endpoint('GET', f'/patients/{patient_id}/alerts', 
                                     test_name="Get Patient Alerts")
                return patient_id
        
        return None

    def test_doctors_endpoints(self):
        """Test doctor-related endpoints"""
        # Get all doctors
        success, doctors_data = self.test_api_endpoint('GET', '/doctors', 
                                                      test_name="Get All Doctors")
        
        if success and isinstance(doctors_data, list):
            doctor_count = len(doctors_data)
            self.log_test(f"Doctors Count ({doctor_count})", doctor_count >= 20, 
                         f"Expected at least 20, got {doctor_count}")
            
            if doctor_count > 0:
                # Test individual doctor endpoint
                doctor_id = doctors_data[0]['id']
                self.test_api_endpoint('GET', f'/doctors/{doctor_id}', 
                                     test_name="Get Individual Doctor")
                
                # Test doctor patients
                self.test_api_endpoint('GET', f'/doctors/{doctor_id}/patients', 
                                     test_name="Get Doctor Patients")
                return doctor_id
        
        return None

    def test_hospitals_endpoints(self):
        """Test hospital-related endpoints"""
        # Get all hospitals
        success, hospitals_data = self.test_api_endpoint('GET', '/hospitals', 
                                                        test_name="Get All Hospitals")
        
        if success and isinstance(hospitals_data, list):
            hospital_count = len(hospitals_data)
            self.log_test(f"Hospitals Count ({hospital_count})", hospital_count >= 30, 
                         f"Expected at least 30, got {hospital_count}")
            
            if hospital_count > 0:
                # Test individual hospital endpoint
                hospital_id = hospitals_data[0]['id']
                self.test_api_endpoint('GET', f'/hospitals/{hospital_id}', 
                                     test_name="Get Individual Hospital")
                
                # Test hospital stats
                self.test_api_endpoint('GET', f'/hospitals/{hospital_id}/stats', 
                                     test_name="Get Hospital Stats")
        
        return success

    def test_telemetry_endpoints(self):
        """Test telemetry endpoints"""
        # Get live telemetry
        success, telemetry_data = self.test_api_endpoint('GET', '/telemetry/live', 
                                                        test_name="Get Live Telemetry")
        
        if success and isinstance(telemetry_data, list):
            telemetry_count = len(telemetry_data)
            self.log_test(f"Live Telemetry Data ({telemetry_count})", telemetry_count > 0, 
                         f"Expected > 0 readings, got {telemetry_count}")
        
        # Record new reading
        self.test_api_endpoint('POST', '/telemetry/reading', test_name="Record New Reading")
        
        return success

    def test_alerts_endpoints(self):
        """Test alerts endpoints"""
        # Get all alerts
        self.test_api_endpoint('GET', '/alerts', test_name="Get All Alerts")
        
        # Get recent alerts
        self.test_api_endpoint('GET', '/alerts/recent', test_name="Get Recent Alerts")

    def test_diet_endpoints(self, patient_id: str):
        """Test AI diet generation endpoints"""
        if not patient_id:
            self.log_test("Diet Plan Generation", False, "No patient ID available")
            return
        
        # Generate diet plan
        success, diet_data = self.test_api_endpoint('POST', f'/diet/generate?patient_id={patient_id}', 
                                                   test_name="Generate AI Diet Plan")
        
        if success and diet_data.get('plan'):
            self.log_test("Diet Plan Content", True)
        elif success:
            self.log_test("Diet Plan Content", False, "No plan content in response")
        
        # Get patient diet plans
        self.test_api_endpoint('GET', f'/diet/{patient_id}', test_name="Get Patient Diet Plans")

    def test_moltbot_endpoints(self):
        """Test Moltbot activity endpoints"""
        # Get activities
        success, activities_data = self.test_api_endpoint('GET', '/moltbot/activities', 
                                                         test_name="Get Moltbot Activities")
        
        # Get stats
        self.test_api_endpoint('GET', '/moltbot/stats', test_name="Get Moltbot Stats")

    def test_dashboard_endpoints(self, patient_id: str, doctor_id: str):
        """Test dashboard endpoints"""
        # Patient dashboard
        if patient_id:
            success, patient_dash = self.test_api_endpoint('GET', f'/dashboard/patient/{patient_id}', 
                                                          test_name="Patient Dashboard")
            if success and patient_dash.get('patient') and patient_dash.get('current_reading'):
                self.log_test("Patient Dashboard Structure", True)
            elif success:
                self.log_test("Patient Dashboard Structure", False, "Missing required dashboard data")
        
        # Doctor dashboard
        if doctor_id:
            success, doctor_dash = self.test_api_endpoint('GET', f'/dashboard/doctor/{doctor_id}', 
                                                         test_name="Doctor Dashboard")
            if success and doctor_dash.get('doctor') and 'patients' in doctor_dash:
                self.log_test("Doctor Dashboard Structure", True)
            elif success:
                self.log_test("Doctor Dashboard Structure", False, "Missing required dashboard data")
        
        # Organization dashboard
        success, org_dash = self.test_api_endpoint('GET', '/dashboard/organization', 
                                                  test_name="Organization Dashboard")
        if success and all(key in org_dash for key in ['total_patients', 'total_doctors', 'total_hospitals']):
            self.log_test("Organization Dashboard Structure", True)
        elif success:
            self.log_test("Organization Dashboard Structure", False, "Missing required dashboard stats")

    def test_blockchain_endpoints(self):
        """Test blockchain verification endpoint"""
        mock_tx_hash = "0x1234567890abcdef1234567890abcdef12345678"
        self.test_api_endpoint('GET', f'/blockchain/verify/{mock_tx_hash}', 
                              test_name="Blockchain Verification")

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🔍 Starting OmniHealth Guardian API Tests")
        print("=" * 50)
        
        # Test API connectivity
        self.test_root_endpoint()
        
        # Test authentication
        auth_success, auth_data = self.test_auth_login()
        
        # Test core data endpoints
        patient_id = self.test_patients_endpoints()
        doctor_id = self.test_doctors_endpoints()
        self.test_hospitals_endpoints()
        
        # Test real-time features
        self.test_telemetry_endpoints()
        self.test_alerts_endpoints()
        
        # Test AI features
        self.test_diet_endpoints(patient_id)
        self.test_moltbot_endpoints()
        
        # Test dashboards
        self.test_dashboard_endpoints(patient_id, doctor_id)
        
        # Test blockchain features
        self.test_blockchain_endpoints()
        
        # Summary
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All API tests passed!")
            return 0
        else:
            failed_tests = [t for t in self.test_results if not t['success']]
            print(f"❌ {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"  - {test['name']}: {test['details']}")
            return 1

def main():
    tester = OmniHealthAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())