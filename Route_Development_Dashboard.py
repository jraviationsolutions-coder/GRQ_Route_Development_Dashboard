import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="GRQ Route Development Dashboard",
    page_icon="✈️",
    layout="wide"
)

# Custom minimalist dark-mode styling
st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .stMetric { background-color: #191919; border: 1px solid #333; padding: 15px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ Groningen Airport Eelde (GRQ) — Route Proposal & Market Analysis")
st.caption("Interactief dashboard voor route-ontwikkeling, catchment leakage en netwerkconnectiviteit.")

# 1. Excel Bestand Inladen (Alleen via gebruikersupload)
@st.cache_data
def load_all_sheets(file_source):
    try:
        xls = pd.ExcelFile(file_source)
        sheets_data = {}
        for sheet in xls.sheet_names:
            try:
                sheets_data[sheet] = pd.read_excel(xls, sheet_name=sheet)
            except Exception:
                sheets_data[sheet] = pd.DataFrame()
        return sheets_data
    except Exception as e:
        st.error(f"Fout bij het laden van het bestand: {e}")
        return None

# Upload functionaliteit in de zijbalk
uploaded_file = st.sidebar.file_uploader("Upload Excel-bestand (.xlsx)", type=["xlsx"])

# Wacht netjes tot de gebruiker een bestand heeft gekozen
if uploaded_file is None:
    st.info("👈 Upload in de linkerzijbalk een Excel-bestand (`.xlsx`) om het dashboard te laden.")
    st.stop()

all_data = load_all_sheets(uploaded_file)

if not all_data:
    st.stop()

# 2. Tabs Structuur voor het Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 Route Voorstellen", 
    "📊 Airport Choice Analysis", 
    "🥊 Route Competitors", 
    "💧 Surface Leakage", 
    "📅 Connectivity & Schedules"
])

# ==========================================
# TAB 1: PROPOSAL INVESTIGATION
# ==========================================
with tab1:
    st.header("📍 Voorgestelde Routes (Proposal Investigation)")
    df_prop = all_data.get('Proposal Investigation', pd.DataFrame())
    
    if not df_prop.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Totaal Voorgestelde Routes", len(df_prop))
        c2.metric("Business Routes", len(df_prop[df_prop['PAX Type'] == 'Business']))
        c3.metric("Leisure Routes", len(df_prop[df_prop['PAX Type'] == 'Non-Business']))
        
        st.markdown("---")
        st.dataframe(df_prop, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Proposal Investigation'.")

# ==========================================
# TAB 2: AIRPORT CHOICE ANALYSIS
# ==========================================
with tab2:
    st.header("📊 Luchthaven Keuze & Passagiersstromen")
    df_choice = all_data.get('Airport Choice', pd.DataFrame())
    
    if not df_choice.empty:
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.subheader("Business Passagiers per Route")
            fig_bus = px.bar(
                df_choice, 
                x='Route', 
                y='Probability% Business', 
                color='Trip Purpose',
                color_discrete_sequence=['#00205B', '#BFCCDE'],
                title="Business PAX per Route"
            )
            st.plotly_chart(fig_bus, use_container_width=True)

        with col_r:
            st.subheader("Non-Business Passagiers per Route")
            fig_nonbus = px.bar(
                df_choice, 
                x='Route', 
                y='Probability% Non-Business', 
                color='Trip Purpose',
                color_discrete_sequence=['#BFCCDE', '#00205B'],
                title="Non-Business PAX per Route"
            )
            st.plotly_chart(fig_nonbus, use_container_width=True)

        st.dataframe(df_choice, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Airport Choice'.")

# ==========================================
# TAB 3: ROUTE COMPETITORS
# ==========================================
with tab3:
    st.header("🥊 Concurrentie & Route Eigenschappen")
    df_comp = all_data.get('Route Competitors', pd.DataFrame())
    
    if not df_comp.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Frequentie per Week per Routing")
            fig_freq = px.bar(
                df_comp, 
                x='Routing', 
                y='Frequency per Week', 
                color='Catchment',
                title="Wekelijkse Frequentie"
            )
            st.plotly_chart(fig_freq, use_container_width=True)

        with c2:
            st.subheader("PAX uit Catchment per Routing")
            fig_pax = px.bar(
                df_comp, 
                x='Routing', 
                y='PAX from catchment', 
                title="Passagiers uit Catchment Zone"
            )
            st.plotly_chart(fig_pax, use_container_width=True)

        st.dataframe(df_comp, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Route Competitors'.")

# ==========================================
# TAB 4: SURFACE LEAKAGE
# ==========================================
with tab4:
    st.header("💧 Surface Leakage (Passagierslekkage naar andere luchthavens)")
    df_leak = all_data.get('Surface Leakage', pd.DataFrame())
    
    if not df_leak.empty:
        st.subheader("Top Bestemmingen met Hoogste Passagierslekkage")
        fig_leak = px.bar(
            df_leak.sort_values(by='Pax leakage', ascending=False).head(15), 
            x='Destination', 
            y='Pax leakage', 
            color='Region',
            text_auto=True,
            title="Pax Leakage per Bestemming"
        )
        st.plotly_chart(fig_leak, use_container_width=True)

        st.dataframe(df_leak, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Surface Leakage'.")

# ==========================================
# TAB 5: WEIGHTED CONNECTIVITY & SCHEDULES
# ==========================================
with tab5:
    st.header("📅 Netwerk Connectivity & Vliegschema's")
    df_conn = all_data.get('Weighted Connectivity', pd.DataFrame())
    
    if not df_conn.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Transfer Potentieel % per Dag & Maatschappij")
            fig_trans = px.line(
                df_conn[df_conn['Day outbound'] != 'AverageDay'], 
                x='Day outbound', 
                y='Transfer Potential', 
                color='Airline',
                markers=True,
                title="Transfer Potential % gedurende de week"
            )
            st.plotly_chart(fig_trans, use_container_width=True)
            
        with col2:
            st.subheader("Inzetbare Vloot (Fleet)")
            fleet_counts = df_conn['Fleet'].value_counts().reset_index()
            fleet_counts.columns = ['Fleet', 'Aantal']
            fig_fleet = px.pie(fleet_counts, names='Fleet', values='Aantal', hole=0.4)
            st.plotly_chart(fig_fleet, use_container_width=True)

        st.dataframe(df_conn, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Weighted Connectivity'.")