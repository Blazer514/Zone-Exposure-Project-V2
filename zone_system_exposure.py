import math
import streamlit as st

# --- Core Functions ---
def shutter_to_ev(shutter_speed):
    if not shutter_speed:
        return None
    try:
        shutter_speed = float(shutter_speed)
    except:
        return None
    return -math.log2(shutter_speed)

def ev_to_shutter(ev):
    return 1 / (2 ** ev)

def shutter_label(ev):
    shutter_speed = ev_to_shutter(ev)
    if shutter_speed >= 1:
        return f"{shutter_speed:.0f}s"
    else:
        return f"1/{round(1/shutter_speed):.0f}s"

def recommend_exposure(aperture, iso, brightest=None, darkest=None, midtone=None, subject=None):
    readings = {}
    if brightest: readings['brightest'] = shutter_to_ev(brightest)
    if darkest: readings['darkest'] = shutter_to_ev(darkest)
    if midtone: readings['midtone'] = shutter_to_ev(midtone)
    if subject: readings['subject'] = shutter_to_ev(subject)

    readings = {k: v for k, v in readings.items() if v is not None}
    if not readings:
        return "No valid readings provided."

    output = []

    # Scene range
    if 'brightest' in readings and 'darkest' in readings:
        scene_range = readings['brightest'] - readings['darkest']
        output.append(f"Scene brightness range: {scene_range:.2f} stops")

    # Zone placement suggestion
    if 'darkest' in readings:
        suggested_ev = readings['darkest'] + 2
        output.append(f"Place shadows on Zone III → Suggested EV: {suggested_ev:.2f}")
        if 'brightest' in readings:
            highlight_zone = readings['brightest'] - suggested_ev
            output.append(f"Highlights would fall at Zone {5 + highlight_zone:.1f}")
    elif 'subject' in readings:
        suggested_ev = readings['subject']
        output.append(f"Place subject on Zone V → Suggested EV: {suggested_ev:.2f}")
    elif 'midtone' in readings:
        suggested_ev = readings['midtone']
        output.append(f"Use midtone reading (Zone V) → Suggested EV: {suggested_ev:.2f}")
    else:
        suggested_ev = list(readings.values())[0]
        output.append(f"Fallback: using first reading → Suggested EV: {suggested_ev:.2f}")

    # Adjust EV for aperture and ISO (reference EV is f/16 ISO 100)
    reference_aperture = 16
    reference_iso = 100
    aperture_adjust = math.log2((aperture / reference_aperture) ** 2)
    iso_adjust = math.log2(iso / reference_iso)
    adjusted_ev = suggested_ev - aperture_adjust - iso_adjust

    # Convert EV back to shutter speed
    shutter_speed = ev_to_shutter(adjusted_ev)
    if shutter_speed >= 1:
        shutter_str = f"{shutter_speed:.0f}s"
    else:
        shutter_str = f"1/{round(1/shutter_speed):.0f}s"

    output.append(f"Suggested exposure ≈ {shutter_str} at f/{aperture} ISO {iso}")

    return "\n".join(output)

# --- Web App (Streamlit with styled UI + sliders + aperture/ISO) ---
st.set_page_config(page_title="Zone System Calculator", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        border-radius: 12px;
        padding: 10px 20px;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .result-box {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎞️ Zone System Exposure Calculator")
st.write("Adjust shutter speed readings with sliders. Each slider also shows its shutter speed equivalent. Set your aperture and ISO for personalized exposure results.")

col1, col2 = st.columns(2)
with col1:
    ev_brightest = st.slider("☀️ Brightest part of the scene", min_value=-5.0, max_value=15.0, value=10.0, step=0.1)
    st.caption(f"Equivalent: {shutter_label(ev_brightest)}")
    ev_midtone = st.slider("🌗 Mid-tone reading", min_value=-5.0, max_value=15.0, value=8.0, step=0.1)
    st.caption(f"Equivalent: {shutter_label(ev_midtone)}")
with col2:
    ev_darkest = st.slider("🌑 Darkest part of the scene", min_value=-5.0, max_value=15.0, value=5.0, step=0.1)
    st.caption(f"Equivalent: {shutter_label(ev_darkest)}")
    ev_subject = st.slider("🎯 Subject reading", min_value=-5.0, max_value=15.0, value=7.0, step=0.1)
    st.caption(f"Equivalent: {shutter_label(ev_subject)}")

st.markdown("---")

aperture = st.number_input("🔘 Aperture (f-stop)", min_value=1.0, max_value=64.0, value=16.0, step=0.1)
iso = st.number_input("🎞️ ISO", min_value=25, max_value=12800, value=100, step=1)

# Convert slider EVs back to shutter speeds
brightest = ev_to_shutter(ev_brightest)
darkest = ev_to_shutter(ev_darkest)
midtone = ev_to_shutter(ev_midtone)
subject = ev_to_shutter(ev_subject)

if st.button("📸 Calculate Exposure"):
    result = recommend_exposure(aperture, iso, brightest, darkest, midtone, subject)
    st.markdown(f"<div class='result-box'><pre>{result}</pre></div>", unsafe_allow_html=True)

# --- Deployment Instructions ---
st.markdown("## 🚀 Deployment Instructions")
st.write("1. Save this file as `zone_system_app.py`. ")
st.write("2. Create a file called `requirements.txt` in the same folder with the following line:")
st.code("streamlit")
st.write("3. Push both files to a GitHub repository.")
st.write("4. Go to [Streamlit Community Cloud](https://share.streamlit.io), sign in, and deploy your repo.")
st.write("5. Your app will get a public URL you can share.")
