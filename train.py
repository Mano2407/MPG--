"""Train + compare 5 algorithms, keep the best one, save artifacts.   Run: python train.py"""
import json
import joblib
import sklearn
from sklearn.base import clone
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor

from pipeline import build_model_pipeline, RAW_NUMERIC, RAW_CATEGORICAL

df = pd.read_csv("data/auto-mpg.csv")
df = df.dropna(subset=["mpg"])
X, y = df[RAW_NUMERIC + RAW_CATEGORICAL], df["mpg"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
cv = KFold(5, shuffle=True, random_state=42)

candidates = {
    "Ridge Regression": (Ridge(), {"model__alpha": [0.1, 1, 3, 10, 30]}),
    "K-Nearest Neighbors": (KNeighborsRegressor(), {"model__n_neighbors": [3, 5, 7, 11], "model__weights": ["distance"]}),
    "Support Vector Regression": (SVR(), {"model__C": [3, 10, 30], "model__gamma": ["scale", 0.01]}),
    "Random Forest": (RandomForestRegressor(random_state=42), {"model__n_estimators": [300], "model__max_depth": [None, 12], "model__min_samples_leaf": [1, 2]}),
    "Gradient Boosting": (GradientBoostingRegressor(random_state=42), {"model__n_estimators": [300, 500], "model__learning_rate": [0.03, 0.05], "model__max_depth": [2, 3], "model__subsample": [0.8]}),
}

results, fitted = [], {}
for name, (est, grid) in candidates.items():
    gs = GridSearchCV(build_model_pipeline(est), grid, cv=cv, scoring="neg_root_mean_squared_error", n_jobs=-1)
    gs.fit(X_tr, y_tr)
    best = gs.best_estimator_
    pred = best.predict(X_te)
    cv_r2 = cross_val_score(best, X_tr, y_tr, cv=cv, scoring="r2").mean()
    results.append({
        "model": name,
        "cv_rmse": float(-gs.best_score_),
        "cv_r2": float(cv_r2),
        "test_rmse": float(np.sqrt(mean_squared_error(y_te, pred))),
        "test_mae": float(mean_absolute_error(y_te, pred)),
        "test_r2": float(r2_score(y_te, pred)),
    })
    fitted[name] = best
    print(f"{name:28s} CV-RMSE {results[-1]['cv_rmse']:.3f}  Test R2 {results[-1]['test_r2']:.3f}  Test RMSE {results[-1]['test_rmse']:.3f}")

best_name = min(results, key=lambda r: r["cv_rmse"])["model"]   # selection on CV only (no test leakage)
print("\nBest model:", best_name)

# refit the winner on ALL data for deployment
final = clone(fitted[best_name])  # same tuned hyper-parameters
final.fit(X, y)

pi = permutation_importance(fitted[best_name], X_te, y_te, n_repeats=30, random_state=42, scoring="r2")
importance = sorted(zip(X.columns, pi.importances_mean), key=lambda t: -t[1])

test_pred = fitted[best_name].predict(X_te)
joblib.dump(final, "model.joblib")
json.dump({
    "best_model": best_name,
    "results": results,
    "importance": [{"feature": f, "importance": float(v)} for f, v in importance],
    "test_actual": y_te.round(2).tolist(),
    "test_pred": np.round(test_pred, 2).tolist(),
    "n_rows": int(len(df)),
    "sklearn_version": sklearn.__version__,
}, open("metrics.json", "w"), indent=2)
print("Saved model.joblib and metrics.json")
