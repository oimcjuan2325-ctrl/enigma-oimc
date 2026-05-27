import streamlit as st
import datetime
import json
import os

# --- CONFIGURACIÓN Y PERSISTENCIA ---
ARCHIVO_DATOS = "codex_data.json"
ABECEDARIO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
USUARIOS = {
    "2313": "Juan", "2021": "Asier", "1365": "Jesús",
    "1460": "Yolanda", "2013": "Mikel", "9837": "Gaizka",
    "7467": "Iñaki", "7562": "Erika", "9786": "Nahia",
    "1053": "Amets", "2325": "MÁQUINA ENIGMA"
}

def guardar_en_disco():
    datos = {
        "archivo": st.session_state.archivo_mensajes,
        "interceptados": st.session_state.interceptados
    }
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump(datos, f)

def cargar_desde_disco():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r") as f:
            datos = json.load(f)
            st.session_state.archivo_mensajes = datos.get("archivo", {})
            st.session_state.interceptados = datos.get("interceptados", [])
    else:
        st.session_state.archivo_mensajes = {}
        st.session_state.interceptados = []

# --- LÓGICA DEL MOTOR ENIGMA ---
def calcular_desfase(fecha):
    factor = (fecha.year * 13) + (fecha.month * 31) + (fecha.day ** 2) + (fecha.isocalendar()[1] * 7)
    return factor % 27

def motor_enigma(texto, desfase, modo='cifrar'):
    n = 27
    desp = desfase if modo == 'cifrar' else -desfase
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
if 'usuario_logueado' not in st.session_state: st.session_state.usuario_logueado = None
if 'datos_cargados' not in st.session_state:
    cargar_desde_disco()
    st.session_state.datos_cargados = True

# --- INTERFAZ ---
st.set_page_config(page_title="CODEX DELTA", page_icon="🔐", layout="centered")

if st.session_state.usuario_logueado is None:
    st.title("🔒 ACCESO CIFRADO")
    pin = st.text_input("PIN:", type="password")
    if st.button("ENTRAR"):
        if pin in USUARIOS:
            st.session_state.usuario_logueado = USUARIOS[pin]
            st.rerun()
        else: st.error("PIN INVÁLIDO")
else:
    st.sidebar.write(f"**Operativo:** {st.session_state.usuario_logueado}")
    if st.sidebar.button("CERRAR SESIÓN"):
        st.session_state.usuario_logueado = None
        st.rerun()

    st.title("CODEX DELTA")

    # 1. CIFRADO
    st.header("1. Cifrado")
    msg_input = st.text_input("Mensaje a cifrar:")
    if st.button("CIFRAR"):
        desfase = calcular_desfase(datetime.date.today())
        st.code(motor_enigma(msg_input, desfase, 'cifrar'))

    # 2. DESCIFRADO
    st.write("---")
    st.header("2. Descifrado")
    fecha_dec = st.date_input("Fecha del mensaje:")
    cifrado_in = st.text_input("Pegar mensaje cifrado:")
    if st.button("DESCIFRAR"):
        st.success(f"Resultado: {motor_enigma(cifrado_in, calcular_desfase(fecha_dec), 'descifrar')}")

    # 3. ARCHIVO DE INTELIGENCIA
    st.write("---")
    st.header("3. Archivo de Inteligencia")
    with st.expander("💾 Guardar mensaje"):
        msg_to_save = st.text_input("Mensaje cifrado:")
        fecha_save = st.date_input("Fecha:")
        if st.button("GUARDAR"):
            f_str = str(fecha_save)
            if f_str not in st.session_state.archivo_mensajes: st.session_state.archivo_mensajes[f_str] = []
            st.session_state.archivo_mensajes[f_str].append(msg_to_save)
            guardar_en_disco()
            st.success("Guardado permanentemente.")
    
    fecha_query = st.date_input("Consultar fecha:")
    if st.button("BUSCAR"):
        for m in st.session_state.archivo_mensajes.get(str(fecha_query), []): st.code(m)

    # 4. INTERCEPCIÓN
    st.write("---")
    st.header("📡 Módulo de Interceptación")
    with st.expander("📝 Registrar nueva interceptación"):
        with st.form("interceptor_form", clear_on_submit=True):
            code_int = st.text_input("Código interceptado:")
            origen_int = st.text_input("Fuente (Opcional):")
            if st.form_submit_button("REGISTRAR"):
                if code_int:
                    st.session_state.interceptados.append({"codigo": code_int, "origen": origen_int or "Desconocido"})
                    guardar_en_disco()
                    st.success("Registrado permanentemente.")
    
    if st.session_state.interceptados:
        st.subheader("Códigos bajo análisis:")
        for m in st.session_state.interceptados:
            col1, col2 = st.columns([3, 1])
            with col1: st.warning(f"DE: {m['origen']} | CÓDIGO: {m['codigo']}")
            with col2: st.link_button("🤖 MODO IA", "https://www.google.com")
