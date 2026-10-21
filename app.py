import streamlit as st
import requests
import pandas as pd
from scipy.stats import poisson

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AI Football Predictor Pro", page_icon="⚽")

# SUSTITUYE ESTO POR TU CLAVE DE RAPIDAPI
API_KEY = "ee46bff398msh8528abea39c4e21p1c1199jsna65d879bc991" 
API_HOST = "api-football-v1.p.rapidapi.com"

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

# --- FUNCIONES DE API ---
def buscar_equipo(nombre):
    url = f"https://{API_HOST}/v3/teams"
    params = {"search": nombre}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        data = response.json()
        if data.get('response'):
            return data['response'][0]
    except:
        return None
    return None

def obtener_estadisticas(team_id, league_id, season):
    url = f"https://{API_HOST}/v3/teams/statistics"
    params = {"team": team_id, "league": league_id, "season": season}
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        return response.json().get('response', {})
    except:
        return {}

def obtener_promedio_liga(league_id, season):
    return 1.35 

# --- INTERFAZ VISUAL ---
st.title("⚽ AI Predictor Pro: Automatizado")
st.write("Busca cualquier equipo del mundo y analiza el valor de la apuesta.")

col1, col2 = st.columns(2)
with col1:
    local_query = st.text_input("Equipo Local", "Celtic")
with col2:
    visitante_query = st.text_input("Equipo Visitante", "Celta de Vigo")

if st.button("🚀 Analizar Partido"):
    with st.spinner("Buscando datos en tiempo real..."):
        team_l = buscar_equipo(local_query)
        team_v = buscar_equipo(visitante_query)

        if team_l and team_v:
            l_id = team_l['team']['id']
            v_id = team_v['team']['id']
            l_name = team_l['team']['name']
            v_name = team_v['team']['name']
            l_league = team_l['league']['id']
            
            stats_l = obtener_estadisticas(l_id, l_league, "2023")
            stats_v = obtener_estadisticas(v_id, l_league, "2023")

            try:
                goles_l = stats_l.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.3)
                goles_v = stats_v.get('goals', {}).get('for', {}).get('average', {}).get('total', 1.1)
                def_l = stats_l.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.0)
                def_v = stats_v.get('goals', {}).get('against', {}).get('average', {}).get('total', 1.0)
            except:
                goles_l, goles_v, def_l, def_v = 1.3, 1.1, 1.0, 1.0

            promedio_liga = obtener_promedio_liga(l_league, "2023")
            ataque_l = goles_l / promedio_liga
            defensa_l = def_l / promedio_liga
            ataque_v = goles_v / promedio_liga
            defensa_v = def_v / promedio_liga

            lambda_l = ataque_l * defensa_v * promedio_liga
            lambda_v = ataque_v * defensa_l * promedio_liga

            p_l, p_e, p_v = 0, 0, 0
            for i in range(10):
                for j in range(10):
                    prob = poisson.pmf(i, lambda_l) * poisson.pmf(j, lambda_v)
                    if i > j: p_l += prob
                    elif i == j: p_e += prob
                    else: p_v += prob

            st.divider()
            st.subheader(f"📊 {l_name} vs {v_name}")
            c1, c2, c3 = st.columns(3)
            c1.metric(l_name, f"{p_l*100:.1f}%")
            c2.metric("Empate", f"{p_e*100:.1f}%")
            c3.metric(v_name, f"{p_v*100:.1f}%")

            st.info(f"Goles Esperados: {l_name} {lambda_l:.2f} - {v_name} {lambda_v:.2f}")

            st.divider()
            st.subheader("💰 Comparador de Valor")
            col_q1, col_q2, col_q3 = st.columns(3)
            q_l = col_q1.number_input(f"Cuota {l_name}", value=1.80)
            q_e = col_q2.number_input("Cuota Empate", value=3.50)
            q_v = col_q3.number_input(f"Cuota {v_name}", value=4.00)

            for nombre, prob, cuota in [(l_name, p_l, q_l), ("Empate", p_e, q_e), (v_name, p_v, q_v)]:
                cuota_justa = 1/prob if prob > 0 else 999
                if cuota > cuota_justa:
                    st.success(f"✅ VALOR en {nombre}: Cuota Casa {cuota} > Justa {cuota_justa:.2f}")

        else:
            st.error("No se encontraron los equipos. Intenta escribirlos exactamente como aparecen en la liga.")
