#!/usr/bin/env python3
"""
OmniHealth Guardian OpenClaw Skills API Testing
Tests all 6 OpenClaw skill endpoints and verifies functionality
"""

import requests
import json
import sys
import time
from datetime import datetime

# Use the public frontend URL for testing
BASE_URL = "https://omni-health-ai.preview.emergentagent.com"

class OpenClawAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.tests_run = 0
        self.tests_passed = 0
        self.results = []

    def log_test(self, name, status, details=None, error=None):
        """Log test result"""
        self.tests_run += 1
        if status == "PASS":
            self.tests_passed += 1
            print(f"✅ {name}")
        else:
            print(f"❌ {name} - {error}")
        
        result = {
            "test": name,
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)

    def test_api_endpoint(self, method, endpoint, expected_status=200, data=None, test_name=None):
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if not test_name:
            test_name = f"{method} {endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            else:
                self.log_test(test_name, "FAIL", error=f"Unsupported method: {method}")
                return False, None

            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_test(test_name, "PASS", response_data)
            else:
                self.log_test(test_name, "FAIL", 
                             error=f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}")
            
            return success, response_data

        except requests.exceptions.RequestException as e:
            self.log_test(test_name, "FAIL", error=f"Request failed: {str(e)}")
            return False, None
        except Exception as e:
            self.log_test(test_name, "FAIL", error=f"Unexpected error: {str(e)}")
            return False, None

    def get_sample_patient_id(self):
        """Get a sample patient ID for testing"""
        print("🔍 Getting sample patient ID...")
        success, data = self.test_api_endpoint('GET', '/api/patients', test_name="Get Patients List")
        
        if success and data and len(data) > 0:
            patient_id = data[0].get('id')
            print(f"📋 Using patient ID: {patient_id} ({data[0].get('name', 'Unknown')})")
            return patient_id
        else:
            print("❌ Could not get patient ID from /api/patients")
            return None

    def test_openclaw_skills(self):
        """Test OpenClaw Skills Endpoint"""
        print("\n🧪 Testing OpenClaw Skills Endpoint...")
        success, data = self.test_api_endpoint('GET', '/api/openclaw/skills', 
                                              test_name="GET /api/openclaw/skills")
        
        if success and data:
            skills = data.get('skills', [])
            if len(skills) == 4:
                self.log_test("Skills Count Validation", "PASS", 
                             details=f"Found {len(skills)} skills as expected")
                
                # Check if all required skills are present
                skill_names = [skill.get('name', '') for skill in skills]
                expected_skills = [
                    'critical_condition_monitor',
                    'ai_diet_suggestion', 
                    'realtime_feedback',
                    'daily_progress_tracker'
                ]
                
                missing_skills = [skill for skill in expected_skills if skill not in skill_names]
                if not missing_skills:
                    self.log_test("Required Skills Validation", "PASS",
                                 details="All 4 required skills found")
                else:
                    self.log_test("Required Skills Validation", "FAIL",
                                 error=f"Missing skills: {missing_skills}")
            else:
                self.log_test("Skills Count Validation", "FAIL", 
                             error=f"Expected 4 skills, got {len(skills)}")
        
        return success

    def test_individual_skills(self, patient_id):
        """Test individual OpenClaw skill endpoints"""
        print(f"\n🧪 Testing Individual Skills for Patient: {patient_id}")
        
        skills_to_test = [
            ('critical-monitor', 'Critical Monitor Skill'),
            ('diet-suggestion', 'Diet Suggestion Skill'),
            ('realtime-feedback', 'Real-time Feedback Skill'), 
            ('daily-progress', 'Daily Progress Skill')
        ]
        
        individual_results = []
        
        for skill_id, skill_name in skills_to_test:
            endpoint = f'/api/openclaw/skill/{skill_id}/{patient_id}'
            print(f"  🔬 Testing {skill_name}...")
            
            success, data = self.test_api_endpoint('POST', endpoint, 
                                                  test_name=f"POST {endpoint}")
            
            individual_results.append({
                'skill': skill_name,
                'success': success,
                'data': data
            })
            
            if success and data:
                # Validate response structure
                if 'skill' in data and 'status' in data:
                    self.log_test(f"{skill_name} Response Structure", "PASS")
                    
                    # Special validation for each skill type
                    if skill_id == 'critical-monitor':
                        if 'vitals' in data:
                            self.log_test(f"{skill_name} Vitals Data", "PASS")
                        else:
                            self.log_test(f"{skill_name} Vitals Data", "FAIL", 
                                         error="No vitals data in response")
                    
                    elif skill_id == 'diet-suggestion':
                        if 'diet_plan' in data:
                            self.log_test(f"{skill_name} Diet Plan", "PASS")
                        else:
                            self.log_test(f"{skill_name} Diet Plan", "FAIL",
                                         error="No diet plan in response")
                    
                    elif skill_id == 'realtime-feedback':
                        if 'feedback' in data:
                            self.log_test(f"{skill_name} Feedback Data", "PASS")
                        else:
                            self.log_test(f"{skill_name} Feedback Data", "FAIL",
                                         error="No feedback data in response")
                    
                    elif skill_id == 'daily-progress':
                        if 'overall_health_score' in data:
                            self.log_test(f"{skill_name} Health Score", "PASS")
                        else:
                            self.log_test(f"{skill_name} Health Score", "FAIL",
                                         error="No health score in response")
                else:
                    self.log_test(f"{skill_name} Response Structure", "FAIL",
                                 error="Missing required 'skill' or 'status' fields")
            
            # Small delay between skill tests
            time.sleep(0.5)
        
        return individual_results

    def test_run_all_skills(self, patient_id):
        """Test Run All Skills endpoint"""
        print(f"\n🧪 Testing Run All Skills for Patient: {patient_id}")
        
        endpoint = f'/api/openclaw/run-all/{patient_id}'
        success, data = self.test_api_endpoint('POST', endpoint,
                                              test_name=f"POST {endpoint}")
        
        if success and data:
            # Validate response structure
            if 'skills_executed' in data:
                skills_executed = data['skills_executed']
                if len(skills_executed) == 4:
                    self.log_test("Run All Skills - Count", "PASS",
                                 details=f"Executed {len(skills_executed)} skills")
                else:
                    self.log_test("Run All Skills - Count", "FAIL",
                                 error=f"Expected 4 skills, executed {len(skills_executed)}")
                    
                # Check if each skill has proper result structure
                skill_validation_passed = True
                for skill_result in skills_executed:
                    if not ('skill' in skill_result and 'result' in skill_result):
                        skill_validation_passed = False
                        break
                
                if skill_validation_passed:
                    self.log_test("Run All Skills - Structure", "PASS")
                else:
                    self.log_test("Run All Skills - Structure", "FAIL",
                                 error="Invalid skill result structure")
            else:
                self.log_test("Run All Skills - Response", "FAIL",
                             error="Missing 'skills_executed' in response")
        
        return success, data

    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting OmniHealth Guardian OpenClaw Skills API Testing")
        print("=" * 60)
        
        # Test 1: OpenClaw Skills endpoint
        if not self.test_openclaw_skills():
            print("❌ Skills endpoint test failed, stopping tests")
            return self.generate_summary()
        
        # Test 2: Get patient ID
        patient_id = self.get_sample_patient_id()
        if not patient_id:
            print("❌ Could not get patient ID, stopping tests")
            return self.generate_summary()
        
        # Test 3: Individual skills
        individual_results = self.test_individual_skills(patient_id)
        
        # Test 4: Run all skills
        run_all_success, run_all_data = self.test_run_all_skills(patient_id)
        
        return self.generate_summary()

    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print(f"📊 TEST SUMMARY")
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%" if self.tests_run > 0 else "0%")
        
        # Show failed tests
        failed_tests = [r for r in self.results if r['status'] == 'FAIL']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['error']}")
        
        return {
            'total_tests': self.tests_run,
            'passed_tests': self.tests_passed,
            'failed_tests': self.tests_run - self.tests_passed,
            'success_rate': (self.tests_passed/self.tests_run)*100 if self.tests_run > 0 else 0,
            'results': self.results,
            'summary': f"OpenClaw Skills Testing: {self.tests_passed}/{self.tests_run} tests passed"
        }


def main():
    tester = OpenClawAPITester()
    try:
        results = tester.run_all_tests()
        return 0 if results['failed_tests'] == 0 else 1
    except Exception as e:
        print(f"❌ Testing failed with error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)