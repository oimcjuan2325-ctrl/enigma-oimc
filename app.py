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
    
    if modo == 'descifrar': resultado = resultado[::-1]
    return resultado

# --- ESTADO DE SESIÓN ---
if 'usuario_logueado' not in st.session_state: st.session_state.usuario_logueado = None

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
    
    st.sidebar.divider()
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state.usuario_logueado = None
        st.rerun()

    st.title("CENTRO DE MANDO CODEX DELTA")
    
    # SECCIÓN 1: CIFRADO
    st.header("1. Sección de Cifrado")
    col_dest, col_msg = st.columns([1, 2])
    with col_dest:
        destinatario = st.selectbox("DESTINATARIO:", 
                                    ["OIMC_GRUPO", "JUAN", "ASIER", "JESÚS", "YOLANDA", "MIKEL", "GAIZKA", "IÑAKI", "ERIKA", "NAHIA", "AMETS"])
    with col_msg:
        msg_input = st.text_input("Mensaje a enviar:")
    
    if st.button("CIFRAR", use_container_width=True):
        if msg_input:
            desfase_hoy = calcular_desfase(datetime.date.today())
            cifrado = motor_enigma(msg_input, desfase_hoy, 'cifrar')
            paquete = f"DE:{usuario} | PARA:{destinatario} | MSG:{cifrado}"
            st.code(paquete)
            st.success(f"Mensaje cifrado y listo para transmitir a {destinatario}.")

    # SECCIÓN 2: DESCIFRADO
    st.write("---")
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
            # Limpiamos el paquete si viene con formato DE:X|PARA:Y|MSG:Z
            texto_limpio = cifrado_in.split("MSG:")[-1] if "MSG:" in cifrado_in else cifrado_in
            res = motor_enigma(texto_limpio.strip(), desfase_calculado, 'descifrar')
            st.success(f"MENSAJE RECUPERADO:\n**{res}**")
