import requests
import json
import base64
import sys
from pathlib import Path
from typing import Dict, Any

BASE_URL = "http://localhost:5000"
TEST_IMAGE_PATH = Path(__file__).parent.parent / "test_image.jpg"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test_result(name: str, passed: bool, details: str = ""):
    """Print test result with colors"""
    status = f"{Colors.GREEN}✓ PASSED{Colors.RESET}" if passed else f"{Colors.RED}✗ FAILED{Colors.RESET}"
    print(f"  {status} - {name}")
    if details:
        print(f"    {details}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test_result("Health Check", True, f"Status: {data.get('status')}")
            return True
        else:
            print_test_result("Health Check", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_test_result("Health Check", False, "Cannot connect to server")
        return False
    except Exception as e:
        print_test_result("Health Check", False, str(e))
        return False

def test_classes():
    """Test classes endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/classes", timeout=5)
        if response.status_code == 200:
            data = response.json()
            classes = data.get('classes', [])
            print_test_result("Classes Info", True, f"Found {len(classes)} classes")
            return True
        else:
            print_test_result("Classes Info", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Classes Info", False, str(e))
        return False

def test_predict():
    """Test prediction endpoint"""
    if not TEST_IMAGE_PATH.exists():
        print_test_result("Predict Image", False, f"Test image not found: {TEST_IMAGE_PATH}")
        return False
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'image': f}
            response = requests.post(f"{BASE_URL}/api/predict", files=files, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                pred_class = result.get('predicted_class', 'Unknown')
                confidence = result.get('confidence', 0)
                print_test_result(
                    "Predict Image", 
                    True, 
                    f"Class: {pred_class}, Confidence: {confidence:.4f}"
                )
                return True
            else:
                print_test_result("Predict Image", False, "API returned success=False")
                return False
        else:
            print_test_result("Predict Image", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Predict Image", False, str(e))
        return False

def test_predict_base64():
    """Test base64 prediction endpoint"""
    if not TEST_IMAGE_PATH.exists():
        print_test_result("Predict Base64", False, f"Test image not found: {TEST_IMAGE_PATH}")
        return False
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            image_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        data = {'image': image_base64}
        response = requests.post(
            f"{BASE_URL}/api/predict_base64",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result = data.get('result', {})
                pred_class = result.get('predicted_class', 'Unknown')
                confidence = result.get('confidence', 0)
                print_test_result(
                    "Predict Base64",
                    True,
                    f"Class: {pred_class}, Confidence: {confidence:.4f}"
                )
                return True
            else:
                print_test_result("Predict Base64", False, "API returned success=False")
                return False
        else:
            print_test_result("Predict Base64", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Predict Base64", False, str(e))
        return False

def test_invalid_file():
    """Test with invalid file type"""
    try:
        # Create a text file
        files = {'image': ('test.txt', b'This is not an image', 'text/plain')}
        response = requests.post(f"{BASE_URL}/api/predict", files=files, timeout=5)
        
        if response.status_code == 400:
            print_test_result("Invalid File", True, "Properly rejected invalid file")
            return True
        else:
            print_test_result("Invalid File", False, f"Expected 400, got {response.status_code}")
            return False
    except Exception as e:
        print_test_result("Invalid File", False, str(e))
        return False

def run_all_tests():
    """Run all test cases"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}🧪 Waste Classification API Tests{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"🌐 Server: {BASE_URL}")
    print()
    
    # Test cases
    tests = [
        ("Health Check", test_health),
        ("Classes Info", test_classes),
        ("Predict Image", test_predict),
        ("Predict Base64", test_predict_base64),
        ("Invalid File", test_invalid_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        if test_func():
            passed += 1
    
    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"📊 Summary: {Colors.GREEN}{passed}{Colors.RESET}/{total} tests passed")
    
    if passed == total:
        print(f"{Colors.GREEN}✅ All tests passed!{Colors.RESET}")
        return True
    else:
        print(f"{Colors.RED}❌ Some tests failed{Colors.RESET}")
        return False

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)