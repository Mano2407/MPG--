"""Shared preprocessing components (imported by train.py and app.py)."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

RAW_NUMERIC = ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model year"]
RAW_CATEGORICAL = ["origin", "car name"]

BRAND_FIXES = {
    "chevy": "chevrolet", "chevroelt": "chevrolet", "maxda": "mazda", "mercedes": "mercedes-benz",
    "toyouta": "toyota", "vokswagen": "volkswagen", "vw": "volkswagen",
}


def extract_brand(name) -> str:
    if not isinstance(name, str) or not name.strip():
        return "unknown"
    brand = name.strip().lower().split()[0]
    return BRAND_FIXES.get(brand, brand)


class FeatureEngineer(BaseEstimator, TransformerMixin):
    """Raw columns -> model-ready columns (brand extraction + engineered ratios).
    Missing values are left as NaN here and handled by the imputers downstream."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        for c in RAW_NUMERIC:
            X[c] = pd.to_numeric(X[c], errors="coerce")
        X["brand"] = X["car name"].apply(extract_brand)
        X["origin"] = X["origin"].astype("object").where(X["origin"].notna(), np.nan)
        X["origin"] = X["origin"].apply(lambda v: str(int(v)) if pd.notna(v) else np.nan)
        X["power_to_weight"] = X["horsepower"] / X["weight"] * 1000
        X["disp_per_cyl"] = X["displacement"] / X["cylinders"]
        X["car_age"] = 83 - X["model year"]
        return X[["cylinders", "displacement", "horsepower", "weight", "acceleration",
                  "model year", "power_to_weight", "disp_per_cyl", "car_age", "origin", "brand"]]


NUM_FEATS = ["cylinders", "displacement", "horsepower", "weight", "acceleration",
             "model year", "power_to_weight", "disp_per_cyl", "car_age"]
CAT_FEATS = ["origin", "brand"]


def build_preprocessor() -> Pipeline:
    num = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
    cat = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                    ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=3))])
    ct = ColumnTransformer([("num", num, NUM_FEATS), ("cat", cat, CAT_FEATS)])
    return Pipeline([("engineer", FeatureEngineer()), ("columns", ct)])


def build_model_pipeline(estimator) -> Pipeline:
    return Pipeline([("prep", build_preprocessor()), ("model", estimator)])
