import os
import sys

# Add the parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print("🔧 Testing imports...")

try:
    # Try direct import
    from backend.app.ml_models.real_data_loader import real_data_loader
    from backend.app.ml_models.crop_model import crop_recommender
    from backend.app.ml_models.yield_model import yield_predictor
    print("✅ All imports successful!")
    
    # Test data loading
    print("\n📊 Testing data loading...")
    if real_data_loader.load_data():
        print("✅ Real data loaded!")
        
        yield_data = real_data_loader.preprocess_yield_data()
        crop_data = real_data_loader.preprocess_crop_data()
        
        print(f"📈 Yield records: {len(yield_data) if yield_data is not None else 0}")
        print(f"🌾 Crop records: {len(crop_data) if crop_data is not None else 0}")
        
        # Test model training
        print("\n🤖 Testing model training...")
        crop_success = crop_recommender.train_model()
        yield_success = yield_predictor.train_model()
        
        print(f"🌱 Crop model: {'✅ Trained' if crop_success else '❌ Failed'}")
        print(f"📈 Yield model: {'✅ Trained' if yield_success else '❌ Failed'}")
    else:
        print("❌ Data loading failed")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"📂 Current dir: {os.getcwd()}")
    print(f"🐍 Python path: {sys.path}")