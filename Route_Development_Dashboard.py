import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Groningen Airport Eelde (GRQ) | Route Development",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GRQ Kleurenpalet
GRQ_ORANGE = "#F37021"
GRQ_ORANGE_LIGHT = "#FF9E5E"
GRQ_CHARCOAL = "#3A3F42"
GRQ_SLATE = "#6B7280"
GRQ_PALETTE = [GRQ_ORANGE, GRQ_SLATE, GRQ_ORANGE_LIGHT, "#9CA3AF", "#D95D13"]

# Custom minimalist dark-mode styling (Groningen Airport Eelde branding)
st.markdown(f"""
    <style>
    .main {{ padding: 1.5rem 2rem; }}
    h1, h2, h3 {{ letter-spacing: 0.01em; font-weight: 600; }}
    
    /* Custom GRQ Brand Header */
    .brand-header {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(90deg, #1D2023 0%, #262A2E 100%);
        border: 1px solid #3A3F42;
        border-left: 5px solid {GRQ_ORANGE};
        border-radius: 10px;
        padding: 20px 26px;
        margin-bottom: 24px;
    }}
    .brand-left {{ display: flex; align-items: center; gap: 20px; }}
    .brand-title {{
        color: #FFFFFF;
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin: 0;
        line-height: 1.2;
    }}
    .brand-subtitle {{
        color: #D1D5DB;
        font-size: 0.9rem;
        margin: 5px 0 0 0;
    }}
    .brand-badge {{
        background-color: rgba(243, 112, 33, 0.14);
        color: {GRQ_ORANGE};
        border: 1px solid {GRQ_ORANGE};
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
    }}

    /* Metric Cards */
    .stMetric {{
        background-color: #1D2023;
        border: 1px solid #3A3F42;
        border-top: 3px solid {GRQ_ORANGE};
        padding: 16px;
        border-radius: 8px;
    }}

    /* Insight & Advies Blokken */
    .insight-box {{
        background-color: #1D2023;
        border: 1px solid #3A3F42;
        border-left: 4px solid {GRQ_ORANGE};
        padding: 18px 22px;
        border-radius: 8px;
        margin-bottom: 16px;
        line-height: 1.65;
    }}

    /* Tabbladen styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        border-bottom: 1px solid #3A3F42;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #1D2023;
        border-radius: 6px 6px 0 0;
        padding: 10px 18px;
        color: #9CA3AF;
        border: 1px solid transparent;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {GRQ_ORANGE} !important;
        color: #FFFFFF !important;
        font-weight: 600;
        border: 1px solid {GRQ_ORANGE} !important;
    }}

    /* Footer */
    .brand-footer {{
        margin-top: 48px;
        padding-top: 16px;
        border-top: 1px solid #3A3F42;
        display: flex;
        justify-content: space-between;
        color: #9CA3AF;
        font-size: 0.8rem;
    }}
    </style>
""", unsafe_allow_html=True)

# Groningen Airport Eelde SVG Beeldmerk (de 6 karakteristieke oranje ovalen)
GRQ_ICON_SVG = """
<svg width="46" height="58" viewBox="0 0 80 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Binnenste boog (3 ovalen) -->
  <ellipse cx="14" cy="60" rx="7" ry="15" transform="rotate(24 14 60)" fill="#F37021"/>
  <ellipse cx="32" cy="33" rx="5.5" ry="11.5" transform="rotate(38 32 33)" fill="#F37021"/>
  <ellipse cx="52" cy="15" rx="3.8" ry="8.5" transform="rotate(50 52 15)" fill="#F37021"/>
  <!-- Buitenste boog (3 grotere ovalen) -->
  <ellipse cx="26" cy="80" rx="10.5" ry="19" transform="rotate(22 26 80)" fill="#F37021"/>
  <ellipse cx="48" cy="40" rx="8.5" ry="16.5" transform="rotate(36 48 40)" fill="#F37021"/>
  <ellipse cx="68" cy="11" rx="6" ry="13.5" transform="rotate(48 68 11)" fill="#F37021"/>
</svg>
"""

def style_fig(fig):
    """Maakt Plotly-grafieken strak en transparant in GRQ-stijl."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F3F4F6"),
        xaxis=dict(gridcolor="#2B3035", zerolinecolor="#3A3F42"),
        yaxis=dict(gridcolor="#2B3035", zerolinecolor="#3A3F42"),
        margin=dict(t=45, b=30, l=20, r=20)
    )
    return fig

# Sidebar Branding
with st.sidebar:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; padding-bottom:16px; border-bottom:1px solid #3A3F42; margin-bottom:18px;">
            {GRQ_ICON_SVG}
            <div style="line-height:1.25;">
                <div style="font-weight:700; font-size:0.95rem; letter-spacing:0.08em; color:#FFFFFF;">GRONINGEN</div>
                <div style="font-weight:700; font-size:0.95rem; letter-spacing:0.08em; color:#FFFFFF;">AIRPORT EELDE</div>
                <div style="font-size:0.75rem; color:{GRQ_ORANGE}; margin-top:3px; font-weight:600;">Route Development Suite</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Hoofdheader
st.markdown(f"""
    <div class="brand-header">
        <div class="brand-left">
            {GRQ_ICON_SVG}
            <div>
                <div class="brand-title">GRONINGEN AIRPORT EELDE</div>
                <div class="brand-subtitle">Route Proposal & Market Analysis — Catchment Leakage, Airport Choice & Netwerkconnectiviteit</div>
            </div>
        </div>
        <div class="brand-badge">GRQ / EHGG</div>
    </div>
""", unsafe_allow_html=True)

# 1. Excel Bestand Inladen
@st.cache_data
def load_all_sheets(file_source):
    try:
        xls = pd.ExcelFile(file_source)
        sheets_data = {}
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(xls, sheet_name=sheet)
                df.columns = df.columns.astype(str).str.strip()
                sheets_data[sheet] = df
            except Exception:
                sheets_data[sheet] = pd.DataFrame()
        return sheets_data
    except Exception as e:
        st.error(f"Fout bij het laden van het bestand: {e}")
        return None

def find_col(df, candidates):
    if df.empty:
        return None
    for c in candidates:
        if c in df.columns:
            return c
    lower_map = {col.lower(): col for col in df.columns}
    for c in candidates:
        if c.lower() in lower_map:
            return lower_map[c.lower()]
    return None

def filter_by_keyword(df, keyword, col_candidates):
    if df.empty or not keyword:
        return pd.DataFrame()
    col = find_col(df, col_candidates)
    if not col:
        return pd.DataFrame()
    clean_kw = str(keyword).replace("GRQ-", "").replace("GRQ - ", "").strip()
    mask = df[col].astype(str).str.contains(clean_kw, case=False, na=False, regex=False)
    return df[mask]

uploaded_file = st.sidebar.file_uploader("Upload Excel-bestand (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("👈 Upload in de linkerzijbalk een Excel-bestand (`.xlsx`) om de route-analyse voor Groningen Airport Eelde te starten.")
    st.stop()

all_data = load_all_sheets(uploaded_file)

if not all_data:
    st.stop()

df_prop = all_data.get('Proposal Investigation', pd.DataFrame())
df_choice = all_data.get('Airport Choice', pd.DataFrame())
df_comp = all_data.get('Route Competitors', pd.DataFrame())
df_leak = all_data.get('Surface Leakage', pd.DataFrame())
df_conn = all_data.get('Weighted Connectivity', pd.DataFrame())

# 2. Tabs Structuur
tab_overview, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Route Business Case",
    "📍 Route Voorstellen", 
    "📊 Airport Choice Analysis", 
    "🥊 Route Competitors", 
    "💧 Surface Leakage", 
    "📅 Connectivity & Schedules"
])

# ==========================================
# TAB 0: INTEGRALE ROUTE BUSINESS CASE
# ==========================================
with tab_overview:
    st.header("🎯 Integrale Route Business Case & Vliegadvies")
    st.markdown("Selecteer een voorgestelde route of bestemming om alle databronnen samen te voegen tot één onderbouwing voor Groningen Airport Eelde.")

    route_options = []
    for df_src, cols in [
        (df_prop, ['Route', 'Destination', 'Routing']),
        (df_choice, ['Route', 'Destination']),
        (df_leak, ['Destination', 'Route'])
    ]:
        c_name = find_col(df_src, cols)
        if c_name:
            vals = df_src[c_name].dropna().astype(str).unique().tolist()
            for v in vals:
                if v not in route_options:
                    route_options.append(v)

    if not route_options:
        st.warning("Geen routes of bestemmingen gevonden om te koppelen. Controleer of je Excel-tabbladen kolommen zoals 'Route' of 'Destination' bevatten.")
    else:
        selected_route = st.selectbox("Kies een te analyseren route / bestemming:", route_options)
        
        sub_prop = filter_by_keyword(df_prop, selected_route, ['Route', 'Destination', 'Routing'])
        sub_choice = filter_by_keyword(df_choice, selected_route, ['Route', 'Destination'])
        sub_comp = filter_by_keyword(df_comp, selected_route, ['Routing', 'Route', 'Destination'])
        sub_leak = filter_by_keyword(df_leak, selected_route, ['Destination', 'Route'])
        sub_conn = filter_by_keyword(df_conn, selected_route, ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])

        # 1. Surface Leakage
        leak_val = 0
        if not sub_leak.empty and 'Pax leakage' in sub_leak.columns:
            leak_val = pd.to_numeric(sub_leak['Pax leakage'], errors='coerce').sum()
        max_leak = pd.to_numeric(df_leak['Pax leakage'], errors='coerce').max() if ('Pax leakage' in df_leak.columns and not df_leak.empty) else 1
        leak_score = min((leak_val / max_leak) * 100, 100) if max_leak > 0 else 50

        # 2. Airport Choice
        prob_bus = pd.to_numeric(sub_choice['Probability% Business'], errors='coerce').mean() if ('Probability% Business' in sub_choice.columns and not sub_choice.empty) else 0
        prob_nonbus = pd.to_numeric(sub_choice['Probability% Non-Business'], errors='coerce').mean() if ('Probability% Non-Business' in sub_choice.columns and not sub_choice.empty) else 0
        avg_prob = max(prob_bus, prob_nonbus, (prob_bus + prob_nonbus) / 2)
        if 0 < avg_prob <= 1:
            avg_prob *= 100
            prob_bus *= 100
            prob_nonbus *= 100
        choice_score = min(avg_prob, 100) if avg_prob > 0 else 50

        # 3. Connectivity / Transfer Potential
        conn_days = sub_conn[sub_conn['Day outbound'] != 'AverageDay'] if ('Day outbound' in sub_conn.columns and not sub_conn.empty) else sub_conn
        if conn_days.empty and not df_conn.empty:
            conn_days = df_conn[df_conn['Day outbound'] != 'AverageDay'] if 'Day outbound' in df_conn.columns else df_conn
        
        avg_trans = pd.to_numeric(conn_days['Transfer Potential'], errors='coerce').mean() if ('Transfer Potential' in conn_days.columns and not conn_days.empty) else 0
        if 0 < avg_trans <= 1:
            avg_trans *= 100
        conn_score = min(avg_trans, 100) if avg_trans > 0 else 50

        # 4. Concurrentie
        comp_freq = pd.to_numeric(sub_comp['Frequency per Week'], errors='coerce').sum() if ('Frequency per Week' in sub_comp.columns and not sub_comp.empty) else 0
        comp_pax = pd.to_numeric(sub_comp['PAX from catchment'], errors='coerce').sum() if ('PAX from catchment' in sub_comp.columns and not sub_comp.empty) else 0

        total_score = round((0.40 * leak_score) + (0.35 * choice_score) + (0.25 * conn_score), 1)

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 GRQ Potentie Score", f"{total_score} / 100")
        k2.metric("💧 Surface Leakage (PAX)", f"{int(leak_val):,}".replace(",", ".") if leak_val > 0 else "Geen data")
        k3.metric("📊 Max GRQ Keuzekans", f"{avg_prob:.1f}%" if avg_prob > 0 else "Geen data")
        k4.metric("🥊 Concurrentie Freq/wk", f"{int(comp_freq)}x / week" if comp_freq > 0 else "0x (Unserved)")

        st.markdown("---")

        col_why, col_when = st.columns(2)

        with col_why:
            st.subheader("💡 Waarom scoort deze route goed?")
            reasons = []
            if leak_val > 0:
                reasons.append(f"• **Hoge terugwinbare vraag:** Er lekken momenteel **{int(leak_val):,} passagiers** uit het Noord-Nederlandse verzorgingsgebied weg naar concurrerende luchthavens.".replace(",", "."))
            if prob_bus > 0 or prob_nonbus > 0:
                dom_segment = "Zakelijke reizigers (Business)" if prob_bus > prob_nonbus else "Vakantie/VFR-reizigers (Non-Business)"
                reasons.append(f"• **Sterke GRQ-voorkeur:** Groningen Airport Eelde behaalt een keuzekans van **{prob_bus:.1f}% (Business)** en **{prob_nonbus:.1f}% (Non-Business)**. Het primaire segment is **{dom_segment}**.")
            if comp_freq == 0:
                reasons.append("• **Geen directe overlap:** Er is geen directe concurrentie vanuit het primaire catchment geregistreerd, wat ruimte biedt voor een sterke marktpositie.")
            else:
                reasons.append(f"• **Bewezen marktvraag:** Concurrerende routings bedienen dit segment al met **{int(comp_freq)} vluchten per week** ({int(comp_pax):,} PAX uit catchment), wat aantoont dat de markt actief is.".replace(",", "."))
            if avg_trans > 0:
                reasons.append(f"• **Netwerkwaarde:** Gemiddeld **{avg_trans:.1f}% transferpotentieel** via aansluitende vluchten vergroot de bezettingsgraad buiten lokaal O&D-verkeer.")

            if not reasons:
                reasons.append("• Upload aanvullende rijen voor deze bestemming in de tabbladen *Surface Leakage*, *Airport Choice* en *Route Competitors* om alle factoren te berekenen.")

            st.markdown(f"<div class='insight-box'>{'<br><br>'.join(reasons)}</div>", unsafe_allow_html=True)

        with col_when:
            st.subheader("🕒 Wanneer is deze route het best te vliegen?")
            schedule_advice = []

            if not conn_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(conn_days.columns):
                day_perf = conn_days.groupby('Day outbound', as_index=False)['Transfer Potential'].mean()
                day_perf = day_perf.sort_values(by='Transfer Potential', ascending=False)
                top_days = day_perf.head(3)
                days_formatted = ", ".join([f"**{row['Day outbound']}** ({row['Transfer Potential']*100 if row['Transfer Potential']<=1 else row['Transfer Potential']:.1f}%)" for _, row in top_days.iterrows()])
                schedule_advice.append(f"• **Beste dagen voor hub-connectiviteit:** {days_formatted} bieden de hoogste aansluitingswaarde.")

            pax_type = ""
            if not sub_prop.empty and 'PAX Type' in sub_prop.columns:
                pax_type = str(sub_prop['PAX Type'].iloc[0])
            elif prob_bus > prob_nonbus:
                pax_type = "Business"
            elif prob_nonbus > 0:
                pax_type = "Non-Business"

            if "Business" in pax_type and "Non" not in pax_type:
                schedule_advice.append("• **Segment-advies (Business):** Vlieg bij voorkeur op **maandagochtend, donderdagavond en vrijdag** met ochtend-/avondrotaties zodat zakelijke reizigers een eendaagse of meerdaagse trip kunnen maken.")
            elif "Non-Business" in pax_type:
                schedule_advice.append("• **Segment-advies (Leisure / VFR):** Focus op **vrijdag, zaterdag en zondag** (plus eventueel maandag/woensdag voor midweek-vakanties) om maximaal te profiteren van weekend- en vakantiespreiding.")

            fleet_col = find_col(sub_conn, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col and not sub_conn.empty:
                rec_fleet = sub_conn[fleet_col].mode()[0]
                schedule_advice.append(f"• **Aanbevolen toesteltype:** Op basis van de netwerkdata sluit een **{rec_fleet}** het beste aan op de capaciteits- en baanvereisten van GRQ (2.500m baanlengte).")

            if not schedule_advice:
                schedule_advice.append("• Voeg weekdagen en Transfer Potential toe in het tabblad *Weighted Connectivity* voor een specifiek dag- en tijdstipadvies.")

            st.markdown(f"<div class='insight-box'>{'<br><br>'.join(schedule_advice)}</div>", unsafe_allow_html=True)

        vis1, vis2 = st.columns(2)
        with vis1:
            st.subheader("Opbouw van de GRQ Potentie")
            df_radar = pd.DataFrame({
                'Factor': ['Surface Leakage (Vraag)', 'Airport Choice (Voorkeur)', 'Netwerk Connectivity'],
                'Score': [round(leak_score, 1), round(choice_score, 1), round(conn_score, 1)]
            })
            fig_factors = px.bar(
                df_radar,
                x='Score',
                y='Factor',
                orientation='h',
                range_x=[0, 100],
                text_auto=True,
                color_discrete_sequence=[GRQ_ORANGE],
                title=f"Deelscores voor {selected_route} (0-100)"
            )
            st.plotly_chart(style_fig(fig_factors), use_container_width=True)

        with vis2:
            st.subheader("Transfer Potentieel per Dag (Beste Vliegdagen)")
            if not conn_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(conn_days.columns):
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                             'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
                fig_days = px.bar(
                    conn_days,
                    x='Day outbound',
                    y='Transfer Potential',
                    color='Airline' if 'Airline' in conn_days.columns else None,
                    barmode='group',
                    category_orders={'Day outbound': day_order},
                    color_discrete_sequence=GRQ_PALETTE,
                    title="Connectiviteit per Weekdag"
                )
                st.plotly_chart(style_fig(fig_days), use_container_width=True)
            else:
                st.info("Geen weekdag-data beschikbaar in 'Weighted Connectivity'.")

        st.markdown("---")
        st.subheader("📋 Overzicht Voorgestelde Routes vanaf Groningen Airport Eelde")
        if not df_prop.empty:
            st.dataframe(df_prop, use_container_width=True, hide_index=True)

# ==========================================
# TAB 1: PROPOSAL INVESTIGATION
# ==========================================
with tab1:
    st.header("📍 Voorgestelde Routes (Proposal Investigation)")
    if not df_prop.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Totaal Voorgestelde Routes", len(df_prop))
        if 'PAX Type' in df_prop.columns:
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
    if not df_choice.empty:
        col_l, col_r = st.columns(2)
        
        with col_l:
            st.subheader("Business Passagiers per Route")
            if {'Route', 'Probability% Business', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_bus = px.bar(
                    df_choice, 
                    x='Route', 
                    y='Probability% Business', 
                    color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE, GRQ_SLATE],
                    title="Business PAX per Route"
                )
                st.plotly_chart(style_fig(fig_bus), use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_choice.columns)}")

        with col_r:
            st.subheader("Non-Business Passagiers per Route")
            if {'Route', 'Probability% Non-Business', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_nonbus = px.bar(
                    df_choice, 
                    x='Route', 
                    y='Probability% Non-Business', 
                    color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE_LIGHT, GRQ_CHARCOAL],
                    title="Non-Business PAX per Route"
                )
                st.plotly_chart(style_fig(fig_nonbus), use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_choice.columns)}")

        st.dataframe(df_choice, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Airport Choice'.")

# ==========================================
# TAB 3: ROUTE COMPETITORS
# ==========================================
with tab3:
    st.header("🥊 Concurrentie & Route Eigenschappen")
    if not df_comp.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Frequentie per Week per Routing")
            if {'Routing', 'Frequency per Week', 'Catchment'}.issubset(df_comp.columns):
                fig_freq = px.bar(
                    df_comp, 
                    x='Routing', 
                    y='Frequency per Week', 
                    color='Catchment',
                    color_discrete_sequence=GRQ_PALETTE,
                    title="Wekelijkse Frequentie"
                )
                st.plotly_chart(style_fig(fig_freq), use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_comp.columns)}")

        with c2:
            st.subheader("PAX uit Catchment per Routing")
            if {'Routing', 'PAX from catchment'}.issubset(df_comp.columns):
                fig_pax = px.bar(
                    df_comp, 
                    x='Routing', 
                    y='PAX from catchment',
                    color_discrete_sequence=[GRQ_ORANGE],
                    title="Passagiers uit Catchment Zone"
                )
                st.plotly_chart(style_fig(fig_pax), use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_comp.columns)}")

        st.dataframe(df_comp, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Route Competitors'.")

# ==========================================
# TAB 4: SURFACE LEAKAGE
# ==========================================
with tab4:
    st.header("💧 Surface Leakage (Passagierslekkage naar andere luchthavens)")
    if not df_leak.empty:
        st.subheader("Top Bestemmingen met Hoogste Passagierslekkage")
        if {'Destination', 'Pax leakage', 'Region'}.issubset(df_leak.columns):
            fig_leak = px.bar(
                df_leak.sort_values(by='Pax leakage', ascending=False).head(15), 
                x='Destination', 
                y='Pax leakage', 
                color='Region',
                text_auto=True,
                color_discrete_sequence=GRQ_PALETTE,
                title="Pax Leakage per Bestemming"
            )
            st.plotly_chart(style_fig(fig_leak), use_container_width=True)
        else:
            st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_leak.columns)}")

        st.dataframe(df_leak, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Surface Leakage'.")

# ==========================================
# TAB 5: WEIGHTED CONNECTIVITY & SCHEDULES
# ==========================================
with tab5:
    st.header("📅 Netwerk Connectivity & Vliegschema's")
    if not df_conn.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Transfer Potentieel % per Dag & Maatschappij")
            if {'Day outbound', 'Transfer Potential', 'Airline'}.issubset(df_conn.columns):
                fig_trans = px.line(
                    df_conn[df_conn['Day outbound'] != 'AverageDay'], 
                    x='Day outbound', 
                    y='Transfer Potential', 
                    color='Airline',
                    markers=True,
                    color_discrete_sequence=GRQ_PALETTE,
                    title="Transfer Potential % gedurende de week"
                )
                st.plotly_chart(style_fig(fig_trans), use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_conn.columns)}")
            
        with col2:
            st.subheader("Inzetbare Vloot (Fleet)")
            fleet_col = find_col(df_conn, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col:
                fleet_counts = df_conn[fleet_col].value_counts().reset_index()
                fleet_counts.columns = ['Fleet', 'Aantal']
                fig_fleet = px.pie(
                    fleet_counts, 
                    names='Fleet', 
                    values='Aantal', 
                    hole=0.4,
                    color_discrete_sequence=GRQ_PALETTE
                )
                st.plotly_chart(style_fig(fig_fleet), use_container_width=True)
            else:
                st.warning(f"Kolom 'Fleet' niet gevonden. Beschikbare kolommen: {list(df_conn.columns)}")

        st.dataframe(df_conn, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Weighted Connectivity'.")

# ==========================================
# BRAND FOOTER
# ==========================================
st.markdown("""
    <div class="brand-footer">
        <span><strong>Groningen Airport Eelde (GRQ)</strong> — Route Development & Network Analytics</span>
        <span>Powered by <strong>JR Aviation Solutions</strong></span>
    </div>
""", unsafe_allow_html=True)
