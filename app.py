import streamlit as st
import requests

# 1. --- PAGE FUNCTIONS ---

def show_home():
    st.markdown("<h1 style='text-align: center; color: #00F0FF; margin-bottom:0;'>✈️ VoyageDeck</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94A3B8; font-size:16px; font-weight: 500; margin-top:5px;'>Maximizing experiences while minimizing expenses</p>", unsafe_allow_html=True)
    st.write("")

    destination = st.text_input("📍 Where are we going?", placeholder="e.g., Goa, Varanasi, Mumbai...", key="input_dest")

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
        custom_val = st.text_input("Specify your exact budget ceiling (in ₹):", placeholder="e.g., 5000...", key="input_custom")
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
            st.session_state['constraint'] = execution_constraint
            
            selected_features = []
            if want_food: selected_features.append("Cheap Eats")
            if want_stay: selected_features.append("Low-cost Hostels")
            if want_spots: selected_features.append("Free Attractions")
            if want_tips: selected_features.append("Transit Hacks")
            st.session_state['features'] = ", ".join(selected_features)
            st.success("Configuration locked in! Switch to the 'Itinerary' page in the sidebar menu.")


def show_itinerary():
    st.markdown("<h1 style='color: #00F0FF;'>⏳ AI Itinerary Generator</h1>", unsafe_allow_html=True)
    if 'destination' not in st.session_state:
        st.warning("Please configure your travel parameters on the Home page first!")
        return

    if "GROQ_API_KEY" not in st.secrets:
        st.error("Missing API Key! Please add 'GROQ_API_KEY' to your Streamlit app secrets.")
        return

    dest = st.session_state['destination']
    days = st.session_state['duration']
    constraint = st.session_state['constraint']
    feats = st.session_state['features']

    st.write(f"📊 **Target Routing:** {dest} | **Duration:** {days} Days")
    
    if st.button("🧠 COMPUTE ITINERARY"):
        with st.spinner("VoyageDeck routing via lightning-fast Groq Cloud..."):
            API_URL = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are VoyageDeck, an expert student travel guide. Provide highly realistic itineraries with markdown emoji bullets. All pricing references must be in Indian Rupees (₹)."},
                    {"role": "user", "content": f"Create a day-by-day itinerary for a student trip to {dest} for {days} days. Budget Profile: {constraint}. Priority Focus Elements: {feats}. Format clearly using headings for Day 1, Day 2, etc. Include realistic cost estimates in INR (₹)."}
                ],
                "temperature": 0.7,
                "max_tokens": 1200
            }
            
            try:
                response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
                
                if response.status_code == 429:
                    st.error("🚦 Rate limit hit. Please wait a minute before making another request.")
                    return
                elif response.status_code != 200:
                    st.error(f"⚠️ Groq API Error: Status {response.status_code}.")
                    return

                raw_output = response.json()
                clean_itinerary = raw_output['choices'][0]['message']['content']
                st.markdown("<h3 style='color: #00F0FF;'>🗺️ Your Personalized
