import streamlit as st
import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Académica", page_icon="🔒")

# Diccionario de usuarios y sus PINs
USUARIOS = {
    "Juan": "2313",
    "Asier": "2021",
    "Jesús": "1365",
    "Yolanda": "1460",
    "Mikel": "2013",
    "Gaizka": "9837",
    "Iñaki": "7467",
    "Erika": "7562",
    "Nahia": "9786",
    "Amets": "1053",
    "MAQUINA ENIGMA": "2325"
}

# --- LÓGICA DE CIFRADO ---
def calcular_desfase():
    fecha = datetime.date.today()
    return (fecha.year * 13 + fecha.month * 31 + fecha.day**2 + fecha.isocalendar()[1] * 7) % 27

def procesar_texto(texto, modo):
    alfabeto = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    desfase = calcular_desfase()
    if modo == "Descifrar": desfase = -desfase
    
    texto = texto.upper()
    if modo == "Cifrar": texto = texto[::-1]
        
    resultado = ""
    for char in texto:
        if char in alfabeto:
            idx = (alfabeto.index(char) + desfase) % 27
            resultado += alfabeto[idx]
        else:
            resultado += char
    return resultado if modo == "Cifrar" else resultado[::-1]

# --- SISTEMA DE LOGIN ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("Acceso al Sistema")
    usuario_input = st.text_input("ID de Usuario:")
    pin = st.text_input("PIN:", type="password")
    
    if st.button("ACCEDER"):
        if usuario_input in USUARIOS and pin == USUARIOS[usuario_input]:
            st.session_state.usuario = usuario_input
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    st.title("Sistema de Gestión Académica")
    st.write(f"Conectado como: **{st.session_state.usuario}**")
    
    modo = st.radio("Acción:", ["Cifrar", "Descifrar"])
    mensaje = st.text_area("Mensaje:")
    
    if st.button("EJECUTAR"):
        st.code(procesar_texto(mensaje, modo))
    
    # --- PRIVILEGIOS DE ADMINISTRADOR ---
    if st.session_state.usuario == "MAQUINA ENIGMA":
        st.divider()
        st.warning("PANEL DE ADMINISTRACIÓN")
        if st.button("🚨 BOTÓN DE PÁNICO: REINICIAR RED"):
            st.session_state.clear()
            st.rerun()
            
    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
