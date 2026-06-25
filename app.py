import streamlit as st
import requests
from datetime import datetime
import json
import re
import folium
import hashlib
from streamlit_folium import st_folium

# --- SECURE NATIVE STATE MEMORY SYSTEM ---
if 'user_creds_store' not in st.session_state:
    # Seed an initial master admin profile for direct testing
    st.session_state['user_creds_store'] = {
        "admin": hashlib.sha256("12345".encode()).hexdigest()
    }
if 'user_work_store' not in st.session_state:
    st.session_state['user_work_store'] = {}

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 1. --- LIVE FINANCIAL PIPELINE ---
def fetch_live_exchange_rate(target_currency):
    """Fetches real-time market exchange rates with INR baseline using the free Frankfurter API."""
    if target_currency == "INR (₹)":
        return 1.0, "₹"
    
    currency_code = "USD" if "USD" in target_currency else "EUR"
    symbol = "$" if "USD" in target_currency else "€"
    
    try:
        response = requests.get(f"https://api.frankfurter.dev/v1/latest?base=INR&symbols={currency_code}", timeout=5)
        if response.status_code == 200:
            rate = response.json()["rates"].get(currency_code, 1.0)
            return rate, symbol
    except Exception:
        pass
    
    fallback_rates = {"USD": 0.011, "EUR": 0.010}
    return fallback_rates.get(currency_code, 1.0), symbol


# 2. --- SYSTEM SCREEN INTERFACES ---

def show_home():
    st.markdown(f"<h1 style='color: #00F0FF; margin-bottom:0;'>👋 Welcome, {st.session_state['username']}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94A3B8; font-size:16px; font-weight: 500; margin-top:5px;'>The Intellectual Architecture for Cost-Effective Travel</p>", unsafe_allow_html=True)
    st.write("")

    # Verify if user profile workspace has active historic parameters
    current_user = st.session_state['username']
    saved_work = st.session_state['user_work_store'].get(current_user, {})
    
    if saved_work.get("saved_destination"):
        st.info(f"📂 **Memory Engine Active:** Reloaded last workspace file for **{saved_work['saved_destination']}**.")

    destination = st.text_input("📍 Where are we going?", placeholder="e.g., Goa, Varanasi, Mumbai...", key="input_dest")

    col1, col2, col3 = st.columns([2, 2, 1.5])
    with col1:
        today = datetime.now()
        date_range = st.date_input("📅 Select Trip Dates", value=(today, today), key="calendar_dates")
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
            days = (end_date - start_date).days + 1
            travel_month = start_date.strftime("%B")
        else:
            days = 1
            travel_month = today.strftime("%B")
        st.caption(f"Calculated Duration: **{days} Days** ({travel_month})")
        
    with col2:
        budget_choice = st.selectbox("💰 Choose your Budget Vibe", ["Dirt Cheap", "Careful Budget", "Flashpacker", "Custom Specification"], key="input_budget")
    with col3:
        currency_choice = st.selectbox("💱 UI Currency Layout", ["INR (₹)", "USD ($)", "EUR (€)"], key="input_currency")

    rate_mult, currency_symbol = fetch_live_exchange_rate(currency_choice)
    st.session_state['currency_rate'] = rate_mult
    st.session_state['currency_symbol'] = currency_symbol

    if budget_choice == "Dirt Cheap":
        execution_constraint = "Survival mode: zero-cost sights, walking, street food, shared hostel dorms."
    elif budget_choice == "Careful Budget":
        execution_constraint = "Standard student framework: public transit passes, local diners, affordable ticketed entries."
    elif budget_choice == "Flashpacker":
        execution_constraint = "Affordable comfort mode: private hostel rooms, casual dining, entry to major landmarks."
    else:
        custom_val = st.text_input("Specify exact overall ceiling limit:", placeholder="e.g., 5000...", key="input_custom")
        execution_constraint = f"Strict custom constraint limit: {custom_val}"

    st.markdown("<h3 style='color: #00F0FF;'>🛠️ Tailor Your Adventure Options</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="travel-card">', unsafe_allow_html=True)
        want_food = st.checkbox("🍔 Cheap Eats & Cafes", value=True, key="feat_food")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="travel-card">', unsafe_allow_html=True)
        want_stay = st.checkbox("🛌 Low-cost Student Hostels", value=True, key="feat_stay")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="travel-card">', unsafe_allow_html=True)
        want_spots = st.checkbox("🏛️ Free Attractions", value=True, key="feat_spots")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="travel-card">', unsafe_allow_html=True)
        want_tips = st.checkbox("🚌 Local Transit Hacks", value=False, key="feat_tips")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Plot My Budget Escape"):
        if not destination:
            st.error("Please insert an absolute target destination first!")
        else:
            st.session_state['destination'] = destination
            st.session_state['duration'] = days
            st.session_state['travel_month'] = travel_month
            st.session_state['constraint'] = execution_constraint
            
            selected_features = []
            if want_food: selected_features.append("Cheap Eats")
            if want_stay: selected_features.append("Low-cost Hostels")
            if want_spots: selected_features.append("Free Attractions")
            if want_tips: selected_features.append("Transit Hacks")
            st.session_state['features'] = ", ".join(selected_features)
            st.session_state['generation_complete'] = False 
            st.success("Configuration locked! Switch to 'AI Generation Deck' in the sidebar menu.")


def show_itinerary():
    st.markdown("<h1 style='color: #00F0FF;'>⏳ AI Itinerary Generator</h1>", unsafe_allow_html=True)
    
    current_user = st.session_state['username']
    saved_work = st.session_state['user_work_store'].get(current_user, {})
    
    if 'destination' not in st.session_state:
        if saved_work.get("saved_destination"):
            st.session_state['destination'] = saved_work["saved_destination"]
            st.session_state['display_itinerary'] = saved_work["saved_itinerary"]
            st.session_state['coords_json'] = saved_work["saved_coords"]
            st.session_state['generation_complete'] = True
        else:
            st.warning("Please configure your travel parameters on the Configuration Hub first!")
            return

    dest = st.session_state['destination']
    symbol = st.session_state.get('currency_symbol', '₹')

    st.write(f"📊 **Active Identity Profile Work:** {dest}")
    
    # 35% Left Sidebar for Itinerary Text / 65% Main Panel for Interactive Maps
    col_text, col_map = st.columns([3.5, 6.5])
    
    with col_text:
        if st.button("🧠 COMPUTE PRO ITINERARY"):
            st.session_state['generation_complete'] = False
            days = st.session_state.get('duration', 3)
            month = st.session_state.get('travel_month', 'Current Month')
            constraint = st.session_state.get('constraint', 'Standard Profile')
            feats = st.session_state.get('features', 'General')
            
            with st.spinner("VoyageDeck routing via lightning-fast Groq Cloud..."):
                API_URL = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                    "Content-Type": "application/json"
                }
                
                system_instruction = (
                    "You are VoyageDeck, an elite travel analytics bot. Provide comprehensive day-by-day itineraries. "
                    f"Output all estimated costs in currency layout format {symbol}. "
                    "CRITICAL OUTPUT STRUCTURE: You must provide a complete itinerary for ALL requested days. Do not truncate. "
                    "At the very end of your response, output the exact marker separator string: |||COORD_DATA||| "
                    "Immediately following that separator, output a single raw JSON array containing latitude and longitude objects "
                    "for EVERY single physical venue, attraction, or stop mentioned across all days in the itinerary. "
                    "Example layout format exactly: Itinerary text goes here... |||COORD_DATA|||[{\"name\":\"Spot\",\"lat\":15.49,\"lon\":73.82}]"
                )
                
                user_query = (
                    f"Create an extensively detailed day-by-day budget itinerary for {dest} for exactly {days} days during the month of {month}. "
                    f"Budget Profile: {constraint}. Features requested: {feats}. Output cleanly formatted headers."
                )
                
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_query}
                    ],
                    "temperature": 0.5,
                    "max_tokens": 2800
                }
                
                try:
                    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
                    if response.status_code == 200:
                        raw_output = response.json()['choices'][0]['message']['content']
                        
                        if "|||COORD_DATA|||" in raw_output:
                            parts = raw_output.split("|||COORD_DATA|||")
                            text_itinerary = parts[0].strip()
                            coords_json = parts[1].strip()
                        else:
                            text_itinerary = raw_output
                            coords_json = "[]"
                        
                        # Direct assignment back into session cluster
                        st.session_state['user_work_store'][current_user] = {
                            "saved_destination": dest,
                            "saved_itinerary": text_itinerary,
                            "saved_coords": coords_json
                        }
                        
                        st.session_state['display_itinerary'] = text_itinerary
                        st.session_state['coords_json'] = coords_json
                        st.session_state['generation_complete'] = True
                        st.success("✨ Workspace metrics synchronized successfully to your account memory folder!")
                    else:
                        st.error("Groq Cloud routing interface execution failed.")
                except Exception as e:
                    st.error(f"Network Latency Failure: {str(e)}")

        if st.session_state.get('generation_complete', False):
            display_text = st.session_state.get('display_itinerary', '')
            st.markdown("<h3 style='color: #00F0FF;'>🗺️ Your Personalized Deck</h3>", unsafe_allow_html=True)
            st.markdown(display_text)

    with col_map:
        st.markdown("<h3 style='color: #00F0FF;'>📍 Tactical Navigation HUD</h3>", unsafe_allow_html=True)
        
        map_points = []
        if st.session_state.get('generation_complete', False):
            json_str = st.session_state.get('coords_json', '[]')
            try:
                json_str = re.sub(r"```[a-z]*", "", json_str).replace("```", "").strip()
                map_points = json.loads(json_str)
            except Exception:
                pass

        center_lat = map_points[0]['lat'] if map_points else 22.0
        center_lon = map_points[0]['lon'] if map_points else 78.0
        zoom_level = 13 if map_points else 4
        
        m = folium.Map(
            location=[center_lat, center_lon], 
            zoom_start=zoom_level, 
            tiles="CartoDB Positron",
            zoom_control=True
        )
        
        custom_css = '''
        <style>
            .neon-marker {
                width: 16px !important;
                height: 16px !important;
                background-color: #0055FF;
                border: 3px solid #FFFFFF;
                border-radius: 50%;
                box-shadow: 0 0 10px #0055FF, 0 0 15px #0055FF;
            }
        </style>
        '''
        m.get_root().header.add_child(folium.Element(custom_css))

        coordinate_pipeline = []
        
        for idx, pt in enumerate(map_points):
            try:
                coord = [float(pt['lat']), float(pt['lon'])]
                coordinate_pipeline.append(coord)
                
                popup_html = f"<div style='color:#333333; font-weight:700;'>📍 stop {idx+1}:</div><div style='color:#0055FF;'>{pt['name']}</div>"
                
                folium.Marker(
                    location=coord,
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=pt['name'],
                    icon=folium.DivIcon(
                        html='<div class="neon-marker"></div>',
                        icon_size=(16, 16),
                        icon_anchor=(8, 8)
                    )
                ).add_to(m)
            except Exception:
                pass
            
        if len(coordinate_pipeline) > 1:
            folium.PolyLine(
                locations=coordinate_pipeline,
                color="#0055FF",
                weight=4,
                opacity=0.8
            ).add_to(m)
            
        st_folium(m, width=None, height=600, use_container_width=True, key="voyagedeck_map")


def show_tracker():
    st.markdown("<h1 style='color: #00F0FF;'>💰 Smart Expense Calculator</h1>", unsafe_allow_html=True)
    dest = st.session_state.get('destination', 'Your Destination')
    days = st.session_state.get('duration', 3)
    
    rate = st.session_state.get('currency_rate', 1.0)
    sym = st.session_state.get('currency_symbol', '₹')

    st.markdown(f"<h3 style='color: #FFFFFF;'>📊 Estimated Costs for {dest} ({days} Days)</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        stay_cost = st.number_input(f"Hotel / Hostel Room (Per night in {sym}):", min_value=0.0, value=float(600 * rate), step=50.0)
        food_cost = st.number_input(f"Food & Drinks (Daily allowance in {sym}):", min_value=0.0, value=float(400 * rate), step=50.0)
    with col2:
        transit_cost = st.number_input(f"Local Transit / Metro (Daily budget in {sym}):", min_value=0.0, value=float(200 * rate), step=20.0)
        misc_cost = st.number_input(f"Shopping & Emergency Cash (Total in {sym}):", min_value=0.0, value=float(1000 * rate), step=100.0)

    total_stay = stay_cost * (days - 1 if days > 1 else 1)
    total_daily_expenses = (food_cost + transit_cost) * days
    grand_total = total_stay + total_daily_expenses + misc_cost

    st.markdown("---")
    st.metric(label=f"Estimated Grand Total Outlay ({sym})", value=f"{sym} {grand_total:,.2f}")


# NEW PAGE INTERFACE FUNCTION
def show_about():
    st.markdown("<h1 style='color: #00F0FF;'>ℹ️ About the Developer</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="travel-card">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Creator Profile")
    st.markdown("#### **ANSH VERMA**")
    st.markdown(
        "Hello! I am the creator and engineer behind **VoyageDeck**. This platform was built "
        "to solve a common travel challenge: balancing real-world travel ambitions with strict financial guardrails. "
        "By merging high-speed AI text compilation models with dynamic geographic mapping interfaces, VoyageDeck "
        "delivers optimized smart exploration routes instantly."
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="travel-card">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Engine Architecture")
    st.markdown(
        "- **Core Interface:** Python / Streamlit Engine Framework\n"
        "- **AI Router Intelligence:** LLaMA 3.1 Inference Pipeline via Groq Cloud\n"
        "- **Visual HUD Components:** Folium Interactive Mapping Systems\n"
        "- **Authentication Module:** Persistent State-Locked Encryption Panels"
    )
    st.markdown('</div>', unsafe_allow_html=True)


# --- LOGIN PORTAL UI FORM LAYOUT ---
def render_auth_gateway():
    st.markdown("<h1 style='text-align: center; color: #00F0FF; margin-top: 40px;'>✈️ VoyageDeck</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size:15px;'>Production Secure Identity Entry Portal</p>", unsafe_allow_html=True)
    
    with st.form(key="auth_form_panel"):
        auth_mode = st.radio("Select System Operation Mode:", ["Secure Login Profile", "Register New User ID"])
        st.markdown("---")
        
        user_id = st.text_input("👤 Enter Account Username / Login ID:", placeholder="e.g., student_explorer")
        user_pass = st.text_input("🔒 Enter Account Password Passphrase:", type="password", placeholder="••••••••")
        
        submit_btn = st.form_submit_button(label="EXECUTE IDENTITY AUTHORIZATION")
        
        if submit_btn:
            u_clean = user_id.strip()
            p_clean = user_pass.strip()
            
            if auth_mode == "Secure Login Profile":
                if u_clean in st.session_state['user_creds_store'] and st.session_state['user_creds_store'][u_clean] == hash_password(p_clean):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = u_clean
                    st.success("Access authorized! Entry authenticated.")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password credential configuration format.")
            else:
                if len(u_clean) < 3 or len(p_clean) < 4:
                    st.error("Username must be > 2 chars, Password must be > 3 chars.")
                elif u_clean in st.session_state['user_creds_store']:
                    st.error("This Username is already occupied. Pick a separate unique identity name.")
                else:
                    st.session_state['user_creds_store'][u_clean] = hash_password(p_clean)
                    st.session_state['user_work_store'][u_clean] = {
                        "saved_destination": "", "saved_itinerary": "", "saved_coords": "[]"
                    }
                    st.success("✨ User deployment completely set up! Switch selector to Login and click execute to enter.")


# --- MAIN ENGINE ENTRY CONFIGURATION ---
st.set_page_config(page_title="VoyageDeck", page_icon="✈️", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0B0F19 !important; }
    [data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] span, [data-testid="stMain"] li {
        color: #FFFFFF !important; font-weight: 500 !important;
    }
    [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 { color: #00F0FF !important; }
    .stButton > button, [data-testid="stForm"] button {
        background: linear-gradient(135deg, #00F0FF 0%, #007799 100%) !important;
        color: #0B0F19 !important; font-weight: 800 !important; font-size: 14px !important;
        text-transform: uppercase !important; border: none !important; border-radius: 12px !important;
        padding: 10px 20px !important; width: 100%; box-shadow: 0px 4px 0px #004455 !important;
    }
    .travel-card {
        background: #1E293B; padding: 15px; border-radius: 12px; border: 2px solid #334155; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state['logged_in']:
    render_auth_gateway()
else:
    with st.sidebar:
        st.markdown(f"🧬 Active Profile: **{st.session_state['username']}**")
        if st.button("🔒 SECURELY LOG OUT"):
            st.session_state['logged_in'] = False
            st.session_state['username'] = None
            st.rerun()
            
    page_home = st.Page(show_home, title="Configuration Hub", icon="✈️", default=True)
    page_itinerary = st.Page(show_itinerary, title="AI Generation Deck", icon="⏳")
    page_tracker = st.Page(show_tracker, title="Financial Analytics", icon="💰")
    page_about = st.Page(show_about, title="About Developer", icon="ℹ️") # Page mapped here

    pg = st.navigation([page_home, page_itinerary, page_tracker, page_about])
    pg.run()
