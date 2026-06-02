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

# --- 2. MOTOR DEL CODEX CELTA 2.0 ---
def calcular_desplazamiento(fecha):
    # Número base derivado de tu esquema
    numero_base = 345324535554563 
    
    # Filtrado dinámico por mes
    mes_str = str(fecha.month)
    numero_filtrado = str(numero_base)
    for digito in mes_str:
        numero_filtrado = numero_filtrado.replace(digito, "")
    
    val = int(numero_filtrado)
    cociente = val // 2
    sobra = val % 2
    
    # Ajuste: Sobra * últimos DOS dígitos del cociente
    ultimos_dos = int(str(cociente)[-2:])
    ajuste = sobra * ultimos_dos
    
    # Fórmula Final: (Mes + Día + Ajuste) / 2
    desplazamiento = (fecha.month + fecha.day + ajuste) // 2
    return desplazamiento

def motor_codex(texto, es_cifrado, fecha):
    desfase = calcular_desplazamiento(fecha)
    if not es_cifrado: desfase = -desfase
    
    resultado = ""
    for c in texto.upper():
        if c.isalpha():
            resultado += chr(((ord(c) - 65 + desfase) % 26) + 65)
        else:
            resultado += c
    return resultado

# --- 3. INTERFAZ ---
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
    st.sidebar.title(f"Operativo: {st.session_state.user}")
    seccion = st.sidebar.radio("Navegación", ["Cifrar", "Descifrar", "Mis Archivos Cifrados"])
    
    # PANEL MAQUINA ENIGMA
    if st.session_state.user == "MAQUINA_ENIGMA":
        if st.sidebar.button("⚙️ Administración Central"): st.session_state.admin = True
    
    if seccion == "Cifrar":
        st.subheader("Cifrar Mensaje")
        msg = st.text_area("Mensaje a cifrar")
        if st.button("Cifrar"):
            st.session_state.temp = motor_codex(msg, True, datetime.date.today())
            st.code(st.session_state.temp)
            
    elif seccion == "Descifrar":
        st.subheader("Descifrar Mensaje")
        msg_c = st.text_input("Mensaje cifrado")
        fecha_c = st.date_input("Fecha de cuando se cifró")
        if st.button("Descifrar"):
            st.write(f"**Resultado:** {motor_codex(msg_c, False, fecha_c)}")

    elif seccion == "Mis Archivos Cifrados":
        st.subheader("📁 Mis Archivos Cifrados")
        with st.expander("Guardar nuevo mensaje cifrado"):
            m_c = st.text_input("Pega el mensaje cifrado aquí")
            f_c = st.date_input("Fecha de cuando se cifró")
            if st.button("Guardar en Mis Archivos"):
                if not os.path.exists("data_oimc"): os.makedirs("data_oimc")
                with open(f"data_oimc/{st.session_state.user}.txt", "a") as f:
                    f.write(json.dumps({"fecha": f_c.strftime("%d/%m/%Y"), "msg": m_c}) + "\n")
                st.success("Mensaje guardado correctamente.")
        
        st.write("---")
        st.subheader("Ver mis mensajes")
        ruta = f"data_oimc/{st.session_state.user}.txt"
        if os.path.exists(ruta):
            with open(ruta, "r") as f:
                for l in f:
                    data = json.loads(l)
                    st.write(f"📅 **{data['fecha']}**: `{data['msg']}`")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
