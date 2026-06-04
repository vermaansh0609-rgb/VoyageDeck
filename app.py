import streamlit as st
import requests

# 1. --- PAGE FUNCTIONS ---

def show_home():
    st.markdown("<h1 style='text-align: center; color: #0369A1; margin-bottom:0;'>✈️ VoyageDeck</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #64748B; font-size:16px; font-weight: 500; margin-top:5px;'>Maximizing experiences while minimizing expenses</p>", unsafe_allow_html=True)
    st.write("")

    destination = st.text_input("📍 Where are we going?", placeholder="e.g., Goa, Tokyo, Paris...", key="input_dest")

    col1, col2 = st.columns(2)
    with col1:
        days = st.slider("⏳ Trip Duration (Days)", 1, 7, 3, key="input_days")
    with col2:
        budget_choice = st.selectbox("💰 Choose your Budget Vibe", ["Dirt Cheap", "Careful Budget", "Flashpacker", "Custom Specification"], key="input_budget")

    if budget_choice == "Dirt Cheap":
        st.info("💡 **Dirt Cheap Profile:** Survival mode. Focuses only on zero-cost sights, walking routes, street food, and shared hostel dorms.")
        execution_constraint = "Survival mode: zero-cost sights, walking, street food, shared hostel dorms."
    elif budget_choice == "Careful Budget":
        st.info("💡 **Careful Budget Profile:** Standard student framework. Includes public transit passes, local diners, and low-cost ticketed entry points.")
        execution_constraint = "Standard student framework: public transit passes, local diners, affordable ticketed entries."
    elif budget_choice == "Flashpacker":
        st.info("💡 **Flashpacker Profile:** Affordable comfort mode. Allows for private hostel rooms, casual dining, and entry to major iconic landmarks.")
        execution_constraint = "Affordable comfort mode: private hostel rooms, casual dining, entry to major landmarks."
    else:
        custom_val = st.text_input("Specify your exact budget ceiling:", placeholder="e.g., Rs. 5000 max...", key="input_custom")
        execution_constraint = f"Strict custom constraint limit: {custom_val}"

    st.markdown("### 🛠️ Tailor Your Adventure Options")
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
            st.session_state['constraint'] = execution_constraint
            
            selected_features = []
            if want_food: selected_features.append("Cheap Eats")
            if want_stay: selected_features.append("Low-cost Hostels")
            if want_spots: selected_features.append("Free Attractions")
            if want_tips: selected_features.append("Transit Hacks")
            st.session_state['features'] = ", ".join(selected_features)
            st.success("Configuration locked in! Switch to the 'Itinerary' page in the sidebar menu.")


def show_itinerary():
    st.title("⏳ AI Itinerary Generator")
    if 'destination' not in st.session_state:
        st.warning("Please configure your travel parameters on the Home page first!")
        return

    dest = st.session_state['destination']
    days = st.session_state['duration']
    constraint = st.session_state['constraint']
    feats = st.session_state['features']

    st.write(f"📊 **Target Routing:** {dest} | **Duration:** {days} Days")
    
    if st.button("🧠 COMPUTE ITINERARY"):
        with st.spinner("VoyageDeck routing via serverless AI cloud..."):
            API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-1.5B-Instruct"
            prompt = f"<|im_start|>system\nYou are VoyageDeck, an expert student travel guide. Provide highly realistic itineraries with markdown emoji bullets.<|im_end|>\n<|im_start|>user\nCreate a day-by-day itinerary for a student trip to {dest} for {days} days. Budget Profile: {constraint}. Priority Focus Elements: {feats}. Format clearly using headings for Day 1, Day 2, etc.<|im_end|>\n<|im_start|>assistant\n"
            
            try:
                response = requests.post(API_URL, json={"inputs": prompt, "parameters": {"max_new_tokens": 700, "temperature": 0.7}})
                raw_output = response.json()
                
                if isinstance(raw_output, list) and 'generated_text' in raw_output[0]:
                    clean_itinerary = raw_output[0]['generated_text'].split("<|im_start|>assistant\n")[-1]
                    st.markdown("### 🗺️ Your Personalized Deck")
                    st.markdown(clean_itinerary)
                else:
                    st.info("🔄 Serverless model engine is spinning up. Please try again in 10 seconds.")
            except Exception as e:
                st.error("Network interface busy. Try executing again.")


def show_tracker():
    st.title("💰 Smart Expense Calculator")
    dest = st.session_state.get('destination', 'Your Destination')
    days = st.session_state.get('duration', 3)

    st.subheader(f"📊 Outlay Projections for {dest} ({days} Days)")
    col1, col2 = st.columns(2)
    with col1:
        stay_cost = st.number_input("Stay per night:", min_value=0, value=15)
        food_cost = st.number_input("Food allocation per day:", min_value=0, value=10)
    with col2:
        transit_cost = st.number_input("Local transit per day:", min_value=0, value=5)
        misc_cost = st.number_input("Emergency fund:", min_value=0, value=20)

    total_stay = stay_cost * (days - 1 if days > 1 else 1)
    total_daily = (food_cost + transit_cost) * days
    grand_total = total_stay + total_daily + misc_cost

    st.markdown("---")
    st.metric(label="Estimated Grand Total Outlay", value=f"{grand_total}")


# 2. --- ROUTING & NAVIGATION ENGINE ---

st.set_page_config(page_title="VoyageDeck - AI Travel Planner", page_icon="✈️", layout="centered")

# Global CSS Injection
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #E0F2FE 0%, #F1F5F9 100%) !important; }
    .stButton > button {
        background: linear-gradient(135deg, #0EA5E9 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important; font-size: 16px !important; text-transform: uppercase !important;
        border: none !important; border-radius: 14px !important; padding: 14px 28px !important;
        box-shadow: 0px 6px 0px #01476C !important; transition: transform 0.08s ease, box-shadow 0.08s ease !important; cursor: pointer !important; width: 100%;
    }
    .stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0px 8px 0px #01476C !important; }
    .stButton > button:active { transform: translateY(6px) !important; box-shadow: 0px 0px 0px #01476C !important; }
    .travel-card { background: #FFFFFF; padding: 20px; border-radius: 16px; box-shadow: 0px 4px 0px #E2E8F0; border: 2px solid #E2E8F0; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# Declare logical pages linked to functions
page_home = st.Page(show_home, title="Home", icon="✈️", default=True)
page_itinerary = st.Page(show_itinerary, title="Itinerary", icon="⏳")
page_tracker = st.Page(show_tracker, title="Budget Tracker", icon="💰")

# Initialize routing navigation system
pg = st.navigation([page_home, page_itinerary, page_tracker])
pg.run()
