import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Groningen Airport Eelde (GRQ) | Route Development",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GRQ Kleurenpalet (werkt contrastrijk in zowel Light als Dark mode)
GRQ_ORANGE = "#F37021"
GRQ_ORANGE_LIGHT = "#FF9E5E"
GRQ_CHARCOAL = "#3A3F42"
GRQ_SLATE = "#64748B"
GRQ_TEAL = "#0D9488"
GRQ_PALETTE = [GRQ_ORANGE, "#334155", GRQ_TEAL, GRQ_ORANGE_LIGHT, "#94A3B8", "#D95D13"]

# Adaptieve CSS (gebruikt Streamlit's thema-variabelen voor Light & Dark mode)
st.markdown(f"""<style>
.main {{ padding: 1.2rem 2rem; }}
h1, h2, h3 {{ letter-spacing: 0.01em; font-weight: 600; }}

/* Adaptieve GRQ Brand Header */
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

/* Adaptieve Metric Cards */
[data-testid="stMetric"] {{
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-top: 3px solid {GRQ_ORANGE};
    padding: 14px 16px;
    border-radius: 8px;
}}

/* Compacte Signaal-Chips (vervangt grote tekstvakken) */
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

/* Tabbladen styling */
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

/* Footer */
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

# Groningen Airport Eelde SVG Beeldmerk
GRQ_ICON_SVG = '<svg width="44" height="54" viewBox="0 0 80 100" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="14" cy="60" rx="7" ry="15" transform="rotate(24 14 60)" fill="#F37021"/><ellipse cx="32" cy="33" rx="5.5" ry="11.5" transform="rotate(38 32 33)" fill="#F37021"/><ellipse cx="52" cy="15" rx="3.8" ry="8.5" transform="rotate(50 52 15)" fill="#F37021"/><ellipse cx="26" cy="80" rx="10.5" ry="19" transform="rotate(22 26 80)" fill="#F37021"/><ellipse cx="48" cy="40" rx="8.5" ry="16.5" transform="rotate(36 48 40)" fill="#F37021"/><ellipse cx="68" cy="11" rx="6" ry="13.5" transform="rotate(48 68 11)" fill="#F37021"/></svg>'

def style_fig(fig):
    """Maakt Plotly-grafieken transparant zodat ze perfect werken in Light én Dark mode."""
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
# GLOBALE FILTERS IN DE ZIJBALK
# ==========================================
st.sidebar.markdown("### 🔍 Globale Filters")

# Verzamel alle unieke bestemmingen/routes uit alle tabbladen
all_destinations = set()
for df_s, cols in [
    (df_prop_raw, ['Route', 'Destination', 'Routing']),
    (df_choice_raw, ['Route', 'Destination']),
    (df_leak_raw, ['Destination', 'Route']),
    (df_comp_raw, ['Routing', 'Route', 'Destination'])
]:
    c_n = find_col(df_s, cols)
    if c_n:
        for val in df_s[c_n].dropna().unique():
            all_destinations.add(clean_route_name(val))

sorted_destinations = sorted(list(all_destinations))

selected_dests = st.sidebar.multiselect(
    "Filter op Bestemming(en) / Route(s)",
    options=sorted_destinations,
    default=[],
    placeholder="Alle bestemmingen tonen..."
)

# Segment filter (Business / Non-Business)
pax_types = []
if not df_prop_raw.empty and 'PAX Type' in df_prop_raw.columns:
    pax_types = sorted(df_prop_raw['PAX Type'].dropna().unique().tolist())
selected_pax = st.sidebar.multiselect(
    "Filter op Segment (PAX Type)",
    options=pax_types,
    default=pax_types
) if pax_types else []

# Minimale Surface Leakage slider
min_leakage = 0
if not df_leak_raw.empty and 'Pax leakage' in df_leak_raw.columns:
    max_l = int(pd.to_numeric(df_leak_raw['Pax leakage'], errors='coerce').max() or 0)
    if max_l > 0:
        min_leakage = st.sidebar.slider("Min. Surface Leakage (PAX)", 0, max_l, 0, step=max(1, max_l // 20))

# Pas globale filters toe op de dataframes
df_prop = filter_df_multi(df_prop_raw, selected_dests, ['Route', 'Destination', 'Routing'])
if selected_pax and not df_prop.empty and 'PAX Type' in df_prop.columns:
    df_prop = df_prop[df_prop['PAX Type'].isin(selected_pax)]

df_choice = filter_df_multi(df_choice_raw, selected_dests, ['Route', 'Destination'])
df_comp = filter_df_multi(df_comp_raw, selected_dests, ['Routing', 'Route', 'Destination'])
df_leak = filter_df_multi(df_leak_raw, selected_dests, ['Destination', 'Route'])
if min_leakage > 0 and not df_leak.empty and 'Pax leakage' in df_leak.columns:
    df_leak = df_leak[pd.to_numeric(df_leak['Pax leakage'], errors='coerce') >= min_leakage]

df_conn = filter_df_multi(df_conn_raw, selected_dests, ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])

# ==========================================
# HULPFUNCTIE: BEREKEN ROUTE SCORECARD
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
            "Bestemming": dest,
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

active_dest_pool = selected_dests if selected_dests else sorted_destinations
df_matrix = build_route_summary(active_dest_pool)

# ==========================================
# TABS STRUCTUUR
# ==========================================
tab_overview, tab_single, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Multi-Route Vergelijking",
    "🎯 Bestemming Deep-Dive",
    "📍 Route Voorstellen", 
    "🧭 Airport Choice", 
    "🥊 Concurrentie", 
    "💧 Surface Leakage", 
    "📅 Connectivity & Vloot"
])

# ==========================================
# TAB 0: MULTI-ROUTE VERGELIJKING (OVERZICHT)
# ==========================================
with tab_overview:
    st.subheader("📊 Integrale Route Vergelijking & Kansenmatrix")

    if df_matrix.empty:
        st.warning("Geen gekoppelde routes gevonden voor de huidige filterselectie.")
    else:
        # Bovenste KPI-rij
        top_route = df_matrix.iloc[0]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🥇 Hoogst Scorende Bestemming", top_route["Bestemming"], f"{top_route['Potentie Score']} / 100 pt")
        m2.metric("💧 Totale Surface Leakage", f"{df_matrix['Surface Leakage'].sum():,}".replace(",", "."))
        m3.metric("📈 Gem. GRQ Keuzekans", f"{df_matrix[['Business Kans %', 'Leisure Kans %']].max(axis=1).mean():.1f}%")
        m4.metric("✈️ Geselecteerde Routes", len(df_matrix))

        # Visuele grafieken naast elkaar (geen grote tekstvakken)
        g1, g2 = st.columns(2)
        with g1:
            fig_rank = px.bar(
                df_matrix.head(12),
                x="Potentie Score",
                y="Bestemming",
                orientation="h",
                color="Segment",
                text_auto=True,
                color_discrete_sequence=[GRQ_ORANGE, GRQ_SLATE, GRQ_TEAL],
                title="Top Routes op Gecombineerde GRQ Potentie Score (0-100)"
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
                text="Bestemming",
                color_discrete_sequence=[GRQ_ORANGE, GRQ_TEAL, GRQ_SLATE],
                title="Vraag (Leakage) vs. GRQ Voorkeur (Bubbel = Score)"
            )
            fig_bubble.update_traces(textposition='top center')
            st.plotly_chart(style_fig(fig_bubble), use_container_width=True)

        # Interactieve Vergelijkingstabel met visuele voortgangsbalken
        st.subheader("📋 Gecombineerde Beslismatrix (Alle Tabbladen Gekoppeld)")
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
    if not active_dest_pool:
        st.warning("Geen bestemmingen beschikbaar.")
    else:
        col_sel, col_info = st.columns([1, 2])
        with col_sel:
            chosen_dest = st.selectbox("🎯 Selecteer één specifieke bestemming:", active_dest_pool)
        
        row_dest = df_matrix[df_matrix["Bestemming"] == chosen_dest].iloc[0]
        s_conn = filter_df_multi(df_conn_raw, [chosen_dest], ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])
        if s_conn.empty:
            s_conn = df_conn_raw

        # 4 Compacte KPI's
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 Potentie Score", f"{row_dest['Potentie Score']} / 100")
        k2.metric("💧 Terugwinbare PAX", f"{row_dest['Surface Leakage']:,}".replace(",", "."))
        k3.metric("🧭 Hoogste Keuzekans", f"{max(row_dest['Business Kans %'], row_dest['Leisure Kans %']):.1f}%")
        k4.metric("🥊 Concurrentie", f"{row_dest['Concurrentie (vl/wk)']} vl/wk")

        # Compacte Signaal-Chips (vervangen grote tekstblokken)
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

        # Visuele onderbouwing: Radar/Bar + Weekdag-grafiek
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
# TAB 2: PROPOSAL INVESTIGATION
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
# TAB 4: ROUTE COMPETITORS
# ==========================================
with tab3:
    st.subheader("🥊 Concurrentie & Catchment Overlap")
    if not df_comp.empty:
        # Extra lokale filter op Catchment
        if 'Catchment' in df_comp.columns:
            catchments = sorted(df_comp['Catchment'].dropna().unique().tolist())
            sel_catch = st.multiselect("Filter op Catchment Zone:", catchments, default=catchments)
            df_comp_view = df_comp[df_comp['Catchment'].isin(sel_catch)]
        else:
            df_comp_view = df_comp

        c1, c2 = st.columns(2)
        with c1:
            if {'Routing', 'Frequency per Week', 'Catchment'}.issubset(df_comp_view.columns):
                fig_freq = px.bar(
                    df_comp_view, x='Routing', y='Frequency per Week', color='Catchment',
                    color_discrete_sequence=GRQ_PALETTE, title="Wekelijkse Frequentie Concurrenten"
                )
                st.plotly_chart(style_fig(fig_freq), use_container_width=True)
        with c2:
            if {'Routing', 'PAX from catchment'}.issubset(df_comp_view.columns):
                fig_pax = px.bar(
                    df_comp_view, x='Routing', y='PAX from catchment',
                    color_discrete_sequence=[GRQ_ORANGE], title="PAX uit GRQ Catchment"
                )
                st.plotly_chart(style_fig(fig_pax), use_container_width=True)
        st.dataframe(df_comp_view, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar voor deze filterselectie.")

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
