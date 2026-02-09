"""
real_data_loader.py

Utility for loading and preprocessing the REAL agricultural dataset
for:
  - Yield prediction
  - Crop recommendation

Expected CSV file (with header):

  backend/app/data/crop_yield_data.csv

Columns in the CSV:

  'Year',
  'Location',
  'Area',
  'Rainfall',
  'Temperature',
  'Soil type',
  'Irrigation',
  'yeilds',
  'Humidity',
  'Crops',
  'price',
  'Season'

NOTE: We use Option B:
  ❌ No Rainfall / Temperature / Humidity as model features.
  ✅ Features are only:
       state, district, crop_name, soil_type, season, irrigation_source
"""

import os
import logging
from typing import Dict, Any

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class RealDataLoader:
    """
    Loads and preprocesses the real crop yield dataset for:
      - yield prediction
      - crop recommendation
    """

    def __init__(self) -> None:
        self.data: pd.DataFrame | None = None

        # CSV path: backend/app/data/crop_yield_data.csv
        base_dir = os.path.dirname(__file__)              # .../backend/app/ml_models
        self.data_path = os.path.normpath(
            os.path.join(base_dir, "..", "data", "crop_yield_data.csv")
        )

    # -------------------------------------------------------------------------
    # Basic loading
    # -------------------------------------------------------------------------
    def load_data(self, force_reload: bool = False) -> bool:
        """
        Load the dataset from CSV into self.data.

        Returns:
            True  -> loaded successfully
            False -> file not found or error
        """
        if self.data is not None and not force_reload:
            return True

        try:
            abs_path = os.path.abspath(self.data_path)
            print(f"📂 Looking for data at: {abs_path}")
            print(f"📂 File exists: {os.path.exists(abs_path)}")

            if not os.path.exists(abs_path):
                print("❌ CSV file not found at the specified path")
                return False

            # CSV already has column headers
            self.data = pd.read_csv(abs_path)

            print(f"✅ Dataset loaded: {len(self.data)} rows, {len(self.data.columns)} columns")
            print(f"📊 Columns: {list(self.data.columns)}")
            print("📊 First 3 rows:")
            print(self.data.head(3))

            print("📊 Data types:")
            print(self.data.dtypes)

            print("❓ Missing values per column:")
            print(self.data.isnull().sum())

            return True

        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            import traceback
            print("🔍 Traceback:", traceback.format_exc())
            return False

    # -------------------------------------------------------------------------
    # Normalization helpers
    # -------------------------------------------------------------------------
    def normalize_data_units(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize units if needed.

        Assumptions:
          - Temperature is already in °C (typical range < 60)
          - 'yeilds' in CSV are already in tons/hectare
        Only adjust if values look obviously wrong.
        """
        try:
            df_norm = df.copy()

            # Safety: if temperature ever comes in insane values (> 80°C), scale down.
            if "Temperature" in df_norm.columns:
                if df_norm["Temperature"].max() > 80:
                    print("  🔄 Normalizing temperature (dividing by 10)")
                    df_norm["Temperature"] = df_norm["Temperature"] / 10.0

            # Safety: if yield comes in huge values (> 1000), treat as kg/ha and convert to t/ha
            if "yield" in df_norm.columns:
                if df_norm["yield"].max() > 1000:
                    print("  🔄 Normalizing yield (dividing by 1000)")
                    df_norm["yield"] = df_norm["yield"] / 1000.0

            return df_norm

        except Exception as e:
            print(f"❌ Error normalizing data units: {e}")
            return df

    # -------------------------------------------------------------------------
    # Yield prediction preprocessing (Option B: no weather features)
    # -------------------------------------------------------------------------
    def preprocess_yield_data(self) -> pd.DataFrame:
        """
        Preprocess data for yield prediction.

        Target column:
          - 'yield'  (tons/hectare)

        Feature columns used for training:
          - 'state'
          - 'district'
          - 'crop_name'
          - 'soil_type'
          - 'season'
          - 'irrigation_source'

        NOTE: We deliberately DO NOT include Rainfall, Temperature, Humidity
              (Option B – simpler input, same as your frontend form).
        """
        if self.data is None:
            if not self.load_data():
                raise Exception("Real yield data not available - cannot proceed without data file")

        try:
            yield_data = self.data.copy()

            print("🔄 Preprocessing yield data from REAL dataset...")

            # Standardize column names for internal use
            yield_data = yield_data.rename(
                columns={
                    "Location": "district",
                    "Soil type": "soil_type",
                    "Irrigation": "irrigation_source",
                    "Crops": "crop_name",
                    "yeilds": "yield",  # fix spelling
                    "Season": "season",
                }
            )

            # Add state column (all in Karnataka)
            yield_data["state"] = "Karnataka"

            # Only these features + target
            features = [
                "state",
                "district",
                "crop_name",
                "soil_type",
                "season",
                "irrigation_source",
                "yield",
            ]

            yield_data = yield_data[features]

            # Drop rows with missing target
            initial_count = len(yield_data)
            yield_data = yield_data.dropna(subset=["yield"])
            final_count = len(yield_data)

            if final_count == 0:
                raise Exception("No valid yield data found after preprocessing")

            print(f"  📊 Using {final_count} REAL yield records (dropped {initial_count - final_count})")
            print(f"  🌾 Unique crops in real data: {yield_data['crop_name'].nunique()}")
            print(f"  🗺️ Unique districts in real data: {yield_data['district'].nunique()}")

            # Normalize units if needed
            yield_data = self.normalize_data_units(yield_data)

            print("  📈 Real yield statistics (tons/hectare):")
            print(f"     Min : {yield_data['yield'].min():.2f}")
            print(f"     Max : {yield_data['yield'].max():.2f}")
            print(f"     Mean: {yield_data['yield'].mean():.2f}")
            print("  🔍 Final yield features used for training:", list(yield_data.columns))

            return yield_data

        except Exception as e:
            print(f"❌ Error preprocessing REAL yield data: {e}")
            raise Exception(f"Cannot use yield prediction without real data: {e}")

    # -------------------------------------------------------------------------
    # Crop recommendation preprocessing (Option B: no weather features)
    # -------------------------------------------------------------------------
    def preprocess_crop_data(self) -> pd.DataFrame:
        """
        Preprocess data for crop recommendation.

        Target column:
          - 'crop'

        Feature columns used for training:
          - 'state'
          - 'district'
          - 'soil_type'
          - 'season'
          - 'irrigation_source'

        NOTE: We deliberately DO NOT include Rainfall, Temperature, Humidity.
        """
        if self.data is None:
            if not self.load_data():
                raise Exception("Real crop data not available - cannot proceed without data file")

        try:
            crop_data = self.data.copy()

            print("🔄 Preprocessing crop recommendation data from REAL dataset...")

            crop_data = crop_data.rename(
                columns={
                    "Location": "district",
                    "Soil type": "soil_type",
                    "Irrigation": "irrigation_source",
                    "Crops": "crop",
                    "Season": "season",
                }
            )

            crop_data["state"] = "Karnataka"

            features = [
                "state",
                "district",
                "soil_type",
                "season",
                "irrigation_source",
                "crop",
            ]

            crop_data = crop_data[features]

            # Drop duplicates so classification is cleaner
            initial_count = len(crop_data)
            crop_data = crop_data.drop_duplicates()
            final_count = len(crop_data)

            if final_count == 0:
                raise Exception("No valid crop data found after preprocessing")

            print(f"  📊 Using {final_count} REAL crop recommendation records (from {initial_count})")
            print(f"  🌾 Unique crops in real data: {crop_data['crop'].nunique()}")

            print("  📊 Real crop distribution (top 10):")
            crop_counts = crop_data["crop"].value_counts()
            for c, count in crop_counts.head(10).items():
                print(f"     {c}: {count} records")

            print("  🔍 Final crop features used for training:", list(crop_data.columns))

            return crop_data

        except Exception as e:
            print(f"❌ Error preprocessing REAL crop data: {e}")
            raise Exception(f"Cannot use crop recommendation without real data: {e}")

    # -------------------------------------------------------------------------
    # Unique values for dropdowns (for frontend)
    # -------------------------------------------------------------------------
    def get_unique_values(self) -> Dict[str, list]:
        """
        Get unique values for dropdowns from the REAL raw dataset.
        Returns a dict with keys:
          - 'districts'
          - 'crops'
          - 'soil_types'
          - 'seasons'
          - 'irrigation_sources'
        """
        if self.data is None:
            if not self.load_data():
                return {}

        unique_values: Dict[str, list] = {}

        try:
            # Districts (Location in original CSV)
            if "Location" in self.data.columns:
                unique_values["districts"] = sorted(
                    self.data["Location"].astype(str).unique()
                )
                print(f"✅ Found {len(unique_values['districts'])} unique districts")

            # Crops (Crops in original CSV)
            if "Crops" in self.data.columns:
                unique_values["crops"] = sorted(
                    self.data["Crops"].astype(str).unique()
                )
                print(f"✅ Found {len(unique_values['crops'])} unique crops")

            # Soil types
            if "Soil type" in self.data.columns:
                unique_values["soil_types"] = sorted(
                    self.data["Soil type"].astype(str).unique()
                )
                print(f"✅ Found {len(unique_values['soil_types'])} unique soil types")

            # Seasons
            if "Season" in self.data.columns:
                unique_values["seasons"] = sorted(
                    self.data["Season"].astype(str).unique()
                )
                print(f"✅ Found {len(unique_values['seasons'])} unique seasons")

            # Irrigation sources
            if "Irrigation" in self.data.columns:
                unique_values["irrigation_sources"] = sorted(
                    self.data["Irrigation"].astype(str).unique()
                )
                print(
                    f"✅ Found {len(unique_values['irrigation_sources'])} unique irrigation sources"
                )

            return unique_values

        except Exception as e:
            print(f"❌ Error getting unique values: {e}")
            return {}


# Optional: quick manual test
if __name__ == "__main__":
    loader = RealDataLoader
    if loader.load_data():
        _yield_df = loader.preprocess_yield_data()
        _crop_df = loader.preprocess_crop_data()
        uniques = loader.get_unique_values()
        print("\n🔍 Unique values summary:", uniques)

# Global instance used by other modules
real_data_loader = RealDataLoader()

