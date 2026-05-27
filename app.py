import streamlit as st
import datetime

# ==========================================
#       MOTOR DE CIFRADO "ENIGMA" O.I.M.C.
# ==========================================
# Abecedario Maestro (27 caracteres)
ABECEDARIO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

def obtener_desplazamiento_enigma():
    """
    Simula el giro del rotor Enigma basándose en la fecha actual.
    El cálculo cambia automáticamente cada día.
    Clave Diaria = (Día * Mes) + Año_Corto
    """
    hoy = datetime.date.today()
    clave_maestra = (hoy.day * hoy.month) + (hoy.year % 100)
    
    # El desplazamiento se ajusta al tamaño del abecedario
    return clave_maestra % len(ABECEDARIO)

def motor_enigma(texto, modo='cifrar'):
    """
    Aplica la rotación Enigma a cada letra.
    """
    n = len(ABECEDARIO)
    desplazamiento = obtener_desplazamiento_enigma()
    
    # Si desciframos, invertimos el giro
    if modo == 'descifrar':
        desplazamiento = -desplazamiento
        
    resultado = ""
    for char in texto.upper():
        if char in ABECEDARIO:
            # Encuentra la letra, calcula la nueva posición y la devuelve
            indice_actual = ABECEDARIO.index(char)
            nuevo_indice = (indice_actual + desplazamiento) % n
            resultado += ABECEDARIO[nuevo_indice]
        else:
            # Mantiene espacios y números intactos
            resultado += char
    return resultado

# ==========================================
#       INTERFAZ STREAMLIT O.I.M.C.
# ==========================================
# Configuración de la página
st.set_page_config(page_title="O.I.M.C. Enigma", page_icon="🔐", layout="wide")

st.title("CENTRO DE MANDO O.I.M.C.")
st.write("---")

# Barra lateral para el control de usuario y equipo
st.sidebar.header("IDENTIFICACIÓN")
usuario_activo = st.sidebar.selectbox("Miembro", ["JUAN (LÍDER)", "GAIZKA", "IÑAKI", "MIKEL"])
st.sidebar.divider()
st.sidebar.subheader("Información de Misión")
st.sidebar.info(f"Fecha Activa: {datetime.date.today()}")
st.sidebar.success(f"Rotor Enigma hoy: **{obtener_desplazamiento_enigma()}** posiciones")

# --- ZONA 1: CHAT DE OPERACIONES ---
st.header("1. Chat de Operaciones (Grupal/Individual)")

if 'historial' not in st.session_state:
    st.session_state.historial = []

with st.container():
    c1, c2 = st.columns([1, 4])
    with c1:
        destinatario = st.selectbox("PARA:", ["OIMC_GRUPO", "GAIZKA", "IÑAKI", "MIKEL"])
    with c2:
        msg_input = st.text_input("Mensaje a enviar:")

    if st.button("Enviar Cifrado", use_container_width=True):
        if msg_input:
            msg_cifrado = motor_enigma(msg_input, 'cifrar')
            paquete = f"DE:{usuario_activo} | PARA:{destinatario} | MSG:{msg_cifrado}"
            st.session_state.historial.append(paquete)
            st.toast("Mensaje enviado y cifrado en el historial grupal.")

    st.subheader("Bandeja de Entrada Grupal (Cifrada)")
    with st.expander("Ver mensajes recientes del equipo (Solo OIMC)", expanded=True):
        if not st.session_state.historial:
            st.write("*No hay mensajes registrados hoy.*")
        for m in st.session_state.historial[-10:]: # Muestra los últimos 10
            st.text(m)

# --- ZONA 2: DECODIFICACIÓN ---
st.write("---")
st.header("2. Herramienta de Decodificación")

with st.container():
    paquete_recibido = st.text_input("Pega aquí el mensaje cifrado recibido:")
    if st.button("Descifrar con Enigma", use_container_width=True):
        if paquete_recibido:
            # Intenta desglosar el paquete si tiene el formato "DE:X | PARA:Y | MSG:Z"
            if "| MSG:" in paquete_recibido:
                partes = paquete_recibido.split("|")
                emisor = partes[0].split(":")[1]
                msg_cifrado = partes[2].split(":")[1].strip()
                result = motor_enigma(msg_cifrado, 'descifrar')
                st.success(f"MENSAJE DESCIFRADO (De: {emisor}):\n**{result}**")
            else:
                # Si es texto suelto, lo descifra directamente
                result = motor_enigma(paquete_recibido, 'descifrar')
                st.success(f"RESULTADO DESCIFRADO:\n**{result}**")
