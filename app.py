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

# --- LÓGICA DEL MOTOR ENIGMA (NUEVA FÓRMULA DE ALTA SEGURIDAD) ---
def calcular_desfase(fecha):
    # Fórmula de alta volatilidad: los resultados varían drásticamente día a día
    factor = (fecha.year * 13) + (fecha.month * 31) + (fecha.day ** 2) + (fecha.isocalendar()[1] * 7)
    return factor % 27

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

# --- INTERFAZ ---
st.set_page_config(page_title="CODEX DELTA", page_icon="🔐", layout="centered")

if st.session_state.usuario_logueado is None:
    st.title("🔒 ACCESO CIFRADO")
    pin = st.text_input("PIN:", type="password")
    if st.button("ENTRAR"):
        if pin in USUARIOS:
            st.session_state.usuario_logueado = USUARIOS[pin]
            st.rerun()
        else:
            st.error("PIN INVÁLIDO")
else:
    usuario = st.session_state.usuario_logueado
    st.sidebar.write(f"**Operativo:** {usuario}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state.usuario_logueado = None
        st.rerun()

    st.title("CODEX DELTA")

    # 1. CIFRADO
    st.header("1. Cifrado")
    msg_input = st.text_input("Mensaje a cifrar:")
    if st.button("CIFRAR"):
        desfase = calcular_desfase(datetime.date.today())
        cifrado = motor_enigma(msg_input, desfase, 'cifrar')
        st.code(cifrado)

    # 2. DESCIFRADO
    st.write("---")
    st.header("2. Descifrado")
    fecha_input = st.date_input("Fecha del mensaje:")
    cifrado_in = st.text_input("Pegar mensaje cifrado:")
    if st.button("DESCIFRAR"):
        desfase = calcular_desfase(fecha_input)
        res = motor_enigma(cifrado_in, desfase, 'descifrar')
        st.success(f"Resultado: {res}")
