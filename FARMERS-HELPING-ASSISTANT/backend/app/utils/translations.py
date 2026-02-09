import json
import os
from typing import Dict, Any

class Translator:
    def __init__(self):
        self.locales = {}
        self.load_locales()
    
    def load_locales(self):
        locales_path = os.path.join(os.path.dirname(__file__), '..', 'locales')
        
        for lang_file in ['en.json', 'hi.json', 'kn.json']:
            lang_code = lang_file.split('.')[0]
            file_path = os.path.join(locales_path, lang_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.locales[lang_code] = json.load(f)
                print(f"✅ Loaded translations: {lang_code}")
            except Exception as e:
                print(f"❌ Failed to load {lang_code}: {e}")
    
    def translate(self, key: str, lang: str = 'en') -> str:
        try:
            if lang not in self.locales:
                lang = 'en'
            
            keys = key.split('.')
            value = self.locales[lang]
            
            for k in keys:
                value = value[k]
            
            return value
            
        except (KeyError, TypeError):
            return f"[{key}]"
    
    def get_form_options(self, lang: str = 'en') -> Dict[str, Any]:
        return {
            'soil_types': {
                'clay': self.translate('soil_types.clay', lang),
                'sandy': self.translate('soil_types.sandy', lang),
                'loamy': self.translate('soil_types.loamy', lang)
            },
            'seasons': {
                'spring': self.translate('seasons.spring', lang),
                'summer': self.translate('seasons.summer', lang),
                'monsoon': self.translate('seasons.monsoon', lang),
                'winter': self.translate('seasons.winter', lang)
            },
            'irrigation_sources': {
                'rainfed': self.translate('irrigation.rainfed', lang),
                'well': self.translate('irrigation.well', lang),
                'canal': self.translate('irrigation.canal', lang),
                'drip': self.translate('irrigation.drip', lang)
            }
        }

translator = Translator()