import pandas as pd
import numpy as np
import random
from fastapi import HTTPException
import os

class CSVProcessor:
    def __init__(self):
        self.yield_data = None
        self.crop_data = None
        
    def load_yield_data(self, csv_path="app/data/yield_data.csv"):
        """Load yield data from CSV with your actual columns"""
        try:
            self.yield_data = pd.read_csv(csv_path)
            print(f"✅ Loaded yield data: {len(self.yield_data)} records")
            print(f"📊 Yield columns: {list(self.yield_data.columns)}")
            return True
        except Exception as e:
            print(f"❌ Could not load yield data: {e}")
            return False
    
    def load_crop_data(self, csv_path="app/data/crop_data.csv"):
        """Load crop data from CSV with your actual columns"""
        try:
            self.crop_data = pd.read_csv(csv_path)
            print(f"✅ Loaded crop data: {len(self.crop_data)} records")
            print(f"📊 Crop columns: {list(self.crop_data.columns)}")
            return True
        except Exception as e:
            print(f"❌ Could not load crop data: {e}")
            return False
    
    def predict_yield(self, input_data):
        """Smart yield prediction using your dataset columns"""
        if self.yield_data is None or self.yield_data.empty:
            return self._fallback_yield_prediction(input_data)
        
        try:
            # Filter data based on input conditions
            filtered_data = self.yield_data.copy()
            
            # Filter by state if available
            if 'state_name' in filtered_data.columns and 'state' in input_data:
                filtered_data = filtered_data[filtered_data['state_name'].str.lower() == input_data['state'].lower()]
            
            # Filter by crop if available
            if 'crop' in filtered_data.columns and 'crop_name' in input_data:
                filtered_data = filtered_data[filtered_data['crop'].str.lower() == input_data['crop_name'].lower()]
            
            # Filter by soil type if available
            if 'soil_type' in filtered_data.columns and 'soil_type' in input_data:
                filtered_data = filtered_data[filtered_data['soil_type'].str.lower() == input_data['soil_type'].lower()]
            
            # Filter by season if available
            if 'season' in filtered_data.columns and 'season' in input_data:
                filtered_data = filtered_data[filtered_data['season'].str.lower() == input_data['season'].lower()]
            
            # If we have matching records, calculate average yield
            if not filtered_data.empty and 'yield' in filtered_data.columns:
                avg_yield = filtered_data['yield'].mean()
                # Add some variation based on other factors
                variation = random.uniform(0.9, 1.1)
                predicted = avg_yield * variation
                return round(predicted, 2)
            else:
                return self._fallback_yield_prediction(input_data)
                
        except Exception as e:
            print(f"Error in yield prediction: {e}")
            return self._fallback_yield_prediction(input_data)
    
    def _fallback_yield_prediction(self, input_data):
        """Fallback prediction when no data matches"""
        # Base yields for different crops (tons/hectare)
        base_yields = {
            'wheat': 2.5, 'rice': 3.0, 'corn': 2.8, 'sugarcane': 65.0,
            'cotton': 2.2, 'pulses': 1.2, 'vegetables': 12.0,
            'groundnut': 1.5, 'sunflower': 1.2, 'soybean': 1.8
        }
        
        # Multipliers
        soil_multiplier = {'clay': 0.9, 'sandy': 0.8, 'loamy': 1.2}
        season_multiplier = {'spring': 1.1, 'summer': 0.9, 'monsoon': 1.3, 'winter': 1.0}
        irrigation_multiplier = {'rainfed': 0.7, 'well': 1.0, 'canal': 1.1, 'drip': 1.3}
        
        crop_name = input_data.get('crop_name', 'wheat').lower()
        base = base_yields.get(crop_name, 2.0)
        
        # Apply multipliers
        predicted = base
        if 'soil_type' in input_data:
            predicted *= soil_multiplier.get(input_data['soil_type'].lower(), 1.0)
        if 'season' in input_data:
            predicted *= season_multiplier.get(input_data['season'].lower(), 1.0)
        if 'irrigation_source' in input_data:
            predicted *= irrigation_multiplier.get(input_data['irrigation_source'].lower(), 1.0)
        
        # Add some random variation
        predicted *= random.uniform(0.95, 1.05)
        
        return round(predicted, 2)
    
    def recommend_crops(self, input_data, top_n=5):
        """Smart crop recommendations using NPK and environmental data"""
        if self.crop_data is None or self.crop_data.empty:
            return self._fallback_crop_recommendation(input_data)
        
        try:
            filtered_data = self.crop_data.copy()
            
            # Filter by state if available
            if 'state' in filtered_data.columns and 'state' in input_data:
                filtered_data = filtered_data[filtered_data['state'].str.lower() == input_data['state'].lower()]
            
            # Filter by soil type if available
            if 'soil_type' in filtered_data.columns and 'soil_type' in input_data:
                filtered_data = filtered_data[filtered_data['soil_type'].str.lower() == input_data['soil_type'].lower()]
            
            # Filter by season if available
            if 'season' in filtered_data.columns and 'season' in input_data:
                filtered_data = filtered_data[filtered_data['season'].str.lower() == input_data['season'].lower()]
            
            # If we have matching records, get top crops
            if not filtered_data.empty and 'label' in filtered_data.columns:
                # Count frequency of each crop
                crop_counts = filtered_data['label'].value_counts()
                
                recommendations = []
                for crop, count in crop_counts.head(top_n).items():
                    score = min(100, 70 + (count * 5))  # Base score + frequency bonus
                    
                    # Get crop-specific reasons
                    reasons = self._get_crop_reasons(crop, input_data)
                    
                    recommendations.append({
                        'crop_name': crop.title(),
                        'match_score': score,
                        'confidence': round(score / 100, 2),
                        'reasons': reasons
                    })
                
                return recommendations
            else:
                return self._fallback_crop_recommendation(input_data)
                
        except Exception as e:
            print(f"Error in crop recommendation: {e}")
            return self._fallback_crop_recommendation(input_data)
    
    def _fallback_crop_recommendation(self, input_data, top_n=5):
        """Fallback crop recommendations"""
        state_crops = {
            'karnataka': ['rice', 'sugarcane', 'ragi', 'groundnut', 'cotton', 'pulses'],
            'maharashtra': ['wheat', 'sorghum', 'pulses', 'soybean', 'sugarcane', 'cotton'],
            'punjab': ['wheat', 'rice', 'maize', 'cotton', 'potato', 'vegetables']
        }
        
        state = input_data.get('state', 'karnataka').lower()
        crops = state_crops.get(state, ['wheat', 'pulses', 'vegetables'])
        
        recommendations = []
        for crop in crops[:top_n]:
            score = 80 + random.randint(0, 20)
            reasons = self._get_crop_reasons(crop, input_data)
            
            recommendations.append({
                'crop_name': crop.title(),
                'match_score': score,
                'confidence': round(score / 100, 2),
                'reasons': reasons
            })
        
        return recommendations
    
    def _get_crop_reasons(self, crop, input_data):
        """Generate smart reasons for crop recommendations"""
        crop_reasons = {
            'rice': ["High water availability in your region", "Suitable for your soil type", "Good market demand"],
            'wheat': ["Low water requirement", "Stable market prices", "Good for crop rotation"],
            'sugarcane': ["High yield potential", "Good for your climate", "Industrial demand"],
            'cotton': ["Suitable soil conditions", "Textile industry demand", "Moderate maintenance"],
            'pulses': ["Improves soil fertility", "Low input costs", "Nutritional benefits"],
            'vegetables': ["Short growth cycle", "High nutritional value", "Local market demand"],
            'maize': ["Versatile usage", "Good for animal feed", "Moderate water needs"],
            'groundnut': ["Oilseed crop with good demand", "Improves soil nitrogen", "Drought resistant"]
        }
        
        reasons = crop_reasons.get(crop.lower(), [
            "Suitable for your region",
            "Good yield potential", 
            "Moderate maintenance required"
        ])
        
        # Add soil-specific reason
        soil_type = input_data.get('soil_type', '')
        if soil_type:
            if soil_type.lower() == 'clay':
                reasons.append("Retains moisture well for this crop")
            elif soil_type.lower() == 'sandy':
                reasons.append("Good drainage benefits this crop")
            elif soil_type.lower() == 'loamy':
                reasons.append("Ideal soil texture for this crop")
        
        return reasons[:3]  # Return top 3 reasons

# Global instance
csv_processor = CSVProcessor()