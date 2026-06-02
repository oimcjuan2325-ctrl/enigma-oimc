import streamlit as st
import os
import datetime
import json

# --- 1. CONFIGURACIÓN Y USUARIOS ---
USUARIOS = {
    "Juan": "2313", "Asier": "2021", "Jesús": "1365", "Yolanda": "1460",
    "Mikel": "2013", "Gaizka": "9837", "Iñaki": "7467", "Erika": "7562",
    "Nahia": "9786", "Amets": "1053", "MAQUINA_ENIGMA": "2325"
}

# --- 2. MOTOR DEL CODEX CELTA 2.0 (Lógica Matemática) ---
def motor_codex(texto, es_cifrado, fecha_input):
    # Extracción de valores de la fecha seleccionada
    mes = fecha_input.month
    dia = fecha_input.day
    
    # Tu fórmula: (Mes + Día + ClaveNumérica) / 2
    # El 10 es un valor constante de tu esquema (puedes ajustarlo)
    base_calculo = (mes + dia + 10) 
    cociente = base_calculo / 2
    resto = base_calculo % 2
    
    # Factor: últimos dos dígitos del cociente
    factor = int(str(int(cociente))[-2:]) if cociente >= 10 else int(cociente)
    desfase = (resto * factor) % 26
    
    # Aplicar o revertir desplazamiento
    valor = desfase if es_cifrado else -desfase
    resultado = ""
    for char in texto.upper():
        if char.isalpha():
            resultado += chr(((ord(char) - 65 + valor) % 26) + 65)
        else:
            resultado += char
    return resultado

# --- 3. PERSISTENCIA DE DATOS ---
def guardar_mensaje(usuario, msg_cifrado, fecha):
    if not os.path.exists("data_oimc"): os.makedirs("data_oimc")
    with open(f"data_oimc/{usuario}.txt", "a") as f:
        f.write(json.dumps({"fecha": fecha.strftime("%d/%m/%Y"), "msg": msg_cifrado}) + "\n")

# --- 4. INTERFAZ DE USUARIO ---
st.set_page_config(page_title="Central OIMC", layout="wide")

if 'login' not in st.session_state: st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 Central de Cifrado OIMC")
    u = st.text_input("Usuario")
    p = st.text_input("PIN", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.login = True
            st.session_state.user = u
            st.rerun()
        else: st.error("Acceso denegado")
else:
    # Barra lateral
    st.sidebar.title(f"Operativo: {st.session_state.user}")
    
    # Panel Máquina Enigma
    if st.session_state.user == "MAQUINA_ENIGMA":
        if st.sidebar.button("⚙️ Administrar Central"):
            st.session_state.admin = True
    
    if st.session_state.get('admin'):
        st.subheader("Panel Máquina Enigma")
        target = st.selectbox("Seleccionar Operativo", [u for u in USUARIOS if u != "MAQUINA_ENIGMA"])
        if st.button("Ver archivos del operativo"):
            ruta = f"data_oimc/{target}.txt"
            if os.path.exists(ruta):
                with open(ruta, "r") as f:
                    for l in f:
                        data = json.loads(l)
                        st.write(f"📅 {data['fecha']} | ✉️ {data['msg']}")
            else: st.info("Esta persona aún no tiene mensajes guardados.")

    # Acciones principales
    st.title("🗂️ Central de Operaciones OIMC")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cifrado")
        msg = st.text_area("Mensaje a cifrar")
        if st.button("Cifrar mensaje"):
            fecha_hoy = datetime.date.today()
            st.session_state.cifrado_temp = motor_codex(msg, True, fecha_hoy)
            st.code(st.session_state.cifrado_temp)
            
        if st.button("Guardar en mi archivo"):
            if 'cifrado_temp' in st.session_state:
                guardar_mensaje(st.session_state.user, st.session_state.cifrado_temp, datetime.date.today())
                st.success("Guardado en la base de datos OIMC.")
            else: st.warning("Cifra un mensaje primero.")

    with col2:
        st.subheader("Descifrado")
        msg_c = st.text_input("Mensaje cifrado")
        fecha_c = st.date_input("Fecha de cifrado original")
        if st.button("Descifrar"):
            resultado = motor_codex(msg_c, False, fecha_c)
            st.write(f"**Resultado:** {resultado}")

    if st.sidebar.button("Cerrar Sesión"):
        for key in st.session_state.keys(): del st.session_state[key]
        st.rerun()
