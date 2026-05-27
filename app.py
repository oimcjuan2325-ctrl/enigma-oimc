import streamlit as st
import datetime

# --- CONFIGURACIÓN DEL MOTOR ---
ABECEDARIO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

def obtener_desfase_diario():
    hoy = datetime.date.today()
    semana = hoy.isocalendar()[1]
    dia_semana = hoy.isoweekday()
    # Fórmula de desfase: Día*Mes + Semana*DiaSemana + Año
    return ((hoy.day * hoy.month) + (semana * dia_semana) + (hoy.year % 100)) % 27

def motor_enigma(texto, desfase, modo='cifrar'):
    n = 27
    desp = desfase if modo == 'cifrar' else -desfase
    
    # Capa Anti-IA: Inversión del texto
    if modo == 'cifrar': texto = texto[::-1]
    
    resultado = ""
    for char in texto.upper():
        if char in ABECEDARIO:
            idx = (ABECEDARIO.index(char) + desp) % n
            resultado += ABECEDARIO[idx]
        else: resultado += char
            
    if modo == 'descifrar': resultado = resultado[::-1]
    return resultado

# --- ESTADO DE SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'historial' not in st.session_state: st.session_state.historial = []

# --- INTERFAZ DE LOGIN ---
if not st.session_state.autenticado:
    st.set_page_config(page_title="Acceso O.I.M.C.", page_icon="🔐")
    st.title("🔒 ACCESO O.I.M.C.")
    if st.text_input("Clave de Acceso:", type="password") == "OIMC2026":
        st.session_state.autenticado = True
        st.rerun()
else:
    st.set_page_config(page_title="Centro de Mando O.I.M.C.", page_icon="🔐", layout="wide")
    
    # --- BARRA LATERAL ---
    st.sidebar.title("🔐 SESIÓN ACTIVA")
    usuario = st.sidebar.selectbox("Miembro:", ["JUAN (LÍDER)", "GAIZKA", "IÑAKI", "MIKEL"])
    
    if usuario == "JUAN (LÍDER)":
        st.sidebar.info(f"⚙️ Desfase técnico hoy: {obtener_desfase_diario()}")
    
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state.autenticado = False
        st.rerun()

    # --- ZONA PRINCIPAL ---
    st.title("CENTRO DE MANDO O.I.M.C.")
    st.write("---")

    # ZONA 1: CHAT Y CIFRADO
    st.header("1. Chat de Operaciones")
    col_dest, col_msg = st.columns([1, 3])
    with col_dest:
        destinatario = st.selectbox("PARA:", ["OIMC_GRUPO", "GAIZKA", "IÑAKI", "MIKEL"])
    with col_msg:
        msg_input = st.text_input("Mensaje a enviar:")

    if st.button("CIFRAR Y ENVIAR", use_container_width=True):
        if msg_input:
            msg_cifrado = motor_enigma(msg_input, obtener_desfase_diario(), 'cifrar')
            paquete = f"DE:{usuario} | PARA:{destinatario} | MSG:{msg_cifrado}"
            st.session_state.historial.append(paquete)
            st.toast("Mensaje enviado y cifrado.")

    st.subheader("Bandeja de Entrada (Cifrada)")
    with st.expander("Ver historial reciente", expanded=True):
        for m in st.session_state.historial[-10:]:
            st.text(m)

    # ZONA 2: MÓDULO TÁCTICO DE DESCIFRADO
    st.write("---")
    st.header("2. Módulo de Descifrado Táctico")
    col1, col2 = st.columns([1, 2])
    with col1:
        desfase_input = st.number_input("Ajustar Desfase:", min_value=0, max_value=26, value=obtener_desfase_diario())
    with col2:
        cifrado_in = st.text_input("Pegar paquete de datos recibido:")
    
    if st.button("EJECUTAR DESCIFRADO", use_container_width=True):
        if cifrado_in:
            # Limpiamos el texto si viene con formato "DE:X | PARA:Y | MSG:Z"
            texto_a_procesar = cifrado_in.split("MSG:")[-1] if "MSG:" in cifrado_in else cifrado_in
            res = motor_enigma(texto_a_procesar.strip(), desfase_input, 'descifrar')
            st.success(f"MENSAJE RECUPERADO:\n**{res}**")
