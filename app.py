import streamlit as st
import datetime
from streamlit_localstorage import StLocalStorage

# Configuración
st.set_page_config(page_title="Gestor de Tareas Académicas", page_icon="🔒")
storage = StLocalStorage()

# --- LÓGICA DE CIFRADO (MISMA PARA TODOS) ---
def calcular_desfase():
    fecha = datetime.date.today()
    desfase = (fecha.year * 13) + (fecha.month * 31) + (fecha.day**2) + (fecha.isocalendar()[1] * 7)
    return desfase % 27

def cifrar(texto):
    alfabeto = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    desfase = calcular_desfase()
    texto = texto.upper()[::-1]
    resultado = ""
    for char in texto:
        if char in alfabeto:
            idx = (alfabeto.index(char) + desfase) % 27
            resultado += alfabeto[idx]
        else:
            resultado += char
    return resultado

# --- CONTROL DE ACCESO ---
st.title("Sistema de Gestión Académica")

if 'usuario' not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    usuario_input = st.text_input("ID de Usuario:")
    pin = st.text_input("PIN:", type="password")
    if st.button("ACCEDER"):
        # Definición de cuentas
        if usuario_input == "MAQUINA ENIGMA" and pin == "ADMIN123":
            st.session_state.usuario = "MAQUINA ENIGMA"
            st.rerun()
        elif usuario_input == "AGENTE" and pin == "1234":
            st.session_state.usuario = "AGENTE"
            st.rerun()
        else:
            st.error("Credenciales incorrectas")
else:
    st.write(f"Conectado como: **{st.session_state.usuario}**")
    
    # --- FUNCIONES DE LA WEB ---
    mensaje = st.text_area("Introduce mensaje:")
    if st.button("PROCESAR"):
        st.code(cifrar(mensaje))
    
    st.divider()
    
    # --- PRIVILEGIOS DE ADMINISTRADOR ---
    if st.session_state.usuario == "MAQUINA ENIGMA":
        st.warning("PANEL DE ADMINISTRACIÓN")
        if st.button("🚨 BOTÓN DE PÁNICO (BORRAR TODA LA RED)"):
            storage.clear()
            st.session_state.clear()
            st.rerun()
    
    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
