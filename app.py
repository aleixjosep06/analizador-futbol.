import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Predictor de Valor Futbolístico", page_icon="⚽")

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .valor-box {
        background-color: #d4edda;
        color: #155724;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        text-align: center;
        font-weight: bold;
        font-size: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ Analizador de Valor: Apuestas de Fútbol")
st.write("Calcula la probabilidad real de un partido y encuentra cuotas con valor.")

# --- BARRA LATERAL: CONFIGURACIÓN GENERAL ---
st.sidebar.header("⚙️ Configuración de la Liga")
promedio_liga = st.sidebar.slider("Promedio Goles Local (Liga)", 0.5, 2.5, 1.35, 0.05)

# --- SECCIÓN 1: EQUIPOS ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 Equipo Local")
    nombre_local = st.text_input("Nombre Local", "Celtic FC")
    ataque_local = st.slider("Fuerza Ataque Local", 0.1, 3.0, 1.5, 0.1)
    defensa_local = st.slider("Fuerza Defensa Local", 0.1, 3.0, 1.0, 0.1)

with col2:
    st.subheader("🚌 Equipo Visitante")
    nombre_visitante = st.text_input("Nombre Visitante", "Celta de Vigo")
    ataque_visitante = st.slider("Fuerza Ataque Visitante", 0.1, 3.0, 1.0, 0.1)
    defensa_visitante = st.slider("Fuerza Defensa Visitante", 0.1, 3.0, 1.0, 0.1)

# --- SECCIÓN 2: CUOTAS ---
st.divider()
st.subheader("💰 Cuotas de la Casa de Apuestas")
c_col1, c_col2, c_col3 = st.columns(3)
with c_col1:
    cuota_local = st.number_input(f"Cuota {nombre_local}", min_value=1.01, value=1.80)
with c_col2:
    cuota_empate = st.number_input("Cuota Empate", min_value=1.01, value=3.50)
with c_col3:
    cuota_visitante = st.number_input(f"Cuota {nombre_visitante}", min_value=1.01, value=4.20)

# --- MOTOR de CÁLCULO ---
def calcular_prediccion():
    # Cálculo de xG (Goles Esperados)
    lambda_local = ataque_local * defensa_visitante * promedio_liga
    lambda_visitante = ataque_visitante * defensa_local * promedio_liga

    prob_local = 0
    prob_empate = 0
    prob_visitante = 0

    for i in range(10):
        for j in range(10):
            p = poisson.pmf(i, lambda_local) * poisson.pmf(j, lambda_visitante)
            if i > j: prob_local += p
            elif i == j: prob_empate += p
            else: prob_visitante += p

    return prob_local, prob_empate, prob_visitante, lambda_local, lambda_visitante

# Ejecutar cálculo
p_local, p_empate, p_visitante, xg_l, xg_v = calcular_prediccion()

# --- RESULTADOS VISUALES ---
st.divider()
st.subheader("📊 Resultados del Análisis")

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric(f"Prob. {nombre_local}", f"{p_local*100:.1f}%")
res_col2.metric("Prob. Empate", f"{p_empate*100:.1f}%")
res_col3.metric(f"Prob. {nombre_visitante}", f"{p_visitante*100:.1f}%")

st.info(f"**Goles Esperados (xG):** {nombre_local} {xg_l:.2f} - {nombre_visitante} {xg_v:.2f}")

# --- ANÁLISIS DE VALOR ---
st.subheader("🎯 Recomendación de Apuesta")

resultados = {
    nombre_local: (p_local, cuota_local),
    "Empate": (p_empate, cuota_empate),
    nombre_visitante: (p_visitante, cuota_visitante)
}

encontrado_valor = False
for resultado, datos in resultados.items():
    prob, cuota = datos
    cuota_justa = 1 / prob if prob > 0 else 999
    
    if cuota > cuota_justa:
        encontrado_valor = True
        ventaja = (cuota / cuota_justa) - 1
        st.markdown(f"""
            <div class="valor-box">
                🚀 ¡VALOR ENCONTRADO! <br>
                Apuesta a: {resultado} <br>
                Cuota Justa: {cuota_justa:.2f} | Cuota Casa: {cuota} <br>
                Ventaja Estadística: {ventaja:.1%}
            </div>
            """, unsafe_allow_html=True)
        st.write("")

if not encontrado_valor:
    st.warning("No se encontró valor en ninguna de las tres opciones. El riesgo es mayor que la recompensa.")

st.caption("Nota: Este software es una herramienta estadística. El fútbol es impredecible. Apuesta con responsabilidad.")
