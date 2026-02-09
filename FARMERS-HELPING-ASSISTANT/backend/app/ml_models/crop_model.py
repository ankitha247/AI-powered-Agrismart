# backend/app/ml_models/crop_model.py

"""
Rule-based crop recommendation for Karnataka taluks:
- Siruguppa (Ballari)
- Sindhanur (Raichur)
- Gangavathi (Koppal)
- Vijaypur (Vijayapura)

Input:
  {
    "state": "Karnataka",
    "district": "...",
    "soil_type": "...",
    "season": "...",
    "irrigation_source": "..."
  }

Output:
  {
    "recommended_crop": "<best crop>",
    "top_predictions": [
        {"crop": "<crop1>", "score": 0.6},
        {"crop": "<crop2>", "score": 0.25},
        {"crop": "<crop3>", "score": 0.15}
    ]
  }
"""

from typing import Dict, List, Any


# ----------------------------------------------------------------------
# RULES: you can adjust these if sir says
# ----------------------------------------------------------------------

RULES = [
    # SIRUGUPPA (Ballari) - Paddy/Hybrid Rice/Chilli/Cotton etc.
    {
        "district": "Siruguppa",
        "season": "Kharif",
        "soil_types": ["Red soil", "Black soil", "Alluvial soil"],
        "irrigation": ["Canal", "Borewell"],
        "crops": [
            ("Paddy", 0.55),
            ("Maize", 0.25),
            ("Cotton", 0.12),
            ("Red gram", 0.08),
        ],
    },
    {
        "district": "Siruguppa",
        "season": "Rabi",
        "soil_types": ["Red soil", "Black soil"],
        "irrigation": ["Borewell", "Canal"],
        "crops": [
            ("Wheat", 0.4),
            ("Chickpea", 0.35),
            ("Sunflower", 0.25),
        ],
    },
    {
        "district": "Siruguppa",
        "season": "Zaid",
        "soil_types": ["Red soil", "Alluvial soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Maize", 0.45),
            ("Vegetables", 0.35),
            ("Fodder maize", 0.20),
        ],
    },

    # SINDHANUR (Raichur) - Big paddy belt
    {
        "district": "Sindhanur",
        "season": "Kharif",
        "soil_types": ["Red soil", "Black soil", "Alluvial soil"],
        "irrigation": ["Canal", "Borewell"],
        "crops": [
            ("Paddy", 0.65),
            ("Maize", 0.2),
            ("Soybean", 0.1),
            ("Cotton", 0.05),
        ],
    },
    {
        "district": "Sindhanur",
        "season": "Rabi",
        "soil_types": ["Red soil", "Black soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Paddy", 0.5),
            ("Wheat", 0.25),
            ("Chickpea", 0.25),
        ],
    },
    {
        "district": "Sindhanur",
        "season": "Zaid",
        "soil_types": ["Red soil", "Alluvial soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Vegetables", 0.4),
            ("Maize", 0.35),
            ("Fodder maize", 0.25),
        ],
    },

    # GANGAVATHI (Koppal) - Paddy, sugarcane, banana, groundnut
    {
        "district": "Gangavathi",
        "season": "Kharif",
        "soil_types": ["Red soil", "Black soil", "Alluvial soil"],
        "irrigation": ["Canal", "Borewell"],
        "crops": [
            ("Paddy", 0.5),
            ("Groundnut", 0.2),
            ("Maize", 0.15),
            ("Cotton", 0.15),
        ],
    },
    {
        "district": "Gangavathi",
        "season": "Rabi",
        "soil_types": ["Red soil", "Black soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Groundnut", 0.4),
            ("Sunflower", 0.3),
            ("Chickpea", 0.3),
        ],
    },
    {
        "district": "Gangavathi",
        "season": "Zaid",
        "soil_types": ["Red soil", "Alluvial soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Vegetables", 0.4),
            ("Maize", 0.3),
            ("Fodder maize", 0.3),
        ],
    },

    # VIJAYPUR (Vijayapura) - Jowar, Bajra, Cotton, Pulses
    {
        "district": "Vijaypur",
        "season": "Kharif",
        "soil_types": ["Black soil", "Red soil"],
        "irrigation": ["Rainfed", "Borewell"],
        "crops": [
            ("Jowar", 0.45),
            ("Bajra", 0.25),
            ("Cotton", 0.2),
            ("Red gram", 0.1),
        ],
    },
    {
        "district": "Vijaypur",
        "season": "Rabi",
        "soil_types": ["Black soil"],
        "irrigation": ["Rainfed", "Borewell"],
        "crops": [
            ("Wheat", 0.4),
            ("Chickpea", 0.35),
            ("Linseed", 0.25),
        ],
    },
    {
        "district": "Vijaypur",
        "season": "Zaid",
        "soil_types": ["Red soil", "Black soil"],
        "irrigation": ["Borewell"],
        "crops": [
            ("Vegetables", 0.5),
            ("Fodder maize", 0.3),
            ("Maize", 0.2),
        ],
    },
]


class CropRecommender:
    """
    Simple rule-based recommender.
    No ML, no .pkl files.
    """

    def __init__(self) -> None:
        # In rule-based mode, we don't need model loading flags
        self.is_trained_on_real_data = True

    def _match_rules(self, district: str, season: str,
                     soil_type: str, irrigation_source: str) -> List[Dict[str, Any]]:
        """
        Try to find matching rules by:
          1. Exact district + season + soil_type + irrigation
          2. If none → district + season + soil_type
          3. If none → district + season
        """
        district = district.strip()
        season = season.strip()
        soil_type = soil_type.strip()
        irrigation_source = irrigation_source.strip()

        exact_matches = []
        soil_matches = []
        season_matches = []

        for rule in RULES:
            if rule["district"] != district:
                continue
            if rule["season"] != season:
                continue

            # Exact all four
            if soil_type in rule["soil_types"] and irrigation_source in rule["irrigation"]:
                exact_matches.append(rule)
            # district+season+soil only
            elif soil_type in rule["soil_types"]:
                soil_matches.append(rule)
            # district+season only
            else:
                season_matches.append(rule)

        if exact_matches:
            return exact_matches
        if soil_matches:
            return soil_matches
        return season_matches

    def recommend(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method called from API.

        input_data keys:
          - state
          - district
          - soil_type
          - season
          - irrigation_source
        """
        district = input_data.get("district", "")
        soil_type = input_data.get("soil_type", "")
        season = input_data.get("season", "")
        irrigation_source = input_data.get("irrigation_source", "")

        print("📊 Rule-based crop input:", input_data)

        matching_rules = self._match_rules(
            district=district,
            season=season,
            soil_type=soil_type,
            irrigation_source=irrigation_source,
        )

        # If nothing at all matches, give a generic safe set
        if not matching_rules:
            print("⚠️ No specific rule matched, using generic fallback crops")
            fallback_crops = [("Paddy", 0.4), ("Maize", 0.35), ("Chickpea", 0.25)]
            recommended_crop = fallback_crops[0][0]
            top_predictions = [
                {"crop": c, "score": float(s)} for c, s in fallback_crops
            ]
            return {
                "recommended_crop": recommended_crop,
                "top_predictions": top_predictions,
            }

        # Take the first matching rule (you can later combine multiple if needed)
        rule = matching_rules[0]
        crops = rule["crops"]

        # Sort by score descending (just to be safe)
        crops_sorted = sorted(crops, key=lambda x: x[1], reverse=True)
        recommended_crop = crops_sorted[0][0]

        top_predictions = [
            {"crop": c, "score": float(s)} for c, s in crops_sorted[:3]
        ]

        print("🌱 Rule-based recommendation:", recommended_crop, top_predictions)

        return {
            "recommended_crop": recommended_crop,
            "top_predictions": top_predictions,
        }


# Global instance, used by routes
crop_recommender = CropRecommender()
