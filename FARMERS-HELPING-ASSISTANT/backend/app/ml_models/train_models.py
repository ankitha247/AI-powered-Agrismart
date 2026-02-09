# train_models.py

import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

from real_data_loader import RealDataLoader


def encode_categorical(df: pd.DataFrame, target_col: str = None):
    """
    Label-encode all object (string) columns except the target.
    Returns: transformed df, encoders dict
    """
    df_enc = df.copy()
    encoders = {}

    for col in df_enc.columns:
        if df_enc[col].dtype == "object" and col != target_col:
            le = LabelEncoder()
            df_enc[col] = le.fit_transform(df_enc[col].astype(str))
            encoders[col] = le

    return df_enc, encoders


def train_yield_model(loader: RealDataLoader, models_dir: str):
    print("\n=== Training Yield Prediction Model ===")
    df_yield = loader.preprocess_yield_data()

    # Split features/target
    X = df_yield.drop("yield", axis=1)
    y = df_yield["yield"]

    # Encode categorical features
    X_enc, encoders = encode_categorical(X, target_col=None)

    X_train, X_test, y_train, y_test = train_test_split(
        X_enc, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"📈 Yield Model MSE: {mse:.4f}")
    print(f"📈 Yield Model R² : {r2:.4f}")

    # Save model + encoders
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(model, os.path.join(models_dir, "yield_model.pkl"))
    joblib.dump(encoders, os.path.join(models_dir, "yield_encoders.pkl"))

    print(f"✅ Saved yield model & encoders to {models_dir}")


def train_crop_model(loader: RealDataLoader, models_dir: str):
    print("\n=== Training Crop Recommendation Model ===")
    df_crop = loader.preprocess_crop_data()

    # Split features/target
    X = df_crop.drop("crop", axis=1)
    y = df_crop["crop"]

    # Encode input features + target crop
    X_enc, feature_encoders = encode_categorical(X, target_col=None)
    crop_encoder = LabelEncoder()
    y_enc = crop_encoder.fit_transform(y.astype(str))

    X_train, X_test, y_train, y_test = train_test_split(
        X_enc, y_enc, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=400,
        random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"📈 Crop Model Accuracy: {acc:.4f}")

    # Save model + encoders
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(model, os.path.join(models_dir, "crop_model.pkl"))
    joblib.dump(feature_encoders, os.path.join(models_dir, "crop_feature_encoders.pkl"))
    joblib.dump(crop_encoder, os.path.join(models_dir, "crop_label_encoder.pkl"))

    print(f"✅ Saved crop model & encoders to {models_dir}")


if __name__ == "__main__":
    # root/backend/models/
    base_dir = os.path.dirname(__file__)     # backend/app
    models_dir = os.path.join(base_dir, "ml_models", "modelsapp")

    loader = RealDataLoader()
    loader.load_data()
    # Make sure data loads
    if not loader.load_data():
        raise SystemExit("❌ Could not load dataset – check path backend/data/crop_yield_data.csv")

    train_yield_model(loader, models_dir)
    train_crop_model(loader, models_dir)
