import json
import subprocess
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sklearn
import streamlit as st

from pipeline import extract_brand
from styles import CSS, GAUGE, HERO

BASE = Path(__file__).parent
st.set_page_config(page_title="MPG Predictor AI", page_icon="⛽", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

PLOT = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Poppins, sans-serif"))
ORIGINS = {1: "🇺🇸 USA", 2: "🇪🇺 Europe", 3: "🇯🇵 Japan"}


# ------------------------------------------------------------------ loading
@st.cache_data
def load_data():
    p = BASE / "data" / "auto-mpg.csv"
    if p.exists():
        d = pd.read_csv(p)
    else:  # fallback if the data folder was not uploaded
        d = pd.read_csv("https://raw.githubusercontent.com/mwaskom/seaborn-data/master/mpg.csv")
        d["origin"] = d["origin"].map({"usa": 1, "europe": 2, "japan": 3})
        d = d.rename(columns={"model_year": "model year", "name": "car name"})
    d["brand"] = d["car name"].apply(extract_brand)
    d["origin_name"] = d["origin"].map(ORIGINS)
    return d


@st.cache_resource(show_spinner=False)
def load_model():
    """Load the trained pipeline; retrain automatically if missing or built with another scikit-learn."""
    mp, jp = BASE / "model.joblib", BASE / "metrics.json"
    stale = True
    if mp.exists() and jp.exists():
        stale = json.loads(jp.read_text()).get("sklearn_version") != sklearn.__version__
    if stale:
        with st.spinner("⚙️ First launch: training models on your machine (≈1 min)…"):
            subprocess.run([sys.executable, "train.py"], cwd=BASE, check=True)
    return joblib.load(mp), json.loads(jp.read_text())


df = load_data()
model, metrics = load_model()
best = next(r for r in metrics["results"] if r["model"] == metrics["best_model"])
RMSE = best["test_rmse"]
brands = sorted(b for b in df["brand"].unique())

# ------------------------------------------------------------------ helpers
PRESETS = {
    "🚗 Toyota Corolla '80": dict(cyl=4, disp=97, hp=75, wt=2155, acc=16.4, yr=80, origin=3, brand="toyota", mname="corolla"),
    "🏎️ Ford Mustang II '75": dict(cyl=8, disp=302, hp=140, wt=3449, acc=10.5, yr=75, origin=1, brand="ford", mname="mustang ii"),
    "🚙 Chevy Impala '71": dict(cyl=8, disp=400, hp=150, wt=4464, acc=12.0, yr=71, origin=1, brand="chevrolet", mname="impala"),
    "🐇 VW Rabbit '78": dict(cyl=4, disp=89, hp=62, wt=1845, acc=15.3, yr=78, origin=2, brand="volkswagen", mname="rabbit"),
    "🅷 Honda Civic '80": dict(cyl=4, disp=91, hp=67, wt=1850, acc=13.8, yr=80, origin=3, brand="honda", mname="civic"),
    "🏁 BMW 2002 '73": dict(cyl=4, disp=121, hp=113, wt=2234, acc=12.5, yr=73, origin=2, brand="bmw", mname="2002"),
}
DEFAULT_A = PRESETS["🚗 Toyota Corolla '80"]
DEFAULT_B = PRESETS["🚙 Chevy Impala '71"]


def init_car(prefix, d):
    for k, v in d.items():
        st.session_state.setdefault(f"{prefix}_{k}", v)
    st.session_state.setdefault(f"{prefix}_hp_unknown", False)


def apply_preset(prefix, d):
    for k, v in d.items():
        st.session_state[f"{prefix}_{k}"] = v
    st.session_state[f"{prefix}_hp_unknown"] = False


def random_car(prefix):
    r = df.dropna(subset=["horsepower"]).sample(1).iloc[0]
    apply_preset(prefix, dict(cyl=int(r.cylinders), disp=int(r.displacement), hp=int(r.horsepower), wt=int(r.weight),
                              acc=float(r.acceleration), yr=int(r["model year"]), origin=int(r.origin),
                              brand=r.brand, mname=""))


def car_form(prefix):
    """Renders the input widgets for one car and returns the raw feature row."""
    c1, c2 = st.columns(2)
    with c1:
        cyl = st.select_slider("🔩 Cylinders", [3, 4, 5, 6, 8], key=f"{prefix}_cyl")
        disp = st.slider("🛢️ Displacement (cu in)", 60, 470, key=f"{prefix}_disp")
        hp_unknown = st.checkbox("❓ I don't know the horsepower", key=f"{prefix}_hp_unknown",
                                 help="Missing values are filled in automatically by the pipeline's imputer.")
        hp = st.slider("🐎 Horsepower", 40, 250, key=f"{prefix}_hp", disabled=hp_unknown)
        wt = st.slider("⚖️ Weight (lbs)", 1500, 5200, step=10, key=f"{prefix}_wt")
    with c2:
        acc = st.slider("⏱️ Acceleration (0-60, sec)", 7.0, 26.0, step=0.1, key=f"{prefix}_acc")
        yr = st.slider("📅 Model year (19xx)", 70, 82, key=f"{prefix}_yr")
        origin = st.radio("🌍 Origin", list(ORIGINS), format_func=ORIGINS.get, horizontal=True, key=f"{prefix}_origin")
        opts = brands + ["other…"]
        brand = st.selectbox("🏷️ Brand", opts, key=f"{prefix}_brand")
        mname = st.text_input("🔤 Model name (optional)", key=f"{prefix}_mname", placeholder="e.g. corolla")
        if brand == "other…":
            brand = st.text_input("Type the brand", key=f"{prefix}_brand_other") or "unknown"
    return dict(cylinders=cyl, displacement=disp, horsepower=np.nan if hp_unknown else hp, weight=wt,
                acceleration=acc, **{"model year": yr}, origin=origin, **{"car name": f"{brand} {mname}".strip()})


def show_html(html, height):
    """Render animated HTML/JS (st.iframe on new Streamlit, components.html on older ones)."""
    if hasattr(st, "iframe"):
        st.iframe(html, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=height)


def predict(rows):
    return model.predict(pd.DataFrame(rows))


def grade(m):
    for t, g, c in [(35, "A+", "#00e5a8"), (30, "A", "#7bed9f"), (25, "B", "#c6f06b"),
                    (20, "C", "#ffd32a"), (15, "D", "#ff9f43")]:
        if m >= t:
            return g, c
    return "E", "#ff4d4d"


def convert(mpg, unit):
    return {"MPG": (mpg, "mpg"), "km/L": (mpg * 0.425144, "km/L"), "L/100 km": (235.215 / mpg, "L/100km")}[unit]


def kpi(ico, val, lbl, delay=0):
    return (f'<div class="kpi" style="animation-delay:{delay}s"><div class="ico">{ico}</div>'
            f'<div class="val">{val}</div><div class="lbl">{lbl}</div></div>')


def brief(row):
    hp = "?" if pd.isna(row["horsepower"]) else int(row["horsepower"])
    return (f"{row['car name'] or 'unnamed'} · {int(row['cylinders'])} cyl · {int(row['displacement'])} cu in · {hp} hp · "
            f"{int(row['weight'])} lbs · 19{int(row['model year'])}")


# ------------------------------------------------------------------ state
init_car("a", DEFAULT_A)
init_car("c1", DEFAULT_A)
init_car("c2", DEFAULT_B)
st.session_state.setdefault("history", [])
st.session_state.setdefault("result", None)

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("## 🎛️ Control Center")
    unit = st.radio("📏 Display unit", ["MPG", "km/L", "L/100 km"], horizontal=True)
    st.markdown("**⛽ Running-cost settings**")
    cur = st.text_input("Currency symbol", "₹")
    price_l = st.number_input("Fuel price per litre", 1.0, 500.0, 100.0, step=1.0)
    km_year = st.slider("Distance driven per year (km)", 2000, 50000, 12000, step=1000)
    st.divider()
    st.markdown("**⚡ Quick-load a classic**")
    for label, d in PRESETS.items():
        st.button(label, key=f"p_{label}", on_click=apply_preset, args=("a", d), width="stretch")
    st.button("🎲 Surprise me!", on_click=random_car, args=("a",), width="stretch")
    st.divider()
    st.markdown(f"🏆 **Deployed model**\n\n{metrics['best_model']}\n\nR² = **{best['test_r2']:.3f}** · RMSE = **{best['test_rmse']:.2f}** mpg")

# ------------------------------------------------------------------ hero
st.markdown(HERO, unsafe_allow_html=True)
st.write("")
tab_pred, tab_cmp, tab_lab, tab_eda, tab_arena, tab_about = st.tabs(
    ["🔮 Predict", "⚖️ Compare Cars", "🧪 What-If Lab", "📊 Explore Data", "🏆 Model Arena", "ℹ️ About"])

# ================================================================== PREDICT
with tab_pred:
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.markdown("### 🚘 Describe your vehicle")
        row_a = car_form("a")
        go_btn = st.button("🚀 Predict Fuel Efficiency", type="primary", width="stretch")

    if go_btn:
        stages = ["🧹 Cleaning raw inputs…", "🩹 Imputing missing values…", "📐 Scaling numeric features…",
                  "🔤 Encoding categories (origin, brand)…", "🧠 Running " + metrics["best_model"] + "…"]
        bar, txt = st.progress(0), st.empty()
        for i, s in enumerate(stages, 1):
            txt.markdown(f"**{s}**")
            bar.progress(i / len(stages))
            time.sleep(0.28)
        bar.empty(); txt.empty()
        mpg = float(predict([row_a])[0])
        st.session_state.result = dict(row=row_a, mpg=mpg, fresh=True)
        st.session_state.history.append({"Car": brief(row_a), "Pred. MPG": round(mpg, 2),
                                         "km/L": round(mpg * 0.425144, 2)})

    with right:
        res = st.session_state.result
        if res is None:
            st.markdown('<div class="panel" style="text-align:center;padding:60px 20px">'
                        '<div style="font-size:4rem;animation:floaty 3s ease-in-out infinite">🚗💨</div>'
                        '<h3>Ready when you are</h3><p style="color:#9fb0d6">Set the specs on the left, or pick a '
                        'classic from the sidebar, then hit <b>Predict</b>.</p></div>', unsafe_allow_html=True)
        else:
            mpg, row = res["mpg"], res["row"]
            g, gc = grade(mpg)
            show_html(GAUGE.replace("__VALUE__", f"{mpg:.2f}"), 300)
            val, u = convert(mpg, unit)
            pct = float((df["mpg"] < mpg).mean() * 100)
            litres_year = km_year / (mpg * 0.425144)
            cost = litres_year * price_l
            co2 = litres_year * 2.31  # kg CO2 per litre of petrol
            cls = "shake" if mpg < 15 else ""
            st.markdown(f'<div class="{cls}" style="display:flex;align-items:center;gap:18px">'
                        f'<div class="grade" style="background:{gc}">{g}</div>'
                        f'<div><div style="font-size:2rem;font-weight:800">{val:.1f} <span style="font-size:1rem;color:#9fb0d6">{u}</span></div>'
                        f'<div style="color:#9fb0d6;font-size:.9rem">likely between <b>{max(mpg-RMSE,0):.1f}</b> and <b>{mpg+RMSE:.1f}</b> mpg</div></div></div>',
                        unsafe_allow_html=True)
            chips = '<span class="chip">✅ Pipeline OK</span>'
            if pd.isna(row["horsepower"]):
                chips += '<span class="chip warn">🩹 Horsepower imputed (median)</span>'
            if row["car name"].split(" ")[0].lower() not in brands:
                chips += '<span class="chip warn">🆕 Unseen brand → handled safely</span>'
            st.markdown(f"<div style='margin-top:10px'>{chips}</div>", unsafe_allow_html=True)
            st.markdown('<div class="kpi-row">' +
                        kpi("🔁", f"{235.215/mpg:.1f}", "L / 100 km", .05) +
                        kpi("💸", f"{cur}{cost:,.0f}", "fuel cost / year", .15) +
                        kpi("🌱", f"{co2:,.0f} kg", "CO₂ / year", .25) +
                        kpi("🥇", f"Top {100-pct:.0f}%", "vs 1970s dataset", .35) + '</div>', unsafe_allow_html=True)
            st.markdown(f"**Efficiency percentile** · better than {pct:.0f}% of cars in the dataset")
            st.markdown(f'<div class="bar-wrap"><div class="bar" style="width:{pct}%;background:linear-gradient(90deg,#ff4d4d,#ffd32a,#00e5a8)"></div></div>',
                        unsafe_allow_html=True)
            if res.get("fresh"):
                if mpg >= 30:
                    st.balloons()
                    st.toast("Wow, very fuel efficient! 🌿", icon="🎉")
                elif mpg < 15:
                    st.toast("Thirsty engine! ⛽🔥", icon="😅")
                res["fresh"] = False

    # similar cars
    if st.session_state.result:
        row = st.session_state.result["row"]
        feats = ["cylinders", "displacement", "horsepower", "weight", "acceleration", "model year"]
        ref = df[feats].fillna(df[feats].median())
        z = (ref - ref.mean()) / ref.std()
        q = pd.Series({f: (row[f] if not pd.isna(row[f]) else ref[f].median()) for f in feats})
        d = (((z - (q - ref.mean()) / ref.std()) ** 2).sum(axis=1)) ** .5
        sim = df.loc[d.nsmallest(4).index, ["car name", "model year", "weight", "horsepower", "mpg"]].rename(
            columns={"car name": "Similar real car", "model year": "Year", "weight": "Weight", "horsepower": "HP", "mpg": "Actual MPG"})
        st.markdown("### 🔎 Most similar real cars in the dataset")
        st.dataframe(sim, hide_index=True, width="stretch")

    if st.session_state.history:
        with st.expander(f"🕘 Prediction history ({len(st.session_state.history)})"):
            h = pd.DataFrame(st.session_state.history)
            st.dataframe(h, hide_index=True, width="stretch")
            st.download_button("⬇️ Download history (CSV)", h.to_csv(index=False), "mpg_predictions.csv", "text/csv")
            if st.button("🗑️ Clear history"):
                st.session_state.history = []
                st.rerun()

# ================================================================== COMPARE
with tab_cmp:
    st.markdown("### ⚖️ Head-to-head duel")
    ca, cb = st.columns(2, gap="large")
    with ca:
        st.markdown("#### 🔵 Car A")
        ra = car_form("c1")
    with cb:
        st.markdown("#### 🔴 Car B")
        rb = car_form("c2")
    if st.button("⚔️ Fight!", width="stretch"):
        pa, pb = predict([ra, rb])
        win = "A" if pa >= pb else "B"
        mx = max(pa, pb, 1)
        st.markdown(
            f'<div class="panel"><h3 style="text-align:center">🏁 Car {win} is more fuel efficient by '
            f'<span style="color:#00e5a8">{abs(pa-pb):.1f} mpg</span></h3>'
            f'<b>🔵 Car A — {pa:.1f} mpg</b><div class="bar-wrap"><div class="bar" style="width:{pa/mx*100}%;background:#2f80ff"></div></div>'
            f'<b>🔴 Car B — {pb:.1f} mpg</b><div class="bar-wrap"><div class="bar" style="width:{pb/mx*100}%;background:#ff4d6d"></div></div>'
            f'<p style="color:#9fb0d6">Over {km_year:,} km/year Car {win} saves about '
            f'<b>{cur}{abs(km_year/(pa*.425144)-km_year/(pb*.425144))*price_l:,.0f}</b> in fuel.</p></div>', unsafe_allow_html=True)
        st.balloons()

# ================================================================== WHAT-IF
with tab_lab:
    st.markdown("### 🧪 What-If Lab")
    st.caption("Uses the car configured in the **Predict** tab. See how changing one spec moves the prediction.")
    base_mpg = float(predict([row_a])[0])
    sweeps = {"weight": ("Weight (lbs)", np.arange(1500, 5201, 100)), "horsepower": ("Horsepower", np.arange(40, 251, 5)),
              "displacement": ("Displacement (cu in)", np.arange(60, 471, 10)), "model year": ("Model year", np.arange(70, 83, 1)),
              "acceleration": ("Acceleration (s)", np.arange(7, 26.1, .5))}
    feat = st.selectbox("Feature to sweep", list(sweeps), format_func=lambda k: sweeps[k][0])
    xs = sweeps[feat][1]
    rows = [{**row_a, feat: x} for x in xs]
    if feat == "horsepower":
        pass
    ys = predict(rows)
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines+markers", line=dict(color="#00e5a8", width=4, shape="spline"),
                               fill="tozeroy", fillcolor="rgba(0,229,168,.12)", name="Predicted MPG"))
    cur_x = row_a[feat] if not pd.isna(row_a[feat]) else None
    if cur_x is not None:
        fig.add_trace(go.Scatter(x=[cur_x], y=[base_mpg], mode="markers", marker=dict(size=18, color="#ff4d6d", line=dict(width=3, color="white")), name="Your car"))
    fig.update_layout(**PLOT, height=420, xaxis_title=sweeps[feat][0], yaxis_title="Predicted MPG", title="Sensitivity curve",
                      updatemenus=[dict(type="buttons", showactive=False, x=0.02, y=1.18, buttons=[dict(label="▶ Animate", method="animate",
                                        args=[None, dict(frame=dict(duration=60, redraw=True), fromcurrent=True)])])],
                      )
    fig.frames = [go.Frame(data=[go.Scatter(x=xs[:i + 1], y=ys[:i + 1])], traces=[0]) for i in range(2, len(xs))]
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### 🌡️ Weight × Horsepower heat-map")
    W, H = np.arange(1500, 5201, 150), np.arange(40, 251, 10)
    grid = [{**row_a, "weight": w, "horsepower": h} for h in H for w in W]
    Z = predict(grid).reshape(len(H), len(W))
    hm = go.Figure(go.Heatmap(x=W, y=H, z=Z, colorscale="Turbo", colorbar=dict(title="MPG")))
    if not pd.isna(row_a["horsepower"]):
        hm.add_trace(go.Scatter(x=[row_a["weight"]], y=[row_a["horsepower"]], mode="markers",
                                marker=dict(size=16, color="white", symbol="star"), name="Your car"))
    hm.update_layout(**PLOT, height=430, xaxis_title="Weight (lbs)", yaxis_title="Horsepower")
    st.plotly_chart(hm, width="stretch")

# ================================================================== EXPLORE
with tab_eda:
    st.markdown("### 📊 Explore the data")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🚗 Cars", len(df)); k2.metric("⛽ Avg MPG", f"{df.mpg.mean():.1f}")
    k3.metric("🏆 Best MPG", f"{df.mpg.max():.1f}"); k4.metric("🩹 Missing HP", int(df.horsepower.isna().sum()))
    st.markdown("#### 🎬 Fuel economy through the years (press ▶)")
    dd = df.dropna(subset=["horsepower"]).sort_values("model year")
    fa = px.scatter(dd, x="weight", y="mpg", size="horsepower", color="origin_name", animation_frame="model year",
                    hover_name="car name", size_max=28, range_x=[1400, 5300], range_y=[5, 50],
                    color_discrete_sequence=["#ff4d6d", "#2f80ff", "#00e5a8"])
    fa.update_layout(**PLOT, height=520, legend_title="Origin")
    st.plotly_chart(fa, width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        yr = df.groupby(["model year", "origin_name"], as_index=False)["mpg"].mean()
        st.plotly_chart(px.line(yr, x="model year", y="mpg", color="origin_name", markers=True, title="Average MPG by year",
                                color_discrete_sequence=["#ff4d6d", "#2f80ff", "#00e5a8"]).update_layout(**PLOT, height=380), width="stretch")
    with c2:
        st.plotly_chart(px.box(df, x="cylinders", y="mpg", color="cylinders", title="MPG by cylinders",
                               color_discrete_sequence=px.colors.sequential.Tealgrn).update_layout(**PLOT, height=380, showlegend=False), width="stretch")
    c3, c4 = st.columns(2)
    with c3:
        corr = df[["mpg", "cylinders", "displacement", "horsepower", "weight", "acceleration", "model year"]].corr().round(2)
        st.plotly_chart(px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1, title="Correlation matrix")
                        .update_layout(**PLOT, height=420), width="stretch")
    with c4:
        st.plotly_chart(px.scatter_3d(dd, x="weight", y="horsepower", z="mpg", color="mpg", color_continuous_scale="Viridis",
                                      hover_name="car name", title="3-D view: weight · horsepower · MPG").update_layout(**PLOT, height=420), width="stretch")
    with st.expander("🔍 Browse the raw data"):
        st.dataframe(df.drop(columns=["origin_name"]), width="stretch")

# ================================================================== ARENA
with tab_arena:
    st.markdown("### 🏆 Model Arena")
    st.caption("Five algorithms were tuned with 5-fold cross-validated grid search. The champion is chosen by CV-RMSE (never by test score).")
    res_df = pd.DataFrame(metrics["results"]).sort_values("cv_rmse")
    st.markdown(f'<div class="panel" style="text-align:center"><div style="font-size:3rem;animation:pop 1s both">🥇</div>'
                f'<h3 style="margin:0">{metrics["best_model"]}</h3><p style="color:#9fb0d6;margin:4px 0 0">Test R² {best["test_r2"]:.3f} · '
                f'RMSE {best["test_rmse"]:.2f} · MAE {best["test_mae"]:.2f} mpg</p></div>', unsafe_allow_html=True)
    show = res_df.rename(columns={"model": "Model", "cv_rmse": "CV RMSE", "cv_r2": "CV R²", "test_rmse": "Test RMSE", "test_mae": "Test MAE", "test_r2": "Test R²"})
    st.dataframe(show.style.format({c: "{:.3f}" for c in show.columns[1:]}).highlight_min(subset=["CV RMSE", "Test RMSE", "Test MAE"], color="#0b6b53")
                 .highlight_max(subset=["CV R²", "Test R²"], color="#0b6b53"), hide_index=True, width="stretch")
    a, b = st.columns(2)
    with a:
        f = px.bar(res_df, x="model", y="test_r2", color="test_r2", color_continuous_scale="Tealgrn", title="Test R² (higher is better)", text_auto=".3f")
        f.update_layout(**PLOT, height=400, xaxis_title=None, coloraxis_showscale=False, yaxis_range=[0.7, 1])
        st.plotly_chart(f, width="stretch")
    with b:
        f = px.bar(res_df, x="model", y="test_rmse", color="test_rmse", color_continuous_scale="Sunsetdark_r", title="Test RMSE in MPG (lower is better)", text_auto=".2f")
        f.update_layout(**PLOT, height=400, xaxis_title=None, coloraxis_showscale=False)
        st.plotly_chart(f, width="stretch")
    c, d = st.columns(2)
    with c:
        act, prd = np.array(metrics["test_actual"]), np.array(metrics["test_pred"])
        f = go.Figure([go.Scatter(x=act, y=prd, mode="markers", marker=dict(size=9, color=np.abs(act - prd), colorscale="Turbo", showscale=True,
                                  colorbar=dict(title="|error|")), name="Test cars"),
                       go.Scatter(x=[8, 47], y=[8, 47], mode="lines", line=dict(dash="dash", color="white"), name="Perfect")])
        f.update_layout(**PLOT, height=420, title="Actual vs predicted (held-out test set)", xaxis_title="Actual MPG", yaxis_title="Predicted MPG")
        st.plotly_chart(f, width="stretch")
    with d:
        imp = pd.DataFrame(metrics["importance"]).sort_values("importance")
        f = px.bar(imp, x="importance", y="feature", orientation="h", color="importance", color_continuous_scale="Viridis",
                   title="What drives the prediction? (permutation importance)")
        f.update_layout(**PLOT, height=420, coloraxis_showscale=False, yaxis_title=None)
        st.plotly_chart(f, width="stretch")

# ================================================================== ABOUT
with tab_about:
    st.markdown("### ℹ️ How it works")
    st.markdown("""
<div class="panel">

**End-to-end preprocessing pipeline** (one scikit-learn `Pipeline`, applied automatically to every prediction)

1. **Feature engineering** – brand extracted from *car name* (typos like *chevy / vw / toyouta* fixed), plus power-to-weight, displacement-per-cylinder and car age.
2. **Missing values** – numeric → median imputation, categorical → most-frequent imputation (the dataset has 6 missing horsepower values).
3. **Scaling** – `StandardScaler` on all numeric features.
4. **Encoding** – `OneHotEncoder(handle_unknown="ignore")` for *origin* and *brand*, so unseen brands never crash the app.
5. **Model** – Ridge, KNN, SVR, Random Forest and Gradient Boosting are tuned with GridSearchCV; the best by cross-validated RMSE is deployed (refit on all data).

**Good to know**
- The data covers 1970–1982 cars, so predictions for modern vehicles are extrapolations. Treat them as indicative only.
- The ± band shown next to every prediction is the model's hold-out RMSE.
- Re-train anytime with `python train.py`.
</div>""", unsafe_allow_html=True)

st.markdown('<div class="footer">Built with ❤️ using Streamlit · scikit-learn · Plotly &nbsp;|&nbsp; Dataset: UCI Auto-MPG</div>', unsafe_allow_html=True)
