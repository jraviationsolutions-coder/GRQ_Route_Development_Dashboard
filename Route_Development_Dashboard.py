import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="GRQ Route Development Dashboard",
    page_icon="✈️",
    layout="wide"
)

# Custom minimalist dark-mode styling (JR Aviation Solutions palette)
st.markdown("""
    <style>
    .main { padding: 1.5rem; }
    .stMetric { background-color: #191919; border: 1px solid #333; padding: 15px; border-radius: 8px; }
    .insight-box {
        background-color: #191919;
        border-left: 4px solid #BFCCDE;
        padding: 16px 20px;
        border-radius: 6px;
        margin-bottom: 16px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("✈️ Groningen Airport Eelde (GRQ) — Route Proposal & Market Analysis")
st.caption("Interactief dashboard voor integrale route-evaluatie, catchment leakage en netwerkconnectiviteit.")

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

# Hulpfuncties om tabbladen flexibel aan elkaar te koppelen
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
    # Zoek op bestemming/route-naam (ongevoelig voor hoofdletters of GRQ- prefix)
    clean_kw = str(keyword).replace("GRQ-", "").replace("GRQ - ", "").strip()
    mask = df[col].astype(str).str.contains(clean_kw, case=False, na=False, regex=False)
    return df[mask]

# Upload functionaliteit in de zijbalk
uploaded_file = st.sidebar.file_uploader("Upload Excel-bestand (.xlsx)", type=["xlsx"])

if uploaded_file is None:
    st.info("👈 Upload in de linkerzijbalk een Excel-bestand (`.xlsx`) om het dashboard te laden.")
    st.stop()

all_data = load_all_sheets(uploaded_file)

if not all_data:
    st.stop()

# Dataframes ophalen
df_prop = all_data.get('Proposal Investigation', pd.DataFrame())
df_choice = all_data.get('Airport Choice', pd.DataFrame())
df_comp = all_data.get('Route Competitors', pd.DataFrame())
df_leak = all_data.get('Surface Leakage', pd.DataFrame())
df_conn = all_data.get('Weighted Connectivity', pd.DataFrame())

# 2. Tabs Structuur (Nieuw overkoepelend tabblad vooraan)
tab_overview, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Route Business Case (Totaalbeeld)",
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
    st.markdown("Selecteer een voorgestelde route of bestemming om alle databronnen (Leakage, Airport Choice, Concurrentie en Connectivity) samen te voegen tot één onderbouwing.")

    # Verzamel alle unieke routes/bestemmingen uit de tabbladen
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
        
        # Filter alle tabbladen voor deze specifieke route
        sub_prop = filter_by_keyword(df_prop, selected_route, ['Route', 'Destination', 'Routing'])
        sub_choice = filter_by_keyword(df_choice, selected_route, ['Route', 'Destination'])
        sub_comp = filter_by_keyword(df_comp, selected_route, ['Routing', 'Route', 'Destination'])
        sub_leak = filter_by_keyword(df_leak, selected_route, ['Destination', 'Route'])
        sub_conn = filter_by_keyword(df_conn, selected_route, ['Destination', 'Route', 'Routing', 'Hub', 'Airline'])

        # --- BEREKEN KERNCIJFERS & SCORE ---
        # 1. Surface Leakage
        leak_val = 0
        if not sub_leak.empty and 'Pax leakage' in sub_leak.columns:
            leak_val = pd.to_numeric(sub_leak['Pax leakage'], errors='coerce').sum()
        max_leak = pd.to_numeric(df_leak['Pax leakage'], errors='coerce').max() if ('Pax leakage' in df_leak.columns and not df_leak.empty) else 1
        leak_score = min((leak_val / max_leak) * 100, 100) if max_leak > 0 else 50

        # 2. Airport Choice (gemiddelde waarschijnlijkheid Business + Non-Business)
        prob_bus = pd.to_numeric(sub_choice['Probability% Business'], errors='coerce').mean() if ('Probability% Business' in sub_choice.columns and not sub_choice.empty) else 0
        prob_nonbus = pd.to_numeric(sub_choice['Probability% Non-Business'], errors='coerce').mean() if ('Probability% Non-Business' in sub_choice.columns and not sub_choice.empty) else 0
        avg_prob = max(prob_bus, prob_nonbus, (prob_bus + prob_nonbus) / 2)
        # Normaliseer als het een decimaal (0.45) is i.p.v. percentage (45)
        if 0 < avg_prob <= 1:
            avg_prob *= 100
            prob_bus *= 100
            prob_nonbus *= 100
        choice_score = min(avg_prob, 100) if avg_prob > 0 else 50

        # 3. Connectivity / Transfer Potential
        conn_days = sub_conn[sub_conn['Day outbound'] != 'AverageDay'] if ('Day outbound' in sub_conn.columns and not sub_conn.empty) else sub_conn
        if conn_days.empty and not df_conn.empty:
            # Fallback naar algemene hub-connectivity als route niet specifiek in connectivity-tab staat
            conn_days = df_conn[df_conn['Day outbound'] != 'AverageDay'] if 'Day outbound' in df_conn.columns else df_conn
        
        avg_trans = pd.to_numeric(conn_days['Transfer Potential'], errors='coerce').mean() if ('Transfer Potential' in conn_days.columns and not conn_days.empty) else 0
        if 0 < avg_trans <= 1:
            avg_trans *= 100
        conn_score = min(avg_trans, 100) if avg_trans > 0 else 50

        # 4. Concurrentie-intensiteit
        comp_freq = pd.to_numeric(sub_comp['Frequency per Week'], errors='coerce').sum() if ('Frequency per Week' in sub_comp.columns and not sub_comp.empty) else 0
        comp_pax = pd.to_numeric(sub_comp['PAX from catchment'], errors='coerce').sum() if ('PAX from catchment' in sub_comp.columns and not sub_comp.empty) else 0

        # Totale gewogen Route Viability Score (0 - 100)
        total_score = round((0.40 * leak_score) + (0.35 * choice_score) + (0.25 * conn_score), 1)

        # --- KPI BALK ---
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("🏆 Route Potentie Score", f"{total_score} / 100")
        k2.metric("💧 Surface Leakage (PAX)", f"{int(leak_val):,}".replace(",", ".") if leak_val > 0 else "Geen data")
        k3.metric("📊 Max GRQ Keuzekans", f"{avg_prob:.1f}%" if avg_prob > 0 else "Geen data")
        k4.metric("🥊 Concurrentie Freq/wk", f"{int(comp_freq)}x / week" if comp_freq > 0 else "0x (Unserved)")

        st.markdown("---")

        # --- AUTOMATISCHE ONDERBOUWING: WAAROM & WANNEER ---
        col_why, col_when = st.columns(2)

        with col_why:
            st.subheader("💡 Waarom scoort deze route goed?")
            reasons = []
            if leak_val > 0:
                reasons.append(f"• **Hoge terugwinbare vraag:** Er lekken momenteel **{int(leak_val):,} passagiers** uit het GRQ-verzorgingsgebied weg naar concurrerende luchthavens.".replace(",", "."))
            if prob_bus > 0 or prob_nonbus > 0:
                dom_segment = "Zakelijke reizigers (Business)" if prob_bus > prob_nonbus else "Vakantie/VFR-reizigers (Non-Business)"
                reasons.append(f"• **Sterke luchthavenvoorkeur:** GRQ behaalt een keuzekans van **{prob_bus:.1f}% (Business)** en **{prob_nonbus:.1f}% (Non-Business)**. Het primaire segment is **{dom_segment}**.")
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
            best_days = []

            # Bepaal beste dagen op basis van Transfer Potential in Weighted Connectivity
            if not conn_days.empty and {'Day outbound', 'Transfer Potential'}.issubset(conn_days.columns):
                day_perf = conn_days.groupby('Day outbound', as_index=False)['Transfer Potential'].mean()
                day_perf = day_perf.sort_values(by='Transfer Potential', ascending=False)
                top_days = day_perf.head(3)
                best_days = top_days['Day outbound'].tolist()
                days_formatted = ", ".join([f"**{row['Day outbound']}** ({row['Transfer Potential']*100 if row['Transfer Potential']<=1 else row['Transfer Potential']:.1f}%)" for _, row in top_days.iterrows()])
                schedule_advice.append(f"• **Beste dagen voor hub-connectiviteit:** {days_formatted} bieden de hoogste aansluitingswaarde.")

            # Koppel reizigerssegment (Business vs Non-Business) aan dagpatroon
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

            # Vlootadvies uit Connectivity tabblad
            fleet_col = find_col(sub_conn, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col and not sub_conn.empty:
                rec_fleet = sub_conn[fleet_col].mode()[0]
                schedule_advice.append(f"• **Aanbevolen toesteltype:** Op basis van de netwerkdata sluit een **{rec_fleet}** het beste aan op de capaciteits- en baanvereisten van GRQ.")

            if not schedule_advice:
                schedule_advice.append("• Voeg weekdagen en Transfer Potential toe in het tabblad *Weighted Connectivity* voor een specifiek dag- en tijdstipadvies.")

            st.markdown(f"<div class='insight-box'>{'<br><br>'.join(schedule_advice)}</div>", unsafe_allow_html=True)

        # --- VISUELE VERGELIJKING: SCORE OPBOUW & DAGPRESTATIES ---
        vis1, vis2 = st.columns(2)
        with vis1:
            st.subheader("Opbouw van de Route Potentie")
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
                color_discrete_sequence=['#00205B'],
                title=f"Deelscores voor {selected_route} (0-100)"
            )
            st.plotly_chart(fig_factors, use_container_width=True)

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
                    color_discrete_sequence=['#00205B', '#BFCCDE', '#9CA3AF'],
                    title="Connectiviteit per Weekdag"
                )
                st.plotly_chart(fig_days, use_container_width=True)
            else:
                st.info("Geen weekdag-data beschikbaar in 'Weighted Connectivity'.")

        # --- SAMENVATTINGSTABEL VAN ALLE ROUTES ---
        st.markdown("---")
        st.subheader("📋 Vergelijking van alle Voorgestelde Routes (Ranking)")
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
                    color_discrete_sequence=['#00205B', '#BFCCDE'],
                    title="Business PAX per Route"
                )
                st.plotly_chart(fig_bus, use_container_width=True)
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
                    color_discrete_sequence=['#BFCCDE', '#00205B'],
                    title="Non-Business PAX per Route"
                )
                st.plotly_chart(fig_nonbus, use_container_width=True)
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
                    title="Wekelijkse Frequentie"
                )
                st.plotly_chart(fig_freq, use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_comp.columns)}")

        with c2:
            st.subheader("PAX uit Catchment per Routing")
            if {'Routing', 'PAX from catchment'}.issubset(df_comp.columns):
                fig_pax = px.bar(
                    df_comp, 
                    x='Routing', 
                    y='PAX from catchment', 
                    title="Passagiers uit Catchment Zone"
                )
                st.plotly_chart(fig_pax, use_container_width=True)
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
                title="Pax Leakage per Bestemming"
            )
            st.plotly_chart(fig_leak, use_container_width=True)
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
                    title="Transfer Potential % gedurende de week"
                )
                st.plotly_chart(fig_trans, use_container_width=True)
            else:
                st.warning(f"Kolommen niet gevonden. Beschikbaar: {list(df_conn.columns)}")
            
        with col2:
            st.subheader("Inzetbare Vloot (Fleet)")
            fleet_col = find_col(df_conn, ['Fleet', 'Aircraft', 'Aircraft Type', 'Equipment'])
            if fleet_col:
                fleet_counts = df_conn[fleet_col].value_counts().reset_index()
                fleet_counts.columns = ['Fleet', 'Aantal']
                fig_fleet = px.pie(fleet_counts, names='Fleet', values='Aantal', hole=0.4)
                st.plotly_chart(fig_fleet, use_container_width=True)
            else:
                st.warning(f"Kolom 'Fleet' niet gevonden. Beschikbare kolommen: {list(df_conn.columns)}")

        st.dataframe(df_conn, use_container_width=True, hide_index=True)
    else:
        st.info("Geen data beschikbaar in 'Weighted Connectivity'.")
