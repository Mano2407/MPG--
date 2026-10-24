# MPG Predictor AI - Streamlit app

## Run
    pip install -r requirements.txt
    streamlit run app.py

Open http://localhost:8501. A trained model is included; `python train.py` re-trains it
(the app also retrains automatically if your scikit-learn version differs).

## Files
- app.py - Streamlit UI (Predict, Compare, What-If Lab, Explore, Model Arena, About)
- pipeline.py - preprocessing: feature engineering, imputation, scaling, one-hot encoding
- train.py - tunes and compares 5 algorithms, deploys the best by CV-RMSE
- styles.py - CSS animations + animated speedometer
- data/auto-mpg.csv - UCI Auto-MPG dataset
- model.joblib, metrics.json - trained pipeline + evaluation results

## Deploy free
Push this folder to GitHub, then https://share.streamlit.io -> New app -> app.py
