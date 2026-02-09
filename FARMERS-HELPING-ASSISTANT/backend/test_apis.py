import requests
import json

def test_health():
    print("🧪 Testing Health Check...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print(f"✅ Health: {response.json()}")
    else:
        print(f"❌ Health Check Failed: {response.status_code}")

def test_crop_recommendation():
    print("\n🧪 Testing Crop Recommendation...")
    test_data = {
        "state": "Karnataka",
        "district": "Bangalore Urban", 
        "soil_type": "Loamy",
        "season": "Kharif",
        "irrigation_source": "Canal"
    }
    
    response = requests.post("http://localhost:8000/api/crops/recommend", json=test_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Crop Recommendation: Found {len(data.get('recommended_crops', []))} crops")
        
        # 🔽 FIXED: Use 'crop_name' instead of 'crop'
        top = data.get('top_recommendation')
        if top:
            print(f"   🥇 {top.get('crop_name', 'Unknown')} - {top.get('match_score', 0)}%")
        
        # Show all recommendations
        for crop in data.get('recommended_crops', []):
            print(f"   🌱 {crop.get('crop_name', 'Unknown')} - {crop.get('match_score', 0)}%")
            
    else:
        print(f"❌ Crop Recommendation Failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_yield_prediction():
    print("\n🧪 Testing Yield Prediction...")
    test_data = {
        "state": "Karnataka",
        "district": "Bangalore Urban",
        "crop_name": "Tomato", 
        "soil_type": "Loamy",
        "season": "Kharif",
        "irrigation_source": "Canal"
    }
    
    response = requests.post("http://localhost:8000/api/yield/predict", json=test_data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Yield Prediction: {data.get('predicted_yield', 'N/A')}")
        print(f"   Confidence: {data.get('confidence', 'N/A')}")
        print(f"   Stored in DB: {data.get('stored_in_db', False)}")
    else:
        print(f"❌ Yield Prediction Failed: {response.status_code}")
        print(f"   Error: {response.text}")

def test_disease_detection():
    print("\n🧪 Testing Disease Detection...")
    
    # Note: This requires an actual image file
    # For now, we'll skip or use a mock
    print("   ⚠️ Disease detection requires image upload - skipping for now")
    
    # If you want to test with a sample image, uncomment below:
    """
    files = {
        'image': ('test.jpg', open('test.jpg', 'rb'), 'image/jpeg'),
    }
    data = {
        'crop_type': 'tomato',
        'user_id': 'test_user'
    }
    
    response = requests.post("http://localhost:8000/api/disease/detect", files=files, data=data)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Disease Detection: {data.get('disease_name', 'N/A')}")
        print(f"   Confidence: {data.get('confidence', 'N/A')}")
    else:
        print(f"❌ Disease Detection Failed: {response.status_code}")
    """

def test_user_auth():
    print("\n🧪 Testing User Authentication...")
    
    # Use a unique email to avoid duplicate errors
    import random
    random_id = random.randint(1000, 9999)
    
    # Test registration
    reg_data = {
        "name": "Test User",
        "email": f"test{random_id}@example.com",  # Unique email
        "phone": "9876543210",
        "password": "test123",
        "language": "en"
    }
    
    print(f"   📧 Registering with email: {reg_data['email']}")
    
    try:
        response = requests.post("http://localhost:8000/api/auth/signup", json=reg_data)
        print(f"   📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ User Registration: Success")
            user_data = response.json()
            print(f"   👤 User ID: {user_data.get('user_id', 'N/A')}")
        else:
            print(f"❌ User Registration Failed: {response.status_code}")
            print(f"   🔍 Full Response: {response.text}")
            
            # Try to get more detailed error
            try:
                error_detail = response.json()
                print(f"   🚨 Error Details: {error_detail}")
            except:
                print("   🚨 Could not parse error response")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("🚀 Testing AgriSmart APIs...")
    
    try:
        test_health()
        test_crop_recommendation() 
        test_yield_prediction()
        test_disease_detection()
        test_user_auth()
        
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on port 8000!")
    except Exception as e:
        print(f"❌ Test error: {e}")