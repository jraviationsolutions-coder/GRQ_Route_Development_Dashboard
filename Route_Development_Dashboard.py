import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

st.set_page_config(
    page_title="Groningen Airport Eelde (GRQ) | Route Development",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GRQ Kleurenpalet (Light & Dark mode adaptief)
GRQ_ORANGE = "#F37021"
GRQ_ORANGE_LIGHT = "#FF9E5E"
GRQ_CHARCOAL = "#3A3F42"
GRQ_SLATE = "#64748B"
GRQ_TEAL = "#0D9488"
GRQ_PALETTE = [GRQ_ORANGE, "#334155", GRQ_TEAL, GRQ_ORANGE_LIGHT, "#94A3B8", "#D95D13"]

# Coördinaten-database voor luchthavens & Europese bestemmingen (voor de Route Competitors kaart)
AIRPORT_COORDS = {
    # Catchment / Concurrerende luchthavens
    "GRQ": (53.1197, 6.5794, "Groningen Airport Eelde (GRQ)"),
    "EHGG": (53.1197, 6.5794, "Groningen Airport Eelde (GRQ)"),
    "GRONINGEN": (53.1197, 6.5794, "Groningen Airport Eelde (GRQ)"),
    "AMS": (52.3105, 4.7683, "Amsterdam Schiphol (AMS)"),
    "EHAM": (52.3105, 4.7683, "Amsterdam Schiphol (AMS)"),
    "AMSTERDAM": (52.3105, 4.7683, "Amsterdam Schiphol (AMS)"),
    "EIN": (51.4501, 5.3745, "Eindhoven Airport (EIN)"),
    "EHEH": (51.4501, 5.3745, "Eindhoven Airport (EIN)"),
    "EINDHOVEN": (51.4501, 5.3745, "Eindhoven Airport (EIN)"),
    "RTM": (51.9569, 4.4372, "Rotterdam The Hague (RTM)"),
    "MST": (50.9117, 5.7701, "Maastricht Aachen (MST)"),
    "BRE": (53.0475, 8.7867, "Bremen Airport (BRE)"),
    "BREMEN": (53.0475, 8.7867, "Bremen Airport (BRE)"),
    "FMO": (52.1346, 7.6848, "Münster Osnabrück (FMO)"),
    "DUS": (51.2895, 6.7668, "Düsseldorf Airport (DUS)"),
    "NRN": (51.6024, 6.1422, "Weeze Airport (NRN)"),
    "HAM": (53.6304, 9.9882, "Hamburg Airport (HAM)"),
    "HAJ": (52.4611, 9.6850, "Hannover Airport (HAJ)"),
    "BRU": (50.9010, 4.4856, "Brussels Airport (BRU)"),
    "CRL": (50.4592, 4.4538, "Brussels South Charleroi (CRL)"),
    # Veelvoorkomende Europese bestemmingen
    "STN": (51.8860, 0.2389, "London Stansted (STN)"),
    "SEN": (51.5714, 0.6956, "London Southend (SEN)"),
    "LHR": (51.4700, -0.4543, "London Heathrow (LHR)"),
    "LGW": (51.1537, -0.1821, "London Gatwick (LGW)"),
    "LCY": (51.5048, 0.0495, "London City (LCY)"),
    "LONDON": (51.8860, 0.2389, "London (STN/LCY)"),
    "LONDEN": (51.8860, 0.2389, "Londen (STN/LCY)"),
    "AGP": (36.6749, -4.4991, "Málaga (AGP)"),
    "MALAGA": (36.6749, -4.4991, "Málaga (AGP)"),
    "ALC": (38.2822, -0.5582, "Alicante (ALC)"),
    "ALICANTE": (38.2822, -0.5582, "Alicante (ALC)"),
    "PMI": (39.5517, 2.7388, "Palma de Mallorca (PMI)"),
    "PALMA": (39.5517, 2.7388, "Palma de Mallorca (PMI)"),
    "BCN": (41.2974, 2.0833, "Barcelona (BCN)"),
    "BARCELONA": (41.2974, 2.0833, "Barcelona (BCN)"),
    "MAD": (40.4983, -3.5676, "Madrid (MAD)"),
    "FAO": (37.0144, -7.9659, "Faro (FAO)"),
    "FARO": (37.0144, -7.9659, "Faro (FAO)"),
    "LIS": (38.7756, -9.1354, "Lissabon (LIS)"),
    "CPH": (55.6180, 12.6508, "Kopenhagen (CPH)"),
    "COPENHAGEN": (55.6180, 12.6508, "Kopenhagen (CPH)"),
    "KOPENHAGEN": (55.6180, 12.6508, "Kopenhagen (CPH)"),
    "OSL": (60.1976, 11.1004, "Oslo (OSL)"),
    "ARN": (59.6498, 17.9238, "Stockholm (ARN)"),
    "MUC": (48.3537, 11.7750, "München (MUC)"),
    "MUNICH": (48.3537, 11.7750, "München (MUC)"),
    "FRA": (50.0379, 8.5622, "Frankfurt (FRA)"),
    "BER": (52.3667, 13.5033, "Berlijn (BER)"),
    "INN": (47.2602, 11.3440, "Innsbruck (INN)"),
    "INNSBRUCK": (47.2602, 11.3440, "Innsbruck (INN)"),
    "SZG": (47.7933, 13.0043, "Salzburg (SZG)"),
    "VIE": (48.1103, 16.5697, "Wenen (VIE)"),
    "ZRH": (47.4582, 8.5555, "Zürich (ZRH)"),
    "GVA": (46.2370, 6.1092, "Genève (GVA)"),
    "GDN": (54.3776, 18.4662, "Gdańsk (GDN)"),
    "GDANSK": (54.3776, 18.4662, "Gdańsk (GDN)"),
    "WAW": (52.1672, 20.9679, "Warschau (WAW)"),
    "KRK": (50.0777, 19.7848, "Krakau (KRK)"),
    "SPU": (43.5389, 16.2980, "Split (SPU)"),
    "SPLIT": (43.5389, 16.2980, "Split (SPU)"),
    "DBV": (42.5614, 18.2682, "Dubrovnik (DBV)"),
    "FCO": (41.8003, 12.2389, "Rome (FCO)"),
    "MXP": (45.6301, 8.7255, "Milaan (MXP)"),
    "CDG": (49.0097, 2.5479, "Parijs (CDG)"),
    "DUB": (53.4264, -6.2499, "Dublin (DUB)"),
    "EDI": (55.9508, -3.3615, "Edinburgh (EDI)"),
    "MAN": (53.3588, -2.2727, "Manchester (MAN)"),
    "ABZ": (57.2019, -2.1978, "Aberdeen (ABZ)"),
    "ACE": (28.9455, -13.6052, "Lanzarote (ACE)"),
    "TFS": (28.0445, -16.5725, "Tenerife (TFS)"),
    "LPA": (27.9319, -15.3866, "Gran Canaria (LPA)"),
    "HER": (35.3397, 25.1803, "Heraklion (HER)"),
    "AYT": (36.8987, 30.8005, "Antalya (AYT)")
}

# Adaptieve CSS voor Light & Dark mode
st.markdown(f"""<style>
.main {{ padding: 1.2rem 2rem; }}
h1, h2, h3 {{ letter-spacing: 0.01em; font-weight: 600; }}

.brand-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-left: 6px solid {GRQ_ORANGE};
    border-radius: 10px;
    padding: 16px 24px;
    margin-bottom: 20px;
}}
.brand-left {{ display: flex; align-items: center; gap: 18px; }}
.brand-title {{
    color: var(--text-color);
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 0;
    line-height: 1.2;
}}
.brand-subtitle {{
    color: var(--text-color);
    opacity: 0.75;
    font-size: 0.88rem;
    margin: 4px 0 0 0;
}}
.brand-badge {{
    background-color: rgba(243, 112, 33, 0.12);
    color: {GRQ_ORANGE};
    border: 1px solid {GRQ_ORANGE};
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    white-space: nowrap;
}}

[data-testid="stMetric"] {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-top: 3px solid {GRQ_ORANGE};
    padding: 14px 16px;
    border-radius: 8px;
}}

.signal-card {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-left: 4px solid {GRQ_ORANGE};
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 10px;
}}
.signal-label {{
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    opacity: 0.7;
    font-weight: 600;
}}
.signal-value {{
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-color);
    margin-top: 2px;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
}}
.stTabs [data-baseweb="tab"] {{
    background-color: var(--secondary-background-color);
    border-radius: 6px 6px 0 0;
    padding: 9px 16px;
    color: var(--text-color);
    opacity: 0.8;
    border: 1px solid rgba(128, 128, 128, 0.15);
}}
.stTabs [aria-selected="true"] {{
    background-color: {GRQ_ORANGE} !important;
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 600;
    border: 1px solid {GRQ_ORANGE} !important;
}}

.brand-footer {{
    margin-top: 40px;
    padding-top: 14px;
    border-top: 1px solid rgba(128, 128, 128, 0.25);
    display: flex;
    justify-content: space-between;
    color: var(--text-color);
    opacity: 0.65;
    font-size: 0.8rem;
}}
</style>""", unsafe_allow_html=True)

GRQ_ICON_SVG = '<svg width="44" height="54" viewBox="0 0 80 100" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="14" cy="60" rx="7" ry="15" transform="rotate(24 14 60)" fill="#F37021"/><ellipse cx="32" cy="33" rx="5.5" ry="11.5" transform="rotate(38 32 33)" fill="#F37021"/><ellipse cx="52" cy="15" rx="3.8" ry="8.5" transform="rotate(50 52 15)" fill="#F37021"/><ellipse cx="26" cy="80" rx="10.5" ry="19" transform="rotate(22 26 80)" fill="#F37021"/><ellipse cx="48" cy="40" rx="8.5" ry="16.5" transform="rotate(36 48 40)" fill="#F37021"/><ellipse cx="68" cy="11" rx="6" ry="13.5" transform="rotate(48 68 11)" fill="#F37021"/></svg>'

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(128,128,128,0.18)", zerolinecolor="rgba(128,128,128,0.3)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.18)", zerolinecolor="rgba(128,128,128,0.3)"),
        margin=dict(t=42, b=28, l=16, r=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# Sidebar Branding
with st.sidebar:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; padding-bottom:14px; border-bottom:1px solid rgba(128,128,128,0.25); margin-bottom:16px;">'
        f'{GRQ_ICON_SVG}'
        f'<div style="line-height:1.25;">'
        f'<div style="font-weight:700; font-size:0.95rem; letter-spacing:0.08em;">GRONINGEN</div>'
        f'<div style="font-weight:700; font-size:0.95rem; letter-spacing:0.08em;">AIRPORT EELDE</div>'
        f'<div style="font-size:0.75rem; color:{GRQ_ORANGE}; margin-top:2px; font-weight:600;">Route Development Suite</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

# Hoofdheader
st.markdown(
    f'<div class="brand-header">'
    f'<div class="brand-left">{GRQ_ICON_SVG}'
    f'<div>'
    f'<div class="brand-title">GRONINGEN AIRPORT EELDE</div>'
    f'<div class="brand-subtitle">Route Development & Market Intelligence Dashboard</div>'
    f'</div></div>'
    f'<div class="brand-badge">GRQ / EHGG</div>'
    f'</div>',
    unsafe_allow_html=True
)

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

def clean_route_name(val):
    return str(val).replace("GRQ-", "").replace("GRQ - ", "").strip()

def filter_df_multi(df, selected_list, col_candidates):
    if df.empty or not selected_list:
        return df
    col = find_col(df, col_candidates)
    if not col:
        return df
    patterns = [clean_route_name(item) for item in selected_list]
    mask = df[col].astype(str).apply(lambda x: any(p.lower() in x.lower() for p in patterns))
    return df[mask]

def resolve_coords(text):
    """Zoekt luchthaven- of stadsenamen in een string (bijv. 'AMS-AGP' of 'Amsterdam') en geeft (lat, lon, label)."""
    if not text:
        return None
    txt_upper = str(text).upper().strip()
    if txt_upper in AIRPORT_COORDS:
        return AIRPORT_COORDS[txt_upper]
    tokens = re.split(r'[^A-Z0-9]+', txt_upper)
    for tok in tokens:
        if tok in AIRPORT_COORDS and tok not in ["GRQ", "EHGG"]:
            return AIRPORT_COORDS[tok]
    for key, coords in AIRPORT_COORDS.items():
        if len(key) > 3 and key in txt_upper:
            return coords
    return None

uploaded_file = st.sidebar.file_uploader("📂 Upload Excel-bestand (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("👈 Upload in de linkerzijbalk het Excel-bestand (`.xlsx`) om de interactieve route-analyse te openen.")
    st.stop()

all_data = load_all_sheets(uploaded_file)
if not all_data:
    st.stop()

df_prop_raw = all_data.get('Proposal Investigation', pd.DataFrame())
df_choice_raw = all_data.get('Airport Choice', pd.DataFrame())
df_comp_raw = all_data.get('Route Competitors', pd.DataFrame())
df_leak_raw = all_data.get('Surface Leakage', pd.DataFrame())
df_conn_raw = all_data.get('Weighted Connectivity', pd.DataFrame())

# ==========================================
# UITSLUITEND BESTEMMINGEN UIT TABBLAD 1 (PROPOSAL INVESTIGATION)
# ==========================================
prop_destinations = []
prop_col = find_col(df_prop_raw, ['Route', 'Destination', 'Routing'])
if prop_col and not df_prop_raw.empty:
    seen = set()
    for val in df_prop_raw[prop_col].dropna().unique():
        cleaned = clean_route_name(val)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            prop_destinations.append(cleaned)

# ==========================================
# GLOBALE FILTERS IN DE ZIJBALK
# ==========================================
st.sidebar.markdown("### 🔍 Globale Filters")

selected_dests = st.sidebar.multiselect(
    "Filter op Voorgestelde Route(s) (Tab 1)",
    options=prop_destinations,
    default=[],
    placeholder="Alle routes uit Tab 1 tonen..."
)

pax_types = []
if not df_prop_raw.empty and 'PAX Type' in df_prop_raw.columns:
    pax_types = sorted(df_prop_raw['PAX Type'].dropna().unique().tolist())
selected_pax = st.sidebar.multiselect(
    "Filter op Segment (PAX Type)",
    options=pax_types,
    default=pax_types
) if pax_types else []

min_leakage = 0
if not df_leak_raw.empty and 'Pax leakage' in df_leak_raw.columns:
    max_l = int(pd.to_numeric(df_leak_raw['Pax leakage'], errors='coerce').max() or 0)
    if max_l > 0:
        min_leakage = st.sidebar.slider("Min. Surface Leakage (PAX)", 0, max_l, 0, step=max(1, max_l // 20))

# Filter Tabblad 1 en bepaal actieve lijst van bestemmingen uit Tabblad 1
df_prop = filter_df_multi(df_prop_raw, selected_dests, ['Route', 'Destination', 'Routing'])
if selected_pax and not df_prop.empty and 'PAX Type' in df_prop.columns:
    df_prop = df_prop[df_prop['PAX Type'].isin(selected_pax)]

active_tab1_dests = []
if prop_col and not df_prop.empty:
    seen_active = set()
    for val in df_prop[prop_col].dropna().unique():
        cleaned = clean_route_name(val)
        if cleaned and cleaned not in seen_active:
            seen_active.add(cleaned)
            active_tab1_dests.append(cleaned)

# Filter overige tabbladen op basis van geselecteerde routes
filter_target = selected_dests if selected_dests else []
df_choice = filter_df_multi(df_choice_raw, filter_target, ['Route', 'Destination'])
df_comp = filter_df_multi(df_comp_raw, filter_target, ['Routing', 'Route', 'Destination'])
df_leak = filter_df_multi(df_leak_raw, filter_target, ['Destination', 'Route'])
if min_leakage > 0 and not df_leak.empty and 'Pax leakage' in df_leak.columns:
    df_leak = df_leak[pd.to_numeric(df_leak['Pax leakage'], errors='coerce') >= min_leakage]
df_conn = filter_df_multi(df_conn_raw, filter_target, ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])

# ==========================================
# BEREKEN GECOMBINEERDE BESLISMATRIX (ALLEEN TABBLAD 1 BESTEMMINGEN)
# ==========================================
def build_route_summary(dest_list):
    max_leak = pd.to_numeric(df_leak_raw['Pax leakage'], errors='coerce').max() if ('Pax leakage' in df_leak_raw.columns and not df_leak_raw.empty) else 1
    rows = []
    for dest in dest_list:
        s_prop = filter_df_multi(df_prop_raw, [dest], ['Route', 'Destination', 'Routing'])
        s_choice = filter_df_multi(df_choice_raw, [dest], ['Route', 'Destination'])
        s_comp = filter_df_multi(df_comp_raw, [dest], ['Routing', 'Route', 'Destination'])
        s_leak = filter_df_multi(df_leak_raw, [dest], ['Destination', 'Route'])
        s_conn = filter_df_multi(df_conn_raw, [dest], ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])

        leak_v = pd.to_numeric(s_leak['Pax leakage'], errors='coerce').sum() if ('Pax leakage' in s_leak.columns and not s_leak.empty) else 0
        leak_sc = min((leak_v / max_leak) * 100, 100) if max_leak > 0 else 0

        p_bus = pd.to_numeric(s_choice['Probability% Business'], errors='coerce').mean() if ('Probability% Business' in s_choice.columns and not s_choice.empty) else 0
        p_non = pd.to_numeric(s_choice['Probability% Non-Business'], errors='coerce').mean() if ('Probability% Non-Business' in s_choice.columns and not s_choice.empty) else 0
        if 0 < p_bus <= 1: p_bus *= 100
        if 0 < p_non <= 1: p_non *= 100
        best_prob = max(p_bus, p_non)

        c_days = s_conn[s_conn['Day outbound'] != 'AverageDay'] if ('Day outbound' in s_conn.columns and not s_conn.empty) else s_conn
        if c_days.empty and not df_conn_raw.empty:
            c_days = df_conn_raw[df_conn_raw['Day outbound'] != 'AverageDay'] if 'Day outbound' in df_conn_raw.columns else df_conn_raw
        
        avg_tr = pd.to_numeric(c_days['Transfer Potential'], errors='coerce').mean() if ('Transfer Potential' in c_days.columns and not c_days.empty) else 0
        if 0 < avg_tr <= 1: avg_tr *= 100

        best_day = "-"
        if not c_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(c_days.columns):
            d_grp = c_days.groupby('Day outbound', as_index=False)['Transfer Potential'].mean().sort_values(by='Transfer Potential', ascending=False)
            if not d_grp.empty:
                best_day = str(d_grp.iloc[0]['Day outbound'])

        c_freq = pd.to_numeric(s_comp['Frequency per Week'], errors='coerce').sum() if ('Frequency per Week' in s_comp.columns and not s_comp.empty) else 0
        pax_seg = str(s_prop['PAX Type'].iloc[0]) if ('PAX Type' in s_prop.columns and not s_prop.empty) else ("Business" if p_bus > p_non else "Non-Business")

        score = round((0.40 * leak_sc) + (0.35 * min(best_prob, 100)) + (0.25 * min(avg_tr, 100)), 1)
        rows.append({
            "Voorgestelde Route (Tab 1)": dest,
            "Potentie Score": score,
            "Segment": pax_seg,
            "Surface Leakage": int(leak_v),
            "Business Kans %": round(p_bus, 1),
            "Leisure Kans %": round(p_non, 1),
            "Transfer Potentieel %": round(avg_tr, 1),
            "Concurrentie (vl/wk)": int(c_freq),
            "Beste Vliegdag": best_day
        })
    return pd.DataFrame(rows).sort_values(by="Potentie Score", ascending=False) if rows else pd.DataFrame()

df_matrix = build_route_summary(active_tab1_dests)

# ==========================================
# TABS STRUCTUUR
# ==========================================
tab_overview, tab_single, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Gecombineerde Beslismatrix",
    "🎯 Bestemming Deep-Dive",
    "📍 Route Voorstellen (Tab 1)", 
    "🧭 Airport Choice", 
    "🥊 Route Competitors (Kaart)", 
    "💧 Surface Leakage", 
    "📅 Connectivity & Vloot"
])

# ==========================================
# TAB 0: GECOMBINEERDE BESLISMATRIX (ALLEEN TAB 1)
# ==========================================
with tab_overview:
    st.subheader("📊 Gecombineerde Beslismatrix (Uitsluitend Routes uit Tabblad 1)")

    if df_matrix.empty:
        st.warning("Geen voorgestelde routes gevonden in Tabblad 1 ('Proposal Investigation') voor deze filterselectie.")
    else:
        top_route = df_matrix.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🥇 Hoogst Scorende Voorstel", top_route["Voorgestelde Route (Tab 1)"], f"{top_route['Potentie Score']} / 100 pt")
        m2.metric("💧 Totale Surface Leakage", f"{df_matrix['Surface Leakage'].sum():,}".replace(",", "."))
        m3.metric("📈 Gem. GRQ Keuzekans", f"{df_matrix[['Business Kans %', 'Leisure Kans %']].max(axis=1).mean():.1f}%")
        m4.metric("✈️ Routes uit Tabblad 1", len(df_matrix))

        g1, g2 = st.columns(2)
        with g1:
            fig_rank = px.bar(
                df_matrix,
                x="Potentie Score",
                y="Voorgestelde Route (Tab 1)",
                orientation="h",
                color="Segment",
                text_auto=True,
                color_discrete_sequence=[GRQ_ORANGE, GRQ_SLATE, GRQ_TEAL],
                title="Ranking Voorgestelde Routes (Tab 1) op Potentie Score"
            )
            fig_rank.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(fig_rank), use_container_width=True)

        with g2:
            fig_bubble = px.scatter(
                df_matrix,
                x="Surface Leakage",
                y="Business Kans %" if df_matrix["Business Kans %"].sum() > df_matrix["Leisure Kans %"].sum() else "Leisure Kans %",
                size="Potentie Score",
                color="Segment",
                text="Voorgestelde Route (Tab 1)",
                color_discrete_sequence=[GRQ_ORANGE, GRQ_TEAL, GRQ_SLATE],
                title="Vraag (Leakage) vs. GRQ Voorkeur (Bubbel = Score)"
            )
            fig_bubble.update_traces(textposition='top center')
            st.plotly_chart(style_fig(fig_bubble), use_container_width=True)

        st.dataframe(
            df_matrix,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Potentie Score": st.column_config.ProgressColumn(
                    "Potentie Score", format="%.1f", min_value=0, max_value=100
                ),
                "Surface Leakage": st.column_config.NumberColumn("Surface Leakage (PAX)", format="%d"),
                "Business Kans %": st.column_config.NumberColumn("Business %", format="%.1f%%"),
                "Leisure Kans %": st.column_config.NumberColumn("Leisure %", format="%.1f%%"),
                "Transfer Potentieel %": st.column_config.NumberColumn("Transfer %", format="%.1f%%"),
            }
        )

# ==========================================
# TAB 1: LOSSE BESTEMMING DEEP-DIVE
# ==========================================
with tab_single:
    if not active_tab1_dests:
        st.warning("Geen routes beschikbaar in Tabblad 1.")
    else:
        col_sel, _ = st.columns([1, 2])
        with col_sel:
            chosen_dest = st.selectbox("🎯 Selecteer één route uit Tabblad 1:", active_tab1_dests)
        
        row_dest = df_matrix[df_matrix["Voorgestelde Route (Tab 1)"] == chosen_dest].iloc[0]
        s_conn = filter_df_multi(df_conn_raw, [chosen_dest], ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])
        if s_conn.empty:
            s_conn = df_conn_raw

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 Potentie Score", f"{row_dest['Potentie Score']} / 100")
        k2.metric("💧 Terugwinbare PAX", f"{row_dest['Surface Leakage']:,}".replace(",", "."))
        k3.metric("🧭 Hoogste Keuzekans", f"{max(row_dest['Business Kans %'], row_dest['Leisure Kans %']):.1f}%")
        k4.metric("🥊 Concurrentie", f"{row_dest['Concurrentie (vl/wk)']} vl/wk")

        c_sig1, c_sig2, c_sig3, c_sig4 = st.columns(4)
        with c_sig1:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Primair Segment</div><div class="signal-value">{row_dest["Segment"]}</div></div>', unsafe_allow_html=True)
        with c_sig2:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Optimale Vliegdag</div><div class="signal-value">{row_dest["Beste Vliegdag"]}</div></div>', unsafe_allow_html=True)
        with c_sig3:
            adv_days = "Ma / Do / Vr" if "Business" in row_dest["Segment"] and "Non" not in row_dest["Segment"] else "Vr / Za / Zo"
            st.markdown(f'<div class="signal-card"><div class="signal-label">Aanbevolen Rotatie</div><div class="signal-value">{adv_days}</div></div>', unsafe_allow_html=True)
        with c_sig4:
            fleet_col = find_col(s_conn, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            rec_fleet = str(s_conn[fleet_col].mode()[0]) if (fleet_col and not s_conn.empty) else "E190 / B737-800"
            st.markdown(f'<div class="signal-card"><div class="signal-label">Geschikte Vloot</div><div class="signal-value">{rec_fleet}</div></div>', unsafe_allow_html=True)

        v1, v2 = st.columns(2)
        with v1:
            max_l_val = pd.to_numeric(df_leak_raw['Pax leakage'], errors='coerce').max() if ('Pax leakage' in df_leak_raw.columns and not df_leak_raw.empty) else 1
            l_norm = min((row_dest['Surface Leakage'] / max_l_val) * 100, 100) if max_l_val > 0 else 0
            c_norm = max(row_dest['Business Kans %'], row_dest['Leisure Kans %'])
            t_norm = row_dest['Transfer Potentieel %']

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[l_norm, c_norm, t_norm, max(0, 100 - row_dest['Concurrentie (vl/wk)'] * 10), l_norm],
                theta=['Vraag (Leakage)', 'GRQ Voorkeur', 'Transfer Netwerk', 'Marktruimte', 'Vraag (Leakage)'],
                fill='toself',
                line_color=GRQ_ORANGE,
                fillcolor='rgba(243, 112, 33, 0.25)'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(128,128,128,0.25)")),
                showlegend=False,
                title=f"Route Profiel: {chosen_dest}"
            )
            st.plotly_chart(style_fig(fig_radar), use_container_width=True)

        with v2:
            c_days = s_conn[s_conn['Day outbound'] != 'AverageDay'] if 'Day outbound' in s_conn.columns else s_conn
            if not c_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(c_days.columns):
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
                             'Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
                fig_d = px.bar(
                    c_days,
                    x='Day outbound',
                    y='Transfer Potential',
                    color='Airline' if 'Airline' in c_days.columns else None,
                    barmode='group',
                    category_orders={'Day outbound': day_order},
                    color_discrete_sequence=GRQ_PALETTE,
                    title=f"Beste Vliegdagen op basis van Connectiviteit ({chosen_dest})"
                )
                st.plotly_chart(style_fig(fig_d), use_container_width=True)
            else:
                st.info("Geen weekdag-data beschikbaar voor deze selectie.")

# ==========================================
# TAB 2: PROPOSAL INVESTIGATION (TAB 1 DATA)
# ==========================================
with tab1:
    st.subheader("📍 Voorgestelde Routes (Proposal Investigation)")
    if not df_prop.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Gefilterde Routes", len(df_prop))
        if 'PAX Type' in df_prop.columns:
            c2.metric("Business Routes", len(df_prop[df_prop['PAX Type'] == 'Business']))
            c3.metric("Non-Business / Leisure", len(df_prop[df_prop['PAX Type'] == 'Non-Business']))
        st.dataframe(df_prop, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar voor deze filterselectie.")

# ==========================================
# TAB 3: AIRPORT CHOICE ANALYSIS
# ==========================================
with tab2:
    st.subheader("🧭 Luchthaven Keuzekans (GRQ vs. Alternatieven)")
    if not df_choice.empty:
        col_l, col_r = st.columns(2)
        with col_l:
            if {'Route', 'Probability% Business', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_bus = px.bar(
                    df_choice, x='Route', y='Probability% Business', color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE, GRQ_SLATE], title="Business Keuzekans %"
                )
                st.plotly_chart(style_fig(fig_bus), use_container_width=True)
        with col_r:
            if {'Route', 'Probability% Non-Business', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_nonbus = px.bar(
                    df_choice, x='Route', y='Probability% Non-Business', color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE_LIGHT, GRQ_TEAL], title="Non-Business Keuzekans %"
                )
                st.plotly_chart(style_fig(fig_nonbus), use_container_width=True)
        st.dataframe(df_choice, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar voor deze filterselectie.")

# ==========================================
# TAB 4: ROUTE COMPETITORS (PER ROUTE + VERGROOTBARE LANDKAART)
# ==========================================
with tab3:
    st.subheader("🥊 Route Competitors — Concurrentie per Route op de Kaart")

    if df_comp_raw.empty:
        st.info("Geen data beschikbaar in 'Route Competitors'.")
    else:
        f_col1, f_col2, f_col3 = st.columns([1.3, 1.5, 1.0])
        with f_col1:
            comp_route_options = ["Alle routes uit Tabblad 1"] + prop_destinations
            sel_comp_route = st.selectbox("Selecteer mogelijke route (Tab 1):", comp_route_options)
        
        if sel_comp_route != "Alle routes uit Tabblad 1":
            df_comp_view = filter_df_multi(df_comp_raw, [sel_comp_route], ['Routing', 'Route', 'Destination'])
        else:
            df_comp_view = df_comp.copy()

        with f_col2:
            if 'Catchment' in df_comp_view.columns and not df_comp_view.empty:
                catchments = sorted(df_comp_view['Catchment'].dropna().unique().tolist())
                sel_catch = st.multiselect("Filter op Concurrerende Luchthaven / Catchment:", catchments, default=catchments)
                df_comp_view = df_comp_view[df_comp_view['Catchment'].isin(sel_catch)]

        with f_col3:
            map_size_choice = st.selectbox("Kaartgrootte:", ["Normaal (580px)", "Groot (780px)", "Extra Groot (980px)"], index=1)
            map_height = 580 if "Normaal" in map_size_choice else (780 if "Groot (780" in map_size_choice else 980)

        if df_comp_view.empty:
            st.warning("Geen concurrerende vluchten gevonden voor deze route-selectie.")
        else:
            ck1, ck2, ck3 = st.columns(3)
            tot_c_freq = pd.to_numeric(df_comp_view['Frequency per Week'], errors='coerce').sum() if 'Frequency per Week' in df_comp_view.columns else 0
            tot_c_pax = pd.to_numeric(df_comp_view['PAX from catchment'], errors='coerce').sum() if 'PAX from catchment' in df_comp_view.columns else 0
            n_comp_airports = df_comp_view['Catchment'].nunique() if 'Catchment' in df_comp_view.columns else len(df_comp_view)
            ck1.metric("Concurrerende Luchthavens", n_comp_airports)
            ck2.metric("Totale Concurrentie Freq/wk", f"{int(tot_c_freq)} vl/wk")
            ck3.metric("Weglekkende PAX uit Catchment", f"{int(tot_c_pax):,}".replace(",", "."))

            def parse_comp_pair(row_obj, fallback_dest_str):
                routing_s = str(row_obj.get('Routing', '')).strip()
                catch_s = str(row_obj.get('Catchment', '')).strip()
                dest_s = str(row_obj.get('Destination', '')).strip()

                origin_c = None
                dest_c = None

                parts = re.split(r'\s*[-–>/]\s*', routing_s)
                if len(parts) >= 2:
                    origin_c = resolve_coords(parts[0])
                    dest_c = resolve_coords(parts[-1])

                if not origin_c and catch_s:
                    c_try = resolve_coords(catch_s)
                    if c_try and c_try[2] != AIRPORT_COORDS["GRQ"][2]:
                        origin_c = c_try

                if not dest_c:
                    if dest_s:
                        dest_c = resolve_coords(dest_s)
                    if not dest_c and fallback_dest_str != "Alle routes uit Tabblad 1":
                        dest_c = resolve_coords(fallback_dest_str)
                    if not dest_c and routing_s:
                        dest_c = resolve_coords(routing_s)

                return origin_c, dest_c

            grq_lat, grq_lon, grq_name = AIRPORT_COORDS["GRQ"]
            comp_origins = {}
            target_dests = {}
            route_lines = []

            for _, row in df_comp_view.iterrows():
                pax_val = float(pd.to_numeric(row.get('PAX from catchment', 0), errors='coerce') or 0)
                freq_val = int(pd.to_numeric(row.get('Frequency per Week', 0), errors='coerce') or 0)
                routing_str = str(row.get('Routing', ''))
                catch_str = str(row.get('Catchment', ''))

                orig_c, dest_c = parse_comp_pair(row, sel_comp_route)
                info_line = f"{routing_str} ({catch_str}) | {freq_val} vl/wk | {int(pax_val):,} PAX".replace(",", ".")

                if orig_c:
                    o_lat, o_lon, o_name = orig_c
                    if o_name not in comp_origins:
                        comp_origins[o_name] = {"Naam": o_name, "lat": o_lat, "lon": o_lon, "PAX": 0.0, "Freq": 0, "Infos": []}
                    comp_origins[o_name]["PAX"] += max(pax_val, 500.0)
                    comp_origins[o_name]["Freq"] += freq_val
                    if info_line not in comp_origins[o_name]["Infos"]:
                        comp_origins[o_name]["Infos"].append(info_line)

                if dest_c:
                    d_lat, d_lon, d_name = dest_c
                    if d_name not in target_dests:
                        target_dests[d_name] = {"Naam": d_name, "lat": d_lat, "lon": d_lon, "PAX": 0.0, "Infos": []}
                    target_dests[d_name]["PAX"] += max(pax_val, 500.0)
                    if info_line not in target_dests[d_name]["Infos"]:
                        target_dests[d_name]["Infos"].append(info_line)

                # Lijn van Concurrerende Luchthaven -> Mogelijke Bestemming
                if orig_c and dest_c and (orig_c[2] != dest_c[2]):
                    route_lines.append({
                        "o_lat": orig_c[0], "o_lon": orig_c[1],
                        "d_lat": dest_c[0], "d_lon": dest_c[1],
                        "label": info_line
                    })

            if sel_comp_route != "Alle routes uit Tabblad 1" and not target_dests:
                sel_c = resolve_coords(sel_comp_route)
                if sel_c:
                    target_dests[sel_c[2]] = {"Naam": sel_c[2], "lat": sel_c[0], "lon": sel_c[1], "PAX": tot_c_pax, "Infos": [f"Voorgestelde route: {sel_comp_route}"]}

            fig_map = go.Figure()

            # 1. Lijnen van Concurrentie -> Mogelijke Route
            for rl in route_lines:
                fig_map.add_trace(go.Scattergeo(
                    lon=[rl["o_lon"], rl["d_lon"]],
                    lat=[rl["o_lat"], rl["d_lat"]],
                    mode="lines",
                    line=dict(width=2.0, color="rgba(13, 148, 136, 0.70)"),
                    hoverinfo="text",
                    text=rl["label"],
                    showlegend=False
                ))

            # 2. Voorgestelde route-lijn vanaf GRQ -> Mogelijke Route (oranje stippellijn)
            for d_info in target_dests.values():
                fig_map.add_trace(go.Scattergeo(
                    lon=[grq_lon, d_info["lon"]],
                    lat=[grq_lat, d_info["lat"]],
                    mode="lines",
                    line=dict(width=2.2, color="rgba(243, 112, 33, 0.85)", dash="dash"),
                    hoverinfo="text",
                    text=f"Potentiële route: GRQ → {d_info['Naam']}",
                    showlegend=False
                ))

            # 3. Punt: Eigen Luchthaven GRQ
            fig_map.add_trace(go.Scattergeo(
                lon=[grq_lon],
                lat=[grq_lat],
                text=[grq_name],
                hovertemplate="<b>%{text}</b><br>Startpunt routevoorstel<extra></extra>",
                mode="markers+text",
                textposition="top center",
                name="Groningen Airport Eelde (GRQ)",
                marker=dict(size=18, color=GRQ_ORANGE, symbol="star", line=dict(width=1.5, color="#FFFFFF"))
            ))

            # 4. Punten: Concurrerende Luchthavens
            if comp_origins:
                df_o = pd.DataFrame(list(comp_origins.values()))
                max_o_pax = df_o["PAX"].max() or 1
                o_sizes = [max(13, min(36, (v / max_o_pax) * 36)) for v in df_o["PAX"]]
                o_hover = ["<br>".join(i) for i in df_o["Infos"]]
                fig_map.add_trace(go.Scattergeo(
                    lon=df_o["lon"],
                    lat=df_o["lat"],
                    text=df_o["Naam"],
                    customdata=o_hover,
                    hovertemplate="<b>Concurrent: %{text}</b><br>%{customdata}<extra></extra>",
                    mode="markers+text",
                    textposition="bottom center",
                    name="Concurrerende Luchthaven",
                    marker=dict(size=o_sizes, color=GRQ_TEAL, symbol="circle", line=dict(width=1.5, color="#FFFFFF"))
                ))

            # 5. Punten: Mogelijke Bestemming(en)
            if target_dests:
                df_d = pd.DataFrame(list(target_dests.values()))
                d_hover = ["<br>".join(i) for i in df_d["Infos"]]
                fig_map.add_trace(go.Scattergeo(
                    lon=df_d["lon"],
                    lat=df_d["lat"],
                    text=df_d["Naam"],
                    customdata=d_hover,
                    hovertemplate="<b>Bestemming: %{text}</b><br>%{customdata}<extra></extra>",
                    mode="markers+text",
                    textposition="top center",
                    name="Mogelijke Bestemming",
                    marker=dict(size=16, color="#F59E0B", symbol="diamond", line=dict(width=1.5, color="#FFFFFF"))
                ))

            all_lats = [grq_lat] + [v["lat"] for v in comp_origins.values()] + [v["lat"] for v in target_dests.values()]
            all_lons = [grq_lon] + [v["lon"] for v in comp_origins.values()] + [v["lon"] for v in target_dests.values()]
            center_lat = (min(all_lats) + max(all_lats)) / 2
            center_lon = (min(all_lons) + max(all_lons)) / 2
            span = max(max(all_lats) - min(all_lats), max(all_lons) - min(all_lons), 4.0)
            auto_zoom = max(2.2, min(5.5, 22.0 / span))

            fig_map.update_geos(
                scope="europe",
                resolution=50,
                showcountries=True,
                countrycolor="rgba(128,128,128,0.45)",
                showcoastlines=True,
                coastlinecolor="rgba(128,128,128,0.45)",
                showland=True,
                landcolor="rgba(128,128,128,0.12)",
                showocean=True,
                oceancolor="rgba(0,0,0,0)",
                center=dict(lat=center_lat, lon=center_lon),
                projection_scale=auto_zoom
            )
            fig_map.update_layout(
                title=f"Concurrentienetwerk naar Bestemming: {sel_comp_route}",
                paper_bgcolor="rgba(0,0,0,0)",
                geo_bgcolor="rgba(0,0,0,0)",
                height=map_height,
                autosize=True,
                dragmode="pan",
                margin=dict(t=45, b=10, l=0, r=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1)
            )
            st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True, "displayModeBar": True})

            c1, c2 = st.columns(2)
            with c1:
                if {'Routing', 'Frequency per Week', 'Catchment'}.issubset(df_comp_view.columns):
                    fig_freq = px.bar(
                        df_comp_view, x='Routing', y='Frequency per Week', color='Catchment',
                        color_discrete_sequence=GRQ_PALETTE, title="Wekelijkse Frequentie per Concurrent"
                    )
                    st.plotly_chart(style_fig(fig_freq), use_container_width=True)
            with c2:
                if {'Routing', 'PAX from catchment', 'Catchment'}.issubset(df_comp_view.columns):
                    fig_pax = px.bar(
                        df_comp_view, x='Routing', y='PAX from catchment', color='Catchment',
                        color_discrete_sequence=GRQ_PALETTE, title="PAX uit GRQ Catchment per Routing"
                    )
                    st.plotly_chart(style_fig(fig_pax), use_container_width=True)

            st.dataframe(df_comp_view, use_container_width=True, hide_index=True)

# ==========================================
# TAB 5: SURFACE LEAKAGE
# ==========================================
with tab4:
    st.subheader("💧 Surface Leakage Analyse")
    if not df_leak.empty:
        if 'Region' in df_leak.columns:
            regions = sorted(df_leak['Region'].dropna().unique().tolist())
            sel_reg = st.multiselect("Filter op Regio:", regions, default=regions)
            df_leak_view = df_leak[df_leak['Region'].isin(sel_reg)]
        else:
            df_leak_view = df_leak

        if {'Destination', 'Pax leakage', 'Region'}.issubset(df_leak_view.columns):
            fig_leak = px.bar(
                df_leak_view.sort_values(by='Pax leakage', ascending=False).head(20),
                x='Destination', y='Pax leakage', color='Region', text_auto=True,
                color_discrete_sequence=GRQ_PALETTE, title="Top Bestemmingen op Passagierslekkage"
            )
            st.plotly_chart(style_fig(fig_leak), use_container_width=True)
        st.dataframe(df_leak_view, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar voor deze filterselectie.")

# ==========================================
# TAB 6: WEIGHTED CONNECTIVITY & SCHEDULES
# ==========================================
with tab5:
    st.subheader("📅 Netwerk Connectivity, Dagen & Vloot")
    if not df_conn.empty:
        if 'Airline' in df_conn.columns:
            airlines = sorted(df_conn['Airline'].dropna().unique().tolist())
            sel_air = st.multiselect("Filter op Luchtvaartmaatschappij / Alliantie:", airlines, default=airlines)
            df_conn_view = df_conn[df_conn['Airline'].isin(sel_air)]
        else:
            df_conn_view = df_conn

        col1, col2 = st.columns(2)
        with col1:
            if {'Day outbound', 'Transfer Potential', 'Airline'}.issubset(df_conn_view.columns):
                fig_trans = px.line(
                    df_conn_view[df_conn_view['Day outbound'] != 'AverageDay'],
                    x='Day outbound', y='Transfer Potential', color='Airline', markers=True,
                    color_discrete_sequence=GRQ_PALETTE, title="Transfer Potentieel % per Weekdag"
                )
                st.plotly_chart(style_fig(fig_trans), use_container_width=True)
        with col2:
            fleet_col = find_col(df_conn_view, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col:
                fleet_counts = df_conn_view[fleet_col].value_counts().reset_index()
                fleet_counts.columns = ['Fleet', 'Aantal']
                fig_fleet = px.pie(
                    fleet_counts, names='Fleet', values='Aantal', hole=0.45,
                    color_discrete_sequence=GRQ_PALETTE, title="Vlootverdeling"
                )
                st.plotly_chart(style_fig(fig_fleet), use_container_width=True)
        st.dataframe(df_conn_view, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar voor deze filterselectie.")

# ==========================================
# BRAND FOOTER
# ==========================================
st.markdown(
    '<div class="brand-footer">'
    '<span><strong>Groningen Airport Eelde (GRQ)</strong> — Route Development & Network Analytics</span>'
    '<span>Powered by <strong>JR Aviation Solutions</strong></span>'
    '</div>',
    unsafe_allow_html=True
)
