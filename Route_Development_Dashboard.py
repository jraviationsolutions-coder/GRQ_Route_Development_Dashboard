import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

st.set_page_config(
    page_title="Groningen Airport Eelde (GRQ) | Route Development Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Corporate Color Palette (Light & Dark Mode Adaptive)
GRQ_ORANGE = "#F37021"
GRQ_ORANGE_LIGHT = "#FF9E5E"
GRQ_CHARCOAL = "#3A3F42"
GRQ_SLATE = "#64748B"
GRQ_TEAL = "#0D9488"
GRQ_PALETTE = [GRQ_ORANGE, "#334155", GRQ_TEAL, GRQ_ORANGE_LIGHT, "#94A3B8", "#D95D13"]

# Airport & European Destination Coordinates Database
AIRPORT_COORDS = {
    # Catchment / Competing Airports
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
    "CGN": (50.8659, 7.1427, "Cologne Bonn Airport (CGN)"),
    "DTM": (51.5183, 7.6122, "Dortmund Airport (DTM)"),
    "NRN": (51.6024, 6.1422, "Weeze Airport (NRN)"),
    "HAM": (53.6304, 9.9882, "Hamburg Airport (HAM)"),
    "HAJ": (52.4611, 9.6850, "Hannover Airport (HAJ)"),
    "BRU": (50.9010, 4.4856, "Brussels Airport (BRU)"),
    "CRL": (50.4592, 4.4538, "Brussels South Charleroi (CRL)"),
    # European Destinations
    "STN": (51.8860, 0.2389, "London Stansted (STN)"),
    "SEN": (51.5714, 0.6956, "London Southend (SEN)"),
    "LHR": (51.4700, -0.4543, "London Heathrow (LHR)"),
    "LGW": (51.1537, -0.1821, "London Gatwick (LGW)"),
    "LCY": (51.5048, 0.0495, "London City (LCY)"),
    "LONDON": (51.8860, 0.2389, "London (STN/LCY)"),
    "LONDEN": (51.8860, 0.2389, "London (STN/LCY)"),
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
    "LIS": (38.7756, -9.1354, "Lisbon (LIS)"),
    "CPH": (55.6180, 12.6508, "Copenhagen (CPH)"),
    "COPENHAGEN": (55.6180, 12.6508, "Copenhagen (CPH)"),
    "KOPENHAGEN": (55.6180, 12.6508, "Copenhagen (CPH)"),
    "AAL": (57.0928, 9.8492, "Aalborg (AAL)"),
    "OSL": (60.1976, 11.1004, "Oslo (OSL)"),
    "BGO": (60.2934, 5.2181, "Bergen (BGO)"),
    "ARN": (59.6498, 17.9238, "Stockholm (ARN)"),
    "MUC": (48.3537, 11.7750, "Munich (MUC)"),
    "MUNICH": (48.3537, 11.7750, "Munich (MUC)"),
    "FRA": (50.0379, 8.5622, "Frankfurt (FRA)"),
    "BER": (52.3667, 13.5033, "Berlin (BER)"),
    "INN": (47.2602, 11.3440, "Innsbruck (INN)"),
    "INNSBRUCK": (47.2602, 11.3440, "Innsbruck (INN)"),
    "SZG": (47.7933, 13.0043, "Salzburg (SZG)"),
    "VIE": (48.1103, 16.5697, "Vienna (VIE)"),
    "ZRH": (47.4582, 8.5555, "Zurich (ZRH)"),
    "GVA": (46.2370, 6.1092, "Geneva (GVA)"),
    "GDN": (54.3776, 18.4662, "Gdańsk (GDN)"),
    "GDANSK": (54.3776, 18.4662, "Gdańsk (GDN)"),
    "WAW": (52.1672, 20.9679, "Warsaw (WAW)"),
    "KRK": (50.0777, 19.7848, "Kraków (KRK)"),
    "SPU": (43.5389, 16.2980, "Split (SPU)"),
    "SPLIT": (43.5389, 16.2980, "Split (SPU)"),
    "ZAD": (44.1083, 15.3467, "Zadar (ZAD)"),
    "ZAG": (45.7429, 16.0688, "Zagreb (ZAG)"),
    "DBV": (42.5614, 18.2682, "Dubrovnik (DBV)"),
    "FCO": (41.8003, 12.2389, "Rome (FCO)"),
    "MXP": (45.6301, 8.7255, "Milan (MXP)"),
    "CDG": (49.0097, 2.5479, "Paris (CDG)"),
    "BOD": (44.8283, -0.7156, "Bordeaux (BOD)"),
    "DUB": (53.4264, -6.2499, "Dublin (DUB)"),
    "EDI": (55.9508, -3.3615, "Edinburgh (EDI)"),
    "MAN": (53.3588, -2.2727, "Manchester (MAN)"),
    "BRS": (51.3827, -2.7191, "Bristol (BRS)"),
    "ABZ": (57.2019, -2.1978, "Aberdeen (ABZ)"),
    "ACE": (28.9455, -13.6052, "Lanzarote (ACE)"),
    "FUE": (28.4527, -13.8638, "Fuerteventura (FUE)"),
    "TFS": (28.0445, -16.5725, "Tenerife (TFS)"),
    "LPA": (27.9319, -15.3866, "Gran Canaria (LPA)"),
    "HER": (35.3397, 25.1803, "Heraklion (HER)"),
    "AYT": (36.8987, 30.8005, "Antalya (AYT)")
}

# Executive Enterprise CSS (Light & Dark Mode Adaptive)
st.markdown(f"""<style>
.main {{ padding: 1.25rem 2.2rem; }}
h1, h2, h3 {{ letter-spacing: 0.015em; font-weight: 600; }}

.brand-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-left: 5px solid {GRQ_ORANGE};
    border-radius: 8px;
    padding: 18px 26px;
    margin-bottom: 22px;
}}
.brand-left {{ display: flex; align-items: center; gap: 20px; }}
.brand-title {{
    color: var(--text-color);
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    margin: 0;
    line-height: 1.2;
}}
.brand-subtitle {{
    color: var(--text-color);
    opacity: 0.72;
    font-size: 0.86rem;
    letter-spacing: 0.02em;
    margin: 4px 0 0 0;
}}
.brand-badge-group {{ display: flex; align-items: center; gap: 10px; }}
.brand-badge {{
    background-color: rgba(243, 112, 33, 0.10);
    color: {GRQ_ORANGE};
    border: 1px solid {GRQ_ORANGE};
    padding: 5px 14px;
    border-radius: 4px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    white-space: nowrap;
}}
.brand-badge-neutral {{
    background-color: rgba(128, 128, 128, 0.10);
    color: var(--text-color);
    border: 1px solid rgba(128, 128, 128, 0.30);
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    white-space: nowrap;
}}

[data-testid="stMetric"] {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.20);
    border-top: 3px solid {GRQ_ORANGE};
    padding: 15px 18px;
    border-radius: 6px;
}}

.signal-card {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.20);
    border-left: 3px solid {GRQ_ORANGE};
    padding: 13px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
}}
.signal-label {{
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.68;
    font-weight: 600;
}}
.signal-value {{
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--text-color);
    margin-top: 3px;
}}

.methodology-box {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-left: 4px solid {GRQ_TEAL};
    border-radius: 6px;
    padding: 12px 16px;
    margin: 10px 0 14px 0;
    font-size: 0.88rem;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 6px;
    border-bottom: 1px solid rgba(128, 128, 128, 0.25);
}}
.stTabs [data-baseweb="tab"] {{
    background-color: var(--secondary-background-color);
    border-radius: 5px 5px 0 0;
    padding: 9px 16px;
    color: var(--text-color);
    opacity: 0.8;
    font-size: 0.86rem;
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
    margin-top: 44px;
    padding-top: 14px;
    border-top: 1px solid rgba(128, 128, 128, 0.25);
    display: flex;
    justify-content: space-between;
    color: var(--text-color);
    opacity: 0.65;
    font-size: 0.78rem;
    letter-spacing: 0.02em;
}}
</style>""", unsafe_allow_html=True)

GRQ_ICON_SVG = '<svg width="42" height="52" viewBox="0 0 80 100" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="14" cy="60" rx="7" ry="15" transform="rotate(24 14 60)" fill="#F37021"/><ellipse cx="32" cy="33" rx="5.5" ry="11.5" transform="rotate(38 32 33)" fill="#F37021"/><ellipse cx="52" cy="15" rx="3.8" ry="8.5" transform="rotate(50 52 15)" fill="#F37021"/><ellipse cx="26" cy="80" rx="10.5" ry="19" transform="rotate(22 26 80)" fill="#F37021"/><ellipse cx="48" cy="40" rx="8.5" ry="16.5" transform="rotate(36 48 40)" fill="#F37021"/><ellipse cx="68" cy="11" rx="6" ry="13.5" transform="rotate(48 68 11)" fill="#F37021"/></svg>'

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12),
        xaxis=dict(gridcolor="rgba(128,128,128,0.16)", zerolinecolor="rgba(128,128,128,0.28)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.16)", zerolinecolor="rgba(128,128,128,0.28)"),
        margin=dict(t=46, b=28, l=16, r=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# Sidebar Corporate Branding
with st.sidebar:
    st.markdown(
        f'<div style="display:flex; align-items:center; gap:12px; padding-bottom:14px; border-bottom:1px solid rgba(128,128,128,0.25); margin-bottom:16px;">'
        f'{GRQ_ICON_SVG}'
        f'<div style="line-height:1.25;">'
        f'<div style="font-weight:700; font-size:0.92rem; letter-spacing:0.08em;">GRONINGEN</div>'
        f'<div style="font-weight:700; font-size:0.92rem; letter-spacing:0.08em;">AIRPORT EELDE</div>'
        f'<div style="font-size:0.74rem; color:{GRQ_ORANGE}; margin-top:2px; font-weight:600;">Route Development Suite</div>'
        f'</div></div>',
        unsafe_allow_html=True
    )

# Executive Header Banner
st.markdown(
    f'<div class="brand-header">'
    f'<div class="brand-left">{GRQ_ICON_SVG}'
    f'<div>'
    f'<div class="brand-title">GRONINGEN AIRPORT EELDE</div>'
    f'<div class="brand-subtitle">Route Development &amp; Market Intelligence Platform</div>'
    f'</div></div>'
    f'<div class="brand-badge-group">'
    f'<div class="brand-badge-neutral">MK-METRIC O&amp;D ENGINE</div>'
    f'<div class="brand-badge">GRQ / EHGG</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ==========================================
# DATA NORMALIZATION & HELPER FUNCTIONS
# ==========================================
def fix_eu_int(val):
    """Normalizes European thousand separators parsed as floats (e.g., 7.624 -> 7624, while 345.000 -> 345)."""
    if pd.isna(val):
        return 0
    try:
        v = float(val)
        if 0 < v < 1000 and round(v, 3) != int(v):
            return int(round(v * 1000))
        return int(round(v))
    except Exception:
        return 0

def fix_eu_prob(val):
    """Normalizes Airport Choice probability percentages (e.g., 87633.000 -> 87.633%, 0.552 -> 0.552%)."""
    if pd.isna(val):
        return 0.0
    try:
        v = float(val)
        if v > 100:
            return v / 1000.0
        return v
    except Exception:
        return 0.0

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
        st.error(f"Error loading workbook: {e}")
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

def filter_by_iata(df, iata_list, col_candidates):
    """Filters a DataFrame against a list of IATA destination codes."""
    if df.empty or not iata_list:
        return df
    col = find_col(df, col_candidates)
    if not col:
        return df
    codes = [c.upper().strip() for c in iata_list if c]
    mask = df[col].astype(str).str.upper().apply(
        lambda txt: any(re.search(rf'{re.escape(code)}', txt) or code in txt for code in codes)
    )
    return df[mask]

def resolve_coords(text):
    """Resolves airport IATA/ICAO codes or city names to (lat, lon, display_label)."""
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

uploaded_file = st.sidebar.file_uploader("Upload Market Dataset (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("Upload an MK-Metric / Route Development workbook (`.xlsx`) in the left sidebar to initialize the analytical dashboard.")
    st.stop()

all_data = load_all_sheets(uploaded_file)
if not all_data:
    st.stop()

first_sheet_name = 'Proposal Investigation' if 'Proposal Investigation' in all_data else list(all_data.keys())[0]
df_prop_raw = all_data.get(first_sheet_name, pd.DataFrame()).copy()
df_choice_raw = all_data.get('Airport Choice', pd.DataFrame()).copy()
df_comp_raw = all_data.get('Route Competitors', pd.DataFrame()).copy()
df_leak_raw = all_data.get('Surface Leakage', pd.DataFrame()).copy()
df_conn_raw = all_data.get('Weighted Connectivity', pd.DataFrame()).copy()

# Normalize numerical fields from MK-Metric export
if not df_comp_raw.empty and 'PAX from catchment' in df_comp_raw.columns:
    df_comp_raw['PAX_clean'] = df_comp_raw['PAX from catchment'].apply(fix_eu_int)
    if 'Routing' in df_comp_raw.columns:
        df_comp_raw['Origin_Airport'] = df_comp_raw['Routing'].astype(str).apply(
            lambda x: re.split(r'[-–>/]', x.strip())[0].strip().upper()
        )
        df_comp_raw['Dest_Airport'] = df_comp_raw['Routing'].astype(str).apply(
            lambda x: re.split(r'[-–>/]', x.strip())[-1].strip().upper()
        )

if not df_leak_raw.empty and 'Pax leakage' in df_leak_raw.columns:
    df_leak_raw['Leakage_clean'] = df_leak_raw['Pax leakage'].apply(fix_eu_int)

if not df_choice_raw.empty:
    if 'Probability% Business' in df_choice_raw.columns:
        df_choice_raw['Prob_Bus_clean'] = df_choice_raw['Probability% Business'].apply(fix_eu_prob)
    if 'Probability% Non-Business' in df_choice_raw.columns:
        df_choice_raw['Prob_NonBus_clean'] = df_choice_raw['Probability% Non-Business'].apply(fix_eu_prob)

# ==========================================
# EXTRACT PROPOSED ROUTES FROM SHEET 1
# ==========================================
proposals = []
arr_col = find_col(df_prop_raw, ['Arrival', 'Destination', 'Route', 'Routing'])
city_col = find_col(df_prop_raw, ['City', 'Name', 'Destination Name'])
acft_col = find_col(df_prop_raw, ['ACFT Propsal', 'ACFT Proposal', 'Aircraft', 'Fleet'])
air_col = find_col(df_prop_raw, ['Airline ICAO Propsal', 'Airline ICAO Proposal', 'Airline'])

if not df_prop_raw.empty and arr_col:
    for _, r in df_prop_raw.iterrows():
        iata = str(r[arr_col]).strip().upper()
        if not iata or iata == 'NAN':
            continue
        city = str(r[city_col]).strip() if (city_col and pd.notna(r[city_col])) else ""
        label = f"{iata} — {city}" if city else iata
        pax_t = str(r['PAX Type']).strip() if ('PAX Type' in df_prop_raw.columns and pd.notna(r['PAX Type'])) else "Unclassified"
        acft_s = str(r[acft_col]).strip() if (acft_col and pd.notna(r[acft_col])) else "E190 / B738"
        air_s = str(r[air_col]).strip() if (air_col and pd.notna(r[air_col])) else ""
        proposals.append({
            "iata": iata,
            "city": city,
            "label": label,
            "pax_type": pax_t,
            "acft": acft_s,
            "airlines": [a.strip().upper() for a in air_s.split(",") if a.strip()]
        })

# ==========================================
# GLOBAL SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("### Global Parameters")

all_labels = [p["label"] for p in proposals]
selected_labels = st.sidebar.multiselect(
    "Proposed Routes (Sheet 1)",
    options=all_labels,
    default=[],
    placeholder="All proposed routes..."
)

pax_types = sorted(list({p["pax_type"] for p in proposals})) if proposals else []
selected_pax = st.sidebar.multiselect(
    "Passenger Segment (PAX Type)",
    options=pax_types,
    default=pax_types
) if pax_types else []

min_leakage = 0
if not df_leak_raw.empty and 'Leakage_clean' in df_leak_raw.columns:
    max_l = int(df_leak_raw['Leakage_clean'].max() or 0)
    if max_l > 0:
        min_leakage = st.sidebar.slider("Min. Surface Leakage (PAX)", 0, max_l, 0, step=max(1, max_l // 20))

active_proposals = [
    p for p in proposals
    if (not selected_labels or p["label"] in selected_labels)
    and (not selected_pax or p["pax_type"] in selected_pax)
]
active_iatas = [p["iata"] for p in active_proposals]

df_prop = df_prop_raw[df_prop_raw[arr_col].astype(str).str.upper().isin(active_iatas)] if (not df_prop_raw.empty and arr_col and active_iatas) else df_prop_raw.iloc[0:0]
filter_iatas = active_iatas if selected_labels or (len(selected_pax) < len(pax_types)) else []

df_choice = filter_by_iata(df_choice_raw, filter_iatas, ['Route', 'Destination'])
df_comp = filter_by_iata(df_comp_raw, filter_iatas, ['Routing', 'Route', 'Destination'])
df_leak = filter_by_iata(df_leak_raw, filter_iatas, ['Destination', 'Route'])
if min_leakage > 0 and not df_leak.empty and 'Leakage_clean' in df_leak.columns:
    df_leak = df_leak[df_leak['Leakage_clean'] >= min_leakage]

# ==========================================
# EXECUTIVE DECISION MATRIX ENGINE (SHEET 1)
# ==========================================
def build_route_summary(prop_list):
    if not prop_list:
        return pd.DataFrame()

    all_cat_pax = []
    for p in proposals:
        sc = filter_by_iata(df_comp_raw, [p["iata"]], ['Routing', 'Route', 'Destination'])
        all_cat_pax.append(sc['PAX_clean'].sum() if ('PAX_clean' in sc.columns and not sc.empty) else 0)
    max_demand_ref = max(all_cat_pax + [1])

    rows = []
    for p in prop_list:
        iata = p["iata"]
        s_choice = filter_by_iata(df_choice_raw, [iata], ['Route', 'Destination'])
        s_comp = filter_by_iata(df_comp_raw, [iata], ['Routing', 'Route', 'Destination'])
        s_leak = filter_by_iata(df_leak_raw, [iata], ['Destination', 'Route'])

        if not df_conn_raw.empty and 'Airline' in df_conn_raw.columns and p["airlines"]:
            s_conn = df_conn_raw[df_conn_raw['Airline'].astype(str).str.upper().isin(p["airlines"])]
            if s_conn.empty:
                s_conn = df_conn_raw
        else:
            s_conn = df_conn_raw

        leak_v = int(s_leak['Leakage_clean'].sum()) if ('Leakage_clean' in s_leak.columns and not s_leak.empty) else 0
        catch_pax_v = int(s_comp['PAX_clean'].sum()) if ('PAX_clean' in s_comp.columns and not s_comp.empty) else 0
        demand_v = leak_v if leak_v > 0 else catch_pax_v
        demand_sc = min((demand_v / max_demand_ref) * 100, 100) if max_demand_ref > 0 else 0

        p_bus = float(s_choice['Prob_Bus_clean'].max()) if ('Prob_Bus_clean' in s_choice.columns and not s_choice.empty) else 0.0
        p_non = float(s_choice['Prob_NonBus_clean'].max()) if ('Prob_NonBus_clean' in s_choice.columns and not s_choice.empty) else 0.0
        max_prob = p_bus if p["pax_type"] == "Business" else p_non
        alt_capture_sc = max(0.0, 100.0 - max_prob)

        c_days = s_conn[s_conn['Day outbound'] != 'AverageDay'] if ('Day outbound' in s_conn.columns and not s_conn.empty) else s_conn
        avg_tr = float(pd.to_numeric(c_days['Transfer Potential'], errors='coerce').mean()) if ('Transfer Potential' in c_days.columns and not c_days.empty) else 0.0

        best_day = "-"
        if not c_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(c_days.columns):
            d_grp = c_days.groupby('Day outbound', as_index=False)['Transfer Potential'].mean().sort_values(by='Transfer Potential', ascending=False)
            if not d_grp.empty:
                best_day = str(d_grp.iloc[0]['Day outbound'])

        c_freq = int(pd.to_numeric(s_comp['Frequency per Week'], errors='coerce').sum()) if ('Frequency per Week' in s_comp.columns and not s_comp.empty) else 0

        # Composite Route Potential Score: 45% Catchment Demand, 35% Transfer Connectivity, 20% Market Headroom
        v_weighted = 0.45 * demand_sc
        t_weighted = 0.35 * min(avg_tr, 100)
        m_sc = min(alt_capture_sc * 2.5, 100)
        m_weighted = 0.20 * m_sc
        score = round(v_weighted + t_weighted + m_weighted, 1)

        rows.append({
            "Proposed Route": p["label"],
            "IATA": iata,
            "Potential Score": score,
            "Segment": p["pax_type"],
            "Catchment / Leakage PAX": demand_v,
            "Transfer Potential %": round(avg_tr, 1),
            "Competitor Freq (flt/wk)": c_freq,
            "Peak Day": best_day,
            "Proposed Fleet": p["acft"],
            "Proposed Carrier": ", ".join(p["airlines"]) if p["airlines"] else "-",
            "_demand_sc": round(demand_sc, 1),
            "_transfer_sc": round(min(avg_tr, 100), 1),
            "_headroom_sc": round(m_sc, 1),
            "_max_prob": round(max_prob, 2)
        })
    return pd.DataFrame(rows).sort_values(by="Potential Score", ascending=False)

df_matrix = build_route_summary(active_proposals)

# ==========================================
# NAVIGATION TABS
# ==========================================
tab_overview, tab_single, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive Decision Matrix",
    "Route Deep-Dive",
    "Route Proposals (Sheet 1)",
    "Airport Choice Model",
    "Competitor Network Map",
    "Surface Leakage",
    "Connectivity & Fleet"
])

# ==========================================
# TAB 0: EXECUTIVE DECISION MATRIX
# ==========================================
with tab_overview:
    head_col, btn_col = st.columns([2.3, 1.0])
    with head_col:
        st.subheader("Executive Decision Matrix — Proposed Routes")
    with btn_col:
        with st.popover("Scoring Methodology & Live Breakdown", use_container_width=True):
            st.markdown("### Route Potential Score Architecture (0 – 100 pts)")
            st.latex(r"	ext{Potential Score} = (0.45 	imes 	ext{Demand}) + (0.35 	imes 	ext{Connectivity}) + (0.20 	imes 	ext{Market Headroom})")
            st.markdown("""
            1. **Catchment & Leakage Demand (45%):** Derived from `Pax leakage` (or `PAX from catchment` in *Route Competitors*), normalized against the highest-volume proposal in Sheet 1 (`0–100 pts`).
            2. **Network Transfer Connectivity (35%):** Mean `Transfer Potential %` across individual operating days (`Mo`–`Su`, excluding `AverageDay`) for the proposed carrier(s).
            3. **Competitive Market Headroom (20%):** Non-captive market share outside the dominant competing routing (typically AMS): $\min((100\% - 	ext{Max. Choice Prob.}) 	imes 2.5,\; 100)$.
            """)
            if not df_matrix.empty:
                st.markdown("#### Live Component Breakdown by Proposed Route")
                calc_df = pd.DataFrame({
                    "Proposed Route": df_matrix["Proposed Route"],
                    "1. Demand (45%)": df_matrix["_demand_sc"].apply(lambda x: f"{x:.1f} pts (×0.45 = {0.45*x:.1f})"),
                    "2. Connectivity (35%)": df_matrix["_transfer_sc"].apply(lambda x: f"{x:.1f} pts (×0.35 = {0.35*x:.1f})"),
                    "3. Headroom (20%)": df_matrix["_headroom_sc"].apply(lambda x: f"{x:.1f} pts (×0.20 = {0.20*x:.1f})"),
                    "Composite Score": df_matrix["Potential Score"].apply(lambda x: f"{x:.1f} / 100")
                })
                st.dataframe(calc_df, use_container_width=True, hide_index=True)

    if df_matrix.empty:
        st.warning("No proposed routes found in Sheet 1 matching the active filter criteria.")
    else:
        top_route = df_matrix.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Top-Ranked Proposal", top_route["Proposed Route"], f"{top_route['Potential Score']} / 100 pts")
        m2.metric("Total Catchment / Leakage PAX", f"{df_matrix['Catchment / Leakage PAX'].sum():,}")
        m3.metric("Mean Transfer Potential", f"{df_matrix['Transfer Potential %'].mean():.1f}%")
        m4.metric("Evaluated Proposals", len(df_matrix))

        g1, g2 = st.columns(2)
        with g1:
            fig_rank = px.bar(
                df_matrix,
                x="Potential Score",
                y="Proposed Route",
                orientation="h",
                color="Segment",
                text_auto=True,
                color_discrete_sequence=[GRQ_ORANGE, GRQ_TEAL, GRQ_SLATE],
                title="Route Ranking by Composite Potential Score"
            )
            fig_rank.update_layout(yaxis={'categoryorder': 'total ascending'})
            st.plotly_chart(style_fig(fig_rank), use_container_width=True)

        with g2:
            fig_bubble = px.scatter(
                df_matrix,
                x="Catchment / Leakage PAX",
                y="Transfer Potential %",
                size="Potential Score",
                color="Segment",
                text="Proposed Route",
                color_discrete_sequence=[GRQ_ORANGE, GRQ_TEAL, GRQ_SLATE],
                title="Catchment Demand vs. Transfer Connectivity (Bubble Size = Score)"
            )
            fig_bubble.update_traces(textposition='top center')
            st.plotly_chart(style_fig(fig_bubble), use_container_width=True)

        hidden_cols = ["IATA", "_demand_sc", "_transfer_sc", "_headroom_sc", "_max_prob"]
        st.dataframe(
            df_matrix.drop(columns=[c for c in hidden_cols if c in df_matrix.columns]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Potential Score": st.column_config.ProgressColumn(
                    "Potential Score", format="%.1f", min_value=0, max_value=100
                ),
                "Catchment / Leakage PAX": st.column_config.NumberColumn("Catchment / Leakage PAX", format="%d"),
                "Transfer Potential %": st.column_config.NumberColumn("Transfer Potential %", format="%.1f%%"),
            }
        )

# ==========================================
# TAB 1: ROUTE DEEP-DIVE
# ==========================================
with tab_single:
    if not active_proposals:
        st.warning("No proposed routes available in Sheet 1.")
    else:
        col_sel, col_btn_dd = st.columns([2.0, 1.0])
        with col_sel:
            chosen_label = st.selectbox("Select Proposed Route for Detailed Assessment:", [p["label"] for p in active_proposals])

        chosen_prop = next(p for p in active_proposals if p["label"] == chosen_label)
        row_dest = df_matrix[df_matrix["IATA"] == chosen_prop["iata"]].iloc[0]

        with col_btn_dd:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            with st.popover(f"Score Decomposition — {chosen_prop['iata']}", use_container_width=True):
                st.markdown(f"### Score Decomposition: {chosen_label}")
                st.latex(r"	ext{Score} = (0.45 	imes D) + (0.35 	imes C) + (0.20 	imes H)")
                st.markdown(f"""
                - **Demand Score ($D$):** `{row_dest['_demand_sc']:.1f}` pts $	imes 0.45 =$ **{0.45 * row_dest['_demand_sc']:.1f} pts** ({int(row_dest['Catchment / Leakage PAX']):,} PAX)
                - **Transfer Connectivity ($C$):** `{row_dest['_transfer_sc']:.1f}` pts $	imes 0.35 =$ **{0.35 * row_dest['_transfer_sc']:.1f} pts**
                - **Market Headroom ($H$):** `{row_dest['_headroom_sc']:.1f}` pts $	imes 0.20 =$ **{0.20 * row_dest['_headroom_sc']:.1f} pts** (Dominant competitor share: {row_dest['_max_prob']:.1f}%)
                - **Composite Potential Score:** **{row_dest['Potential Score']:.1f} / 100 pts**
                """)

        if not df_conn_raw.empty and 'Airline' in df_conn_raw.columns and chosen_prop["airlines"]:
            s_conn = df_conn_raw[df_conn_raw['Airline'].astype(str).str.upper().isin(chosen_prop["airlines"])]
            if s_conn.empty:
                s_conn = df_conn_raw
        else:
            s_conn = df_conn_raw

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Composite Potential Score", f"{row_dest['Potential Score']} / 100")
        k2.metric("Catchment / Leakage PAX", f"{row_dest['Catchment / Leakage PAX']:,}")
        k3.metric("Transfer Potential", f"{row_dest['Transfer Potential %']:.1f}%")
        k4.metric("Competitor Frequency", f"{row_dest['Competitor Freq (flt/wk)']} flt/wk")

        c_sig1, c_sig2, c_sig3, c_sig4 = st.columns(4)
        with c_sig1:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Primary Segment</div><div class="signal-value">{row_dest["Segment"]}</div></div>', unsafe_allow_html=True)
        with c_sig2:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Peak Connectivity Day</div><div class="signal-value">{row_dest["Peak Day"]}</div></div>', unsafe_allow_html=True)
        with c_sig3:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Proposed Carrier</div><div class="signal-value">{row_dest["Proposed Carrier"]}</div></div>', unsafe_allow_html=True)
        with c_sig4:
            st.markdown(f'<div class="signal-card"><div class="signal-label">Proposed Aircraft</div><div class="signal-value">{row_dest["Proposed Fleet"]}</div></div>', unsafe_allow_html=True)

        v1, v2 = st.columns(2)
        with v1:
            max_p = max(df_matrix['Catchment / Leakage PAX'].max(), 1)
            d_norm = min((row_dest['Catchment / Leakage PAX'] / max_p) * 100, 100)
            t_norm = row_dest['Transfer Potential %']
            c_space = max(15.0, min(100.0, 100.0 - (row_dest['Competitor Freq (flt/wk)'] / 6.0)))

            fig_radar = go.Figure(data=go.Scatterpolar(
                r=[d_norm, t_norm, c_space, row_dest['Potential Score'], d_norm],
                theta=['Catchment Demand', 'Transfer Connectivity', 'Market Headroom', 'Composite Score', 'Catchment Demand'],
                fill='toself',
                line_color=GRQ_ORANGE,
                fillcolor='rgba(243, 112, 33, 0.25)'
            ))
            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(128,128,128,0.25)")),
                showlegend=False,
                title=f"Multi-Dimensional Route Profile: {chosen_label}"
            )
            st.plotly_chart(style_fig(fig_radar), use_container_width=True)

        with v2:
            c_days = s_conn[s_conn['Day outbound'] != 'AverageDay'] if 'Day outbound' in s_conn.columns else s_conn
            if not c_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(c_days.columns):
                day_order = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                fig_d = px.bar(
                    c_days,
                    x='Day outbound',
                    y='Transfer Potential',
                    color='Airline' if 'Airline' in c_days.columns else None,
                    barmode='group',
                    category_orders={'Day outbound': day_order},
                    color_discrete_sequence=GRQ_PALETTE,
                    title=f"Weekly Connectivity Schedule Profile ({chosen_label})",
                    labels={'Day outbound': 'Outbound Day', 'Transfer Potential': 'Transfer Potential (%)'}
                )
                st.plotly_chart(style_fig(fig_d), use_container_width=True)
            else:
                st.info("No day-of-week connectivity records available for this selection.")

# ==========================================
# TAB 2: PROPOSAL INVESTIGATION (SHEET 1)
# ==========================================
with tab1:
    st.subheader("Route Proposals — Baseline Input (Sheet 1)")
    if not df_prop.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Proposed Routes", len(df_prop))
        if 'PAX Type' in df_prop.columns:
            c2.metric("Business-Oriented Routes", len(df_prop[df_prop['PAX Type'] == 'Business']))
            c3.metric("Leisure / Non-Business Routes", len(df_prop[df_prop['PAX Type'] == 'Non-Business']))
        st.dataframe(df_prop, use_container_width=True, hide_index=True)
    else:
        st.info("No baseline proposal records match the active filters.")

# ==========================================
# TAB 3: AIRPORT CHOICE MODEL
# ==========================================
with tab2:
    st.subheader("Airport Choice Model — Competing Routing Share")
    if not df_choice.empty:
        col_l, col_r = st.columns(2)
        with col_l:
            if {'Route', 'Prob_Bus_clean', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_bus = px.bar(
                    df_choice, x='Route', y='Prob_Bus_clean', color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE, GRQ_SLATE], title="Business Choice Probability (%)",
                    labels={'Prob_Bus_clean': 'Business Probability (%)'}
                )
                st.plotly_chart(style_fig(fig_bus), use_container_width=True)
        with col_r:
            if {'Route', 'Prob_NonBus_clean', 'Trip Purpose'}.issubset(df_choice.columns):
                fig_nonbus = px.bar(
                    df_choice, x='Route', y='Prob_NonBus_clean', color='Trip Purpose',
                    color_discrete_sequence=[GRQ_ORANGE_LIGHT, GRQ_TEAL], title="Non-Business Choice Probability (%)",
                    labels={'Prob_NonBus_clean': 'Non-Business Probability (%)'}
                )
                st.plotly_chart(style_fig(fig_nonbus), use_container_width=True)
        disp_choice = df_choice.copy()
        if 'Prob_Bus_clean' in disp_choice.columns:
            disp_choice['Probability% Business'] = disp_choice['Prob_Bus_clean'].round(2)
        if 'Prob_NonBus_clean' in disp_choice.columns:
            disp_choice['Probability% Non-Business'] = disp_choice['Prob_NonBus_clean'].round(2)
        st.dataframe(disp_choice.drop(columns=[c for c in ['Prob_Bus_clean', 'Prob_NonBus_clean'] if c in disp_choice.columns]), use_container_width=True, hide_index=True)
    else:
        st.info("No Airport Choice records match the active filters.")

# ==========================================
# TAB 4: COMPETITOR NETWORK MAP
# ==========================================
with tab3:
    st.subheader("Competitor Network Analysis — Catchment Leakage & Geospatial Routing")

    if df_comp_raw.empty:
        st.info("No records available in 'Route Competitors'.")
    else:
        f_col1, f_col2, f_col3 = st.columns([1.3, 1.5, 1.0])
        with f_col1:
            comp_route_options = ["All Proposed Routes (Sheet 1)"] + [p["label"] for p in proposals]
            sel_comp_route = st.selectbox("Target Proposed Route:", comp_route_options)

        if sel_comp_route != "All Proposed Routes (Sheet 1)":
            sel_iata = sel_comp_route.split("—")[0].strip()
            df_comp_view = filter_by_iata(df_comp_raw, [sel_iata], ['Routing', 'Route', 'Destination'])
        else:
            sel_iata = None
            df_comp_view = filter_by_iata(df_comp_raw, active_iatas, ['Routing', 'Route', 'Destination']) if active_iatas else df_comp_raw.copy()

        with f_col2:
            if 'Origin_Airport' in df_comp_view.columns and not df_comp_view.empty:
                comp_airports = sorted([a for a in df_comp_view['Origin_Airport'].dropna().unique().tolist() if a != "GRQ"])
                sel_origins = st.multiselect("Competing Departure Airports:", comp_airports, default=comp_airports)
                df_comp_view = df_comp_view[df_comp_view['Origin_Airport'].isin(sel_origins)]

        with f_col3:
            map_size_choice = st.selectbox("Map Viewport Height:", ["Standard (580px)", "Large (780px)", "Expanded (980px)"], index=1)
            map_height = 580 if "Standard" in map_size_choice else (780 if "Large" in map_size_choice else 980)

        if df_comp_view.empty:
            st.warning("No competing services identified for the selected route filter.")
        else:
            ck1, ck2, ck3 = st.columns(3)
            tot_c_freq = int(pd.to_numeric(df_comp_view['Frequency per Week'], errors='coerce').sum()) if 'Frequency per Week' in df_comp_view.columns else 0
            tot_c_pax = int(df_comp_view['PAX_clean'].sum()) if 'PAX_clean' in df_comp_view.columns else 0
            n_comp_airports = df_comp_view['Origin_Airport'].nunique() if 'Origin_Airport' in df_comp_view.columns else len(df_comp_view)
            ck1.metric("Competing Departure Airports", n_comp_airports)
            ck2.metric("Aggregate Competitor Frequency", f"{tot_c_freq} flt/wk")
            ck3.metric("Catchment PAX Leakage", f"{tot_c_pax:,}")

            grq_lat, grq_lon, grq_name = AIRPORT_COORDS["GRQ"]
            comp_origins = {}
            target_dests = {}
            route_lines = []

            for _, row in df_comp_view.iterrows():
                pax_val = float(row.get('PAX_clean', 0) or 0)
                freq_val = int(pd.to_numeric(row.get('Frequency per Week', 0), errors='coerce') or 0)
                routing_str = str(row.get('Routing', ''))
                catch_str = str(row.get('Catchment', ''))

                parts = re.split(r'\s*[-–>/]\s*', routing_str.strip())
                orig_c = resolve_coords(parts[0]) if len(parts) >= 1 else None
                dest_c = resolve_coords(parts[-1]) if len(parts) >= 2 else (resolve_coords(sel_iata) if sel_iata else None)

                info_line = f"{routing_str} ({catch_str}) | {freq_val} flt/wk | {int(pax_val):,} PAX"

                if orig_c and orig_c[2] != grq_name:
                    o_lat, o_lon, o_name = orig_c
                    if o_name not in comp_origins:
                        comp_origins[o_name] = {"Name": o_name, "lat": o_lat, "lon": o_lon, "PAX": 0.0, "Freq": 0, "Infos": []}
                    comp_origins[o_name]["PAX"] += max(pax_val, 5.0)
                    comp_origins[o_name]["Freq"] += freq_val
                    if info_line not in comp_origins[o_name]["Infos"]:
                        comp_origins[o_name]["Infos"].append(info_line)

                if dest_c:
                    d_lat, d_lon, d_name = dest_c
                    if d_name not in target_dests:
                        target_dests[d_name] = {"Name": d_name, "lat": d_lat, "lon": d_lon, "PAX": 0.0, "Infos": []}
                    target_dests[d_name]["PAX"] += max(pax_val, 5.0)
                    if info_line not in target_dests[d_name]["Infos"]:
                        target_dests[d_name]["Infos"].append(info_line)

                if orig_c and dest_c and (orig_c[2] != grq_name) and (orig_c[2] != dest_c[2]):
                    route_lines.append({
                        "o_lat": orig_c[0], "o_lon": orig_c[1],
                        "d_lat": dest_c[0], "d_lon": dest_c[1],
                        "label": info_line
                    })

            if sel_iata and not target_dests:
                sel_c = resolve_coords(sel_iata)
                if sel_c:
                    target_dests[sel_c[2]] = {"Name": sel_c[2], "lat": sel_c[0], "lon": sel_c[1], "PAX": tot_c_pax, "Infos": [f"Proposed Route: {sel_comp_route}"]}

            fig_map = go.Figure()

            # 1. Competing Airport -> Destination vectors
            for rl in route_lines:
                fig_map.add_trace(go.Scattergeo(
                    lon=[rl["o_lon"], rl["d_lon"]],
                    lat=[rl["o_lat"], rl["d_lat"]],
                    mode="lines",
                    line=dict(width=1.8, color="rgba(13, 148, 136, 0.55)"),
                    hoverinfo="text",
                    text=rl["label"],
                    showlegend=False
                ))

            # 2. Proposed GRQ -> Destination vector (dashed orange)
            for d_info in target_dests.values():
                fig_map.add_trace(go.Scattergeo(
                    lon=[grq_lon, d_info["lon"]],
                    lat=[grq_lat, d_info["lat"]],
                    mode="lines",
                    line=dict(width=2.5, color="rgba(243, 112, 33, 0.90)", dash="dash"),
                    hoverinfo="text",
                    text=f"Proposed GRQ Link: GRQ → {d_info['Name']}",
                    showlegend=False
                ))

            # 3. Origin Marker: GRQ
            fig_map.add_trace(go.Scattergeo(
                lon=[grq_lon],
                lat=[grq_lat],
                text=[grq_name],
                hovertemplate="<b>%{text}</b><br>Proposed Origin Hub<extra></extra>",
                mode="markers+text",
                textposition="top center",
                name="Groningen Airport Eelde (GRQ)",
                marker=dict(size=18, color=GRQ_ORANGE, symbol="star", line=dict(width=1.5, color="#FFFFFF"))
            ))

            # 4. Competing Departure Airports
            if comp_origins:
                df_o = pd.DataFrame(list(comp_origins.values()))
                max_o_pax = df_o["PAX"].max() or 1
                o_sizes = [max(13, min(38, (v / max_o_pax) * 38)) for v in df_o["PAX"]]
                o_hover = ["<br>".join(i) for i in df_o["Infos"]]
                fig_map.add_trace(go.Scattergeo(
                    lon=df_o["lon"],
                    lat=df_o["lat"],
                    text=df_o["Name"],
                    customdata=o_hover,
                    hovertemplate="<b>Competitor: %{text}</b><br>%{customdata}<extra></extra>",
                    mode="markers+text",
                    textposition="bottom center",
                    name="Competing Airport",
                    marker=dict(size=o_sizes, color=GRQ_TEAL, symbol="circle", line=dict(width=1.5, color="#FFFFFF"))
                ))

            # 5. Target Destination(s)
            if target_dests:
                df_d = pd.DataFrame(list(target_dests.values()))
                d_hover = ["<br>".join(i) for i in df_d["Infos"]]
                fig_map.add_trace(go.Scattergeo(
                    lon=df_d["lon"],
                    lat=df_d["lat"],
                    text=df_d["Name"],
                    customdata=d_hover,
                    hovertemplate="<b>Target Destination: %{text}</b><br>%{customdata}<extra></extra>",
                    mode="markers+text",
                    textposition="top center",
                    name="Target Destination",
                    marker=dict(size=17, color="#F59E0B", symbol="diamond", line=dict(width=1.5, color="#FFFFFF"))
                ))

            all_lats = [grq_lat] + [v["lat"] for v in comp_origins.values()] + [v["lat"] for v in target_dests.values()]
            all_lons = [grq_lon] + [v["lon"] for v in comp_origins.values()] + [v["lon"] for v in target_dests.values()]
            center_lat = (min(all_lats) + max(all_lats)) / 2
            center_lon = (min(all_lons) + max(all_lons)) / 2
            span = max(max(all_lats) - min(all_lats), max(all_lons) - min(all_lons), 4.0)
            auto_zoom = max(2.2, min(5.2, 22.0 / span))

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
                title=f"Competitive Catchment & Route Network: {sel_comp_route}",
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
                if {'Routing', 'Frequency per Week', 'Origin_Airport'}.issubset(df_comp_view.columns):
                    fig_freq = px.bar(
                        df_comp_view, x='Routing', y='Frequency per Week', color='Origin_Airport',
                        color_discrete_sequence=GRQ_PALETTE, title="Weekly Competitor Frequency by Routing",
                        labels={'Origin_Airport': 'Departure Airport'}
                    )
                    st.plotly_chart(style_fig(fig_freq), use_container_width=True)
            with c2:
                if {'Routing', 'PAX_clean', 'Origin_Airport'}.issubset(df_comp_view.columns):
                    fig_pax = px.bar(
                        df_comp_view, x='Routing', y='PAX_clean', color='Origin_Airport',
                        color_discrete_sequence=GRQ_PALETTE, title="GRQ Catchment PAX by Competing Routing",
                        labels={'PAX_clean': 'Catchment PAX', 'Origin_Airport': 'Departure Airport'}
                    )
                    st.plotly_chart(style_fig(fig_pax), use_container_width=True)

            disp_comp = df_comp_view.copy()
            if 'PAX_clean' in disp_comp.columns:
                disp_comp['PAX from catchment'] = disp_comp['PAX_clean']
            st.dataframe(disp_comp.drop(columns=[c for c in ['PAX_clean', 'Origin_Airport', 'Dest_Airport'] if c in disp_comp.columns]), use_container_width=True, hide_index=True)

# ==========================================
# TAB 5: SURFACE LEAKAGE
# ==========================================
with tab4:
    st.subheader("Surface Leakage Analysis — Unserved Catchment Demand")
    if not df_leak.empty:
        if 'Region' in df_leak.columns:
            regions = sorted(df_leak['Region'].dropna().unique().tolist())
            sel_reg = st.multiselect("Filter by Geographic Region:", regions, default=regions)
            df_leak_view = df_leak[df_leak['Region'].isin(sel_reg)]
        else:
            df_leak_view = df_leak

        if {'Destination', 'Leakage_clean', 'Region'}.issubset(df_leak_view.columns):
            fig_leak = px.bar(
                df_leak_view.sort_values(by='Leakage_clean', ascending=False).head(20),
                x='Destination', y='Leakage_clean', color='Region', text_auto=True,
                color_discrete_sequence=GRQ_PALETTE, title="Top Destinations by Passenger Leakage",
                labels={'Leakage_clean': 'Passenger Leakage (PAX)'}
            )
            st.plotly_chart(style_fig(fig_leak), use_container_width=True)
        disp_leak = df_leak_view.copy()
        if 'Leakage_clean' in disp_leak.columns:
            disp_leak['Pax leakage'] = disp_leak['Leakage_clean']
        st.dataframe(disp_leak.drop(columns=[c for c in ['Leakage_clean'] if c in disp_leak.columns]), use_container_width=True, hide_index=True)
    else:
        st.info("No Surface Leakage records match the active filters.")

# ==========================================
# TAB 6: WEIGHTED CONNECTIVITY & FLEET
# ==========================================
with tab5:
    st.subheader("Weighted Connectivity, Operating Days & Fleet Allocation")
    if not df_conn_raw.empty:
        active_airlines = [a for p in active_proposals for a in p["airlines"]]
        df_conn_base = df_conn_raw[df_conn_raw['Airline'].astype(str).str.upper().isin(active_airlines)] if (selected_labels and 'Airline' in df_conn_raw.columns and active_airlines) else df_conn_raw

        if 'Airline' in df_conn_base.columns:
            airlines = sorted(df_conn_base['Airline'].dropna().unique().tolist())
            sel_air = st.multiselect("Filter by Carrier / Alliance:", airlines, default=airlines)
            df_conn_view = df_conn_base[df_conn_base['Airline'].isin(sel_air)]
        else:
            df_conn_view = df_conn_base

        col1, col2 = st.columns(2)
        with col1:
            if {'Day outbound', 'Transfer Potential', 'Airline'}.issubset(df_conn_view.columns):
                day_order = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
                fig_trans = px.line(
                    df_conn_view[df_conn_view['Day outbound'] != 'AverageDay'],
                    x='Day outbound', y='Transfer Potential', color='Airline', markers=True,
                    category_orders={'Day outbound': day_order},
                    color_discrete_sequence=GRQ_PALETTE, title="Transfer Potential (%) by Day of Week",
                    labels={'Day outbound': 'Outbound Day', 'Transfer Potential': 'Transfer Potential (%)'}
                )
                st.plotly_chart(style_fig(fig_trans), use_container_width=True)
        with col2:
            fleet_col = find_col(df_conn_view, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col:
                fleet_counts = df_conn_view[fleet_col].value_counts().reset_index()
                fleet_counts.columns = ['Fleet', 'Count']
                fig_fleet = px.pie(
                    fleet_counts, names='Fleet', values='Count', hole=0.45,
                    color_discrete_sequence=GRQ_PALETTE, title="Fleet Allocation Mix"
                )
                st.plotly_chart(style_fig(fig_fleet), use_container_width=True)
        st.dataframe(df_conn_view, use_container_width=True, hide_index=True)
    else:
        st.info("No Weighted Connectivity records match the active filters.")

# ==========================================
# CORPORATE FOOTER
# ==========================================
st.markdown(
    '<div class="brand-footer">'
    '<span><strong>Groningen Airport Eelde (GRQ)</strong> — Route Development &amp; Network Intelligence</span>'
    '<span><strong>Alpha Phase [Version 0.8.1.9]</strong></span>'
    '<span>Powered by <strong>JR Aviation Solutions</strong></span>'
    '</div>',
    unsafe_allow_html=True
)
