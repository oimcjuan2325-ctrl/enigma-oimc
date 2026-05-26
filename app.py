import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Máquina Enigma O.I.M.C.", layout="wide")
DB_FILE = "mensajes.json"

# --- JS PARA BOTÓN COPIAR ---
st.markdown("""
<script>
function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
}
</script>
""", unsafe_allow_html=True)

JEROGLIFICOS = {
    "A": "⭡", "B": "🜇", "C": "亗", "D": "⨂", "E": "⩦", "F": "⎔", "G": "▣", "H": "⫿", 
    "I": "⁜", "J": "⧉", "K": "⋔", "L": "◬", "M": "🜂", "N": "⚡", "Ñ": "⛩", 
    "O": "☉", "P": "⭧", "Q": "⿿", "R": "♾", "S": "🜔", "T": "⏃", "U": "⊔", 
    "V": "⪧", "W": "⎿", "X": "⧖", "Y": "↟", "Z": "⟐"
}

CUENTAS_PIN = {
    "MAQUINA ENIGMA": "2325", "Juan": "2313", "Asier": "2021", "Jesús": "1365", 
    "Yolanda": "1460", "Mikel": "2013", "Gaizka": "9837", "Iñaki": "7467", 
    "Erika": "7562", "Nahia": "9786", "Amets": "1053"
}

# --- FUNCIONES ---
def cargar_db():
    if not os.path.exists(DB_FILE): return {"mensajes": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if "mensajes" in data else {"mensajes": []}
    except: return {"mensajes": []}

def guardar_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False)

def traducir(texto, tipo="cifrar"):
    if tipo == "cifrar": return "".join([JEROGLIFICOS.get(l, l) for l in texto.upper()])
    res = texto.upper()
    for l, s in JEROGLIFICOS.items(): res = res.replace(s, l)
    return res

# --- LÓGICA DE APP ---
if "usuario" not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("𓁺 Central Enigma O.I.M.C.")
    with st.form("login"):
        u = st.text_input("Nombre:")
        p = st.text_input("PIN:", type="password")
        if st.form_submit_button("Activar"):
            if u in CUENTAS_PIN and CUENTAS_PIN[u] == p:
                st.session_state.usuario = u
                st.rerun()
            else: st.error("Acceso denegado")
else:
    u = st.session_state.usuario
    tabs = st.tabs(["🔑 Cifrar", "🔓 Descifrar", "💬 Chat Grupal", "👤 Chat Individual"] + (["🧹 Gestión"] if u == "MAQUINA ENIGMA" else []))
    
    with tabs[0]:
        t = st.text_area("Texto a cifrar:", height=150, max_chars=500)
        if t:
            cifrado = traducir(t, "cifrar")
            st.code(cifrado)
            if st.button("📋 Copiar Cifrado"):
                st.write(f'<script>copyToClipboard("{cifrado}");</script>', unsafe_allow_html=True)
                st.success("¡Cifrado copiado al portapapeles!")

    with tabs[1]:
        t = st.text_area("Pega aquí el jeroglífico:", height=150, max_chars=500)
        if t: st.write(traducir(t, "descifrar"))

    # Para los chats, ahora el botón de copiar aparecerá junto al mensaje
    def mostrar_mensajes(mensajes):
        for m in mensajes:
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"**{m['de']}** ({m['fecha']}):")
                st.markdown(f"> {m['msg']}")
            with col2:
                if st.button("📋", key=f"btn_{m['id']}_{m['fecha']}"):
                    st.write(f'<script>copyToClipboard("{m["msg"]}");</script>', unsafe_allow_html=True)
                    st.toast("Copiado!")

    with tabs[2]:
        st.subheader("💬 Chat Grupal")
        db = cargar_db()
        mostrar_mensajes([m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"])
        
        msg_g = st.text_area("Escribir mensaje:", key="input_grupal", height=100)
        if st.button("Enviar al grupo"):
            f = datetime.now().strftime("%d/%m/%Y")
            ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
            db["mensajes"].append({"de": u, "a": "CHAT GRUPAL", "msg": traducir(msg_g, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
            guardar_db(db); st.rerun()
