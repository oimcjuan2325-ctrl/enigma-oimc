import streamlit as st
import os
import datetime
import json

# --- BASE DE DATOS DE USUARIOS ---
USUARIOS = {
    "Juan": "2313", "Asier": "2021", "Jesús": "1365", "Yolanda": "1460",
    "Mikel": "2013", "Gaizka": "9837", "Iñaki": "7467", "Erika": "7562",
    "Nahia": "9786", "Amets": "1053", "MAQUINA_ENIGMA": "2325"
}

# --- MOTOR MATEMÁTICO: CODEX CELTA 2.0 ---
def calcular_desplazamiento(mensaje, es_cifrado):
    # Lógica basada en tu explicación: (Mes + Día + PalabraClave) / 2
    # + Multiplicación por los últimos 2 dígitos del cociente
    fecha = datetime.datetime.now()
    mes = fecha.month
    dia = fecha.day
    
    # Simulación del cálculo de la "sobra" (resto) y el "desfase"
    base = (mes + dia + 50) 
    cociente = base / 2
    resto = base % 2
    
    # Extraer últimos 2 dígitos del cociente para el factor
    factor = int(str(int(cociente))[-2:])
    desplazamiento = (resto * factor) % 26
    
    if not es_cifrado: desplazamiento = -desplazamiento
    return desplazamiento

def procesar_codex(texto, es_cifrado):
    desfase = calcular_desplazamiento(texto, es_cifrado)
    resultado = ""
    for char in texto.upper():
        if char.isalpha():
            resultado += chr(((ord(char) - 65 + desfase) % 26) + 65)
        else:
            resultado += char
    return resultado

# --- INTERFAZ Y LÓGICA ---
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
    # --- MENÚ Y ADMINISTRACIÓN ---
    st.sidebar.title(f"Operativo: {st.session_state.user}")
    
    if st.session_state.user == "MAQUINA_ENIGMA":
        st.sidebar.subheader("⚙️ ADMINISTRACIÓN")
        if st.sidebar.button("Administrar Central"):
            st.session_state.modo_admin = True
    
    if st.session_state.get('modo_admin'):
        st.title("⚙️ Panel Máquina Enigma")
        target = st.selectbox("Seleccionar Operativo", [u for u in USUARIOS if u != "MAQUINA_ENIGMA"])
        if st.button("Revisar Base de Datos"):
            ruta = f"data_oimc/{target}.txt"
            if os.path.exists(ruta):
                with open(ruta, "r") as f:
                    for l in f:
                        data = json.loads(l)
                        st.write(f"📅 {data['fecha']} | ✉️ {data['msg']}")
            else: st.info("De momento esta persona no ha guardado ningún mensaje.")
    
    # --- OPERACIONES ---
    st.title("🗂️ Central de Operaciones OIMC")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cifrar y Guardar")
        msg = st.text_area("Mensaje")
        if st.button("Cifrar y Guardar"):
            if msg:
                fecha_hoy = datetime.date.today().strftime("%d/%m/%Y")
                cifrado = procesar_codex(msg, True)
                # Guardar persistente
                if not os.path.exists("data_oimc"): os.makedirs("data_oimc")
                with open(f"data_oimc/{st.session_state.user}.txt", "a") as f:
                    f.write(json.dumps({"fecha": fecha_hoy, "msg": cifrado}) + "\n")
                st.code(cifrado)
                st.success(f"Guardado. Fecha: {fecha_hoy}")
    
    with col2:
        st.subheader("Descifrar")
        msg_c = st.text_input("Mensaje a descifrar")
        if st.button("Descifrar"):
            st.write(f"**Resultado:** {procesar_codex(msg_c, False)}")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.login = False
        st.session_state.modo_admin = False
        st.rerun()
