import streamlit as st
import datetime

# --- CONFIGURACIÓN ---
ABECEDARIO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
USUARIOS = {
    "2313": "Juan", "2021": "Asier", "1365": "Jesús",
    "1460": "Yolanda", "2013": "Mikel", "9837": "Gaizka",
    "7467": "Iñaki", "7562": "Erika", "9786": "Nahia",
    "1053": "Amets", "2325": "MÁQUINA ENIGMA"
}

# --- LÓGICA DEL MOTOR ENIGMA ---
def calcular_desfase(fecha):
    semana = fecha.isocalendar()[1]
    dia_semana = fecha.isoweekday()
    return ((fecha.day * fecha.month) + (semana * dia_semana) + (fecha.year % 100)) % 27

def motor_enigma(texto, desfase, modo='cifrar'):
    n = 27
    desp = desfase if modo == 'cifrar' else -desfase
    if modo == 'cifrar': texto = texto[::-1] # Capa Anti-IA
    
    resultado = ""
    for char in texto.upper():
        if char in ABECEDARIO:
            idx = (ABECEDARIO.index(char) + desp) % n
            resultado += ABECEDARIO[idx]
        else: resultado += char
    
    if modo == 'descifrar': resultado = resultado[::-1] # Inversión final
    return resultado

# --- ESTADO DE SESIÓN ---
if 'usuario_logueado' not in st.session_state: st.session_state.usuario_logueado = None
if 'historial' not in st.session_state: st.session_state.historial = []

# --- INTERFAZ ---
st.set_page_config(page_title="CODEX DELTA", page_icon="🔐", layout="wide")

if st.session_state.usuario_logueado is None:
    st.title("🔒 ACCESO CIFRADO CODEX DELTA")
    pin = st.text_input("Introduce tu PIN de acceso:", type="password")
    if st.button("INICIAR SESIÓN"):
        if pin in USUARIOS:
            st.session_state.usuario_logueado = USUARIOS[pin]
            st.rerun()
        else:
            st.error("PIN NO RECONOCIDO")
else:
    usuario = st.session_state.usuario_logueado
    st.sidebar.title(f"OPERATIVO: {usuario}")
    
    if usuario == "MÁQUINA ENIGMA":
        st.sidebar.divider()
        st.sidebar.subheader("⚙️ MODO ADMINISTRADOR")
        st.sidebar.info(f"Rotor activo hoy: {calcular_desfase(datetime.date.today())}")
    
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state.usuario_logueado = None
        st.rerun()

    st.title("CENTRO DE MANDO CODEX DELTA")
    
    # SECCIÓN 1: CIFRADO
    st.header("1. Sección de Cifrado")
    msg_input = st.text_input("Mensaje a enviar:")
    if st.button("CIFRAR Y ENVIAR"):
        desfase_hoy = calcular_desfase(datetime.date.today())
        cifrado = motor_enigma(msg_input, desfase_hoy, 'cifrar')
        st.session_state.historial.append(f"{usuario} [{datetime.date.today()}]: {cifrado}")
        st.code(f"PAQUETE: {cifrado}")

    # SECCIÓN 2: DESCIFRADO
    st.header("2. Módulo de Descifrado Táctico")
    col1, col2 = st.columns([1, 2])
    with col1:
        fecha_input = st.date_input("Fecha de envío del mensaje:", datetime.date.today())
        desfase_calculado = calcular_desfase(fecha_input)
        st.write(f"Desfase calculado: **{desfase_calculado}**")
    with col2:
        cifrado_in = st.text_input("Pegar código recibido:")
    
    if st.button("EJECUTAR DESCIFRADO", use_container_width=True):
        if cifrado_in:
            res = motor_enigma(cifrado_in, desfase_calculado, 'descifrar')
            st.success(f"MENSAJE RECUPERADO:\n**{res}**")

    # SECCIÓN 3: BANDEJA DE ENTRADA
    st.write("---")
    st.subheader("Bandeja de Entrada (Últimos mensajes)")
    for m in st.session_state.historial[-5:]:
        st.text(m)
