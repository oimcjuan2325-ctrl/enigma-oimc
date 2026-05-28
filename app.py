import streamlit as st
import datetime

st.set_page_config(page_title="Red O.I.M.C.", page_icon="🔒")

if 'buzon' not in st.session_state: st.session_state.buzon = []

USUARIOS = {
    "Juan": "2313", "Asier": "2021", "Jesús": "1365", "Yolanda": "1460",
    "Mikel": "2013", "Gaizka": "9837", "Iñaki": "7467", "Erika": "7562",
    "Nahia": "9786", "Amets": "1053", "MAQUINA ENIGMA": "2325"
}

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
        else: st.error("Credenciales incorrectas")
else:
    st.title("Red de Inteligencia O.I.M.C.")
    opcion = st.radio("Acción:", ["Cifrar", "Descifrar", "Guardar mensaje cifrado", "Ver mis mensajes"])
    
    if opcion in ["Cifrar", "Descifrar"]:
        fecha_op = st.date_input("Fecha:", datetime.date.today())
        mensaje = st.text_area("Mensaje:")
        if st.button("PROCESAR"):
            st.code(procesar_texto(mensaje, opcion, fecha_op))
            
    elif opcion == "Guardar mensaje cifrado":
        msj_cifrado = st.text_area("Mensaje cifrado:")
        fecha_archivar = st.date_input("Fecha de origen:", datetime.date.today())
        if st.button("ARCHIVAR EN RED"):
            st.session_state.buzon.append({
                "agente": st.session_state.usuario,
                "fecha": fecha_archivar,
                "msj": msj_cifrado
            })
            st.success("Mensaje archivado.")
            
    elif opcion == "Ver mis mensajes":
        mis_mensajes = [m for m in st.session_state.buzon if m['agente'] == st.session_state.usuario]
        for i, item in enumerate(mis_mensajes):
            st.write(f"📅 **{item['fecha']}**")
            st.code(item['msj'])

    # --- PANEL MAQUINA ENIGMA (ADMIN) ---
    if st.session_state.usuario == "MAQUINA ENIGMA":
        st.divider()
        st.warning("⚠️ AUDITORÍA DE RED")
        agente_filtro = st.selectbox("Filtrar por agente:", ["Todos"] + list(USUARIOS.keys()))
        
        for i, item in enumerate(st.session_state.buzon):
            if agente_filtro == "Todos" or item['agente'] == agente_filtro:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**[{item['fecha']}]** {item['agente']}:")
                    st.code(item['msj'])
                with col2:
                    if st.button("Borrar", key=f"del_{i}"):
                        st.session_state.buzon.pop(i)
                        st.rerun()

    if st.button("Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
