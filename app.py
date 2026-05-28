import streamlit as st
import datetime

st.set_page_config(page_title="Red O.I.M.C.", page_icon="🔒")

# --- ESTADO PERSISTENTE ---
if 'buzon' not in st.session_state: st.session_state.buzon = []

USUARIOS = {
    "Juan": "2313", "Asier": "2021", "Jesús": "1365", "Yolanda": "1460",
    "Mikel": "2013", "Gaizka": "9837", "Iñaki": "7467", "Erika": "7562",
    "Nahia": "9786", "Amets": "1053", "MAQUINA ENIGMA": "2325"
}

# --- LÓGICA DE CIFRADO ---
def calcular_desfase(fecha):
    return (fecha.year * 13 + fecha.month * 31 + fecha.day**2 + fecha.isocalendar()[1] * 7) % 27

def procesar_texto(texto, modo, fecha):
    alfabeto = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
    desfase = calcular_desfase(fecha)
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

# --- INTERFAZ ---
if 'usuario' not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    usuario_input = st.text_input("ID de Usuario:")
    pin = st.text_input("PIN:", type="password")
    if st.button("ACCEDER"):
        if usuario_input in USUARIOS and pin == USUARIOS[usuario_input]:
            st.session_state.usuario = usuario_input
            st.rerun()
else:
    st.title("Red de Inteligencia O.I.M.C.")
    # Selector de modo
    opcion = st.radio("Acción:", ["Cifrar", "Descifrar", "Guardar mensaje cifrado"])
    
    # Fecha selector
    fecha_msg = st.date_input("Fecha del mensaje:", datetime.date.today())
    
    if opcion in ["Cifrar", "Descifrar"]:
        mensaje = st.text_area("Mensaje:")
        if st.button("PROCESAR"):
            resultado = procesar_texto(mensaje, opcion, fecha_msg)
            st.code(resultado)
    
    elif opcion == "Guardar mensaje cifrado":
        msj_cifrado = st.text_area("Introduce el mensaje ya cifrado:")
        if st.button("ARCHIVAR EN RED"):
            st.session_state.buzon.append({
                "agente": st.session_state.usuario,
                "fecha": fecha_msg,
                "msj": msj_cifrado
            })
            st.success("Mensaje archivado correctamente.")

    # --- PANEL MAQUINA ENIGMA ---
    if st.session_state.usuario == "MAQUINA ENIGMA":
        st.divider()
        st.warning("⚠️ AUDITORÍA DE RED")
        for i, item in enumerate(st.session_state.buzon):
            st.write(f"**[{item['fecha']}]** Agente {item['agente']}: `{item['msj']}`")
        if st.button("🚨 BOTÓN DE PÁNICO: BORRAR TODO"):
            st.session_state.buzon = []
            st.rerun()
            
    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
