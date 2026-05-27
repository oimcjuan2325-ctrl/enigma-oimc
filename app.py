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
if 'archivo_mensajes' not in st.session_state: st.session_state.archivo_mensajes = {}
if 'interceptados' not in st.session_state: st.session_state.interceptados = []

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
        cifrado = motor_enigma(msg_input, desfase, 'cifrar')
        st.code(cifrado)

    # 2. DESCIFRADO
    st.write("---")
    st.header("2. Descifrado")
    fecha_dec = st.date_input("Fecha del mensaje:")
    cifrado_in = st.text_input("Pegar mensaje cifrado:")
    if st.button("DESCIFRAR"):
        desfase = calcular_desfase(fecha_dec)
        res = motor_enigma(cifrado_in, desfase, 'descifrar')
        st.success(f"Resultado: {res}")

    # 3. ARCHIVO DE INTELIGENCIA
    st.write("---")
    st.header("3. Archivo de Inteligencia")
    with st.expander("💾 Guardar mensaje en archivo"):
        msg_to_save = st.text_input("Mensaje cifrado a guardar:")
        fecha_save = st.date_input("Fecha original:")
        if st.button("GUARDAR"):
            fecha_str = str(fecha_save)
            if fecha_str not in st.session_state.archivo_mensajes: st.session_state.archivo_mensajes[fecha_str] = []
            st.session_state.archivo_mensajes[fecha_str].append(msg_to_save)
            st.success("Guardado.")
    
    fecha_query = st.date_input("Consultar fecha:")
    if st.button("BUSCAR ARCHIVOS"):
        mensajes = st.session_state.archivo_mensajes.get(str(fecha_query), [])
        for m in mensajes: st.code(m)

    # 4. MÓDULO DE INTERCEPCIÓN (Fuente Opcional)
    st.write("---")
    st.header("📡 Módulo de Interceptación")
    with st.expander("📝 Registrar nueva interceptación"):
        with st.form("interceptor_form", clear_on_submit=True):
            code_int = st.text_input("Código interceptado:")
            origen_int = st.text_input("Fuente (Opcional):")
            if st.form_submit_button("REGISTRAR"):
                if not code_int:
                    st.error("Error: El Código es obligatorio.")
                else:
                    origen = origen_int if origen_int else "Desconocido"
                    st.session_state.interceptados.append({"codigo": code_int, "origen": origen})
                    st.success("Mensaje registrado.")

    if st.session_state.interceptados:
        st.subheader("Códigos bajo análisis:")
        for m in st.session_state.interceptados:
            col1, col2 = st.columns([3, 1])
            with col1: st.warning(f"DE: {m['origen']} | CÓDIGO: {m['codigo']}")
            with col2: st.link_button("🤖 MODO IA", "https://www.google.com")
