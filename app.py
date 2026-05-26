import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Máquina Enigma O.I.M.C.", layout="wide")
DB_FILE = "mensajes.json"

JEROGLIFICOS = {
    "A": "⭡", "B": "🜇", "C": "亗", "D": "⨂", "E": "⩦", "F": "⎔", "G": "▣", "H": "⫿", 
    "I": "⁜", "J": "⧉", "K": "⋔", "L": "◬", "M": '"亗"', "N": "⚡", "Ñ": "⛩", 
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
    st.sidebar.header(f"Operador: {u}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
    
    tabs = st.tabs(["🔑 Cifrar", "🔓 Descifrar", "💬 Chat Grupal", "👤 Chat Individual"] + (["🛠️ Admin"] if u == "MAQUINA ENIGMA" else []))
    
    # --- CHAT GRUPAL ---
    with tabs[2]:
        st.subheader("💬 Chat Grupal")
        db = cargar_db()
        m_g = [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]
        for m in reversed(m_g): st.write(f"**{m['de']}** ({m['fecha']} | ID:{m['id']}): `{m['msg']}`")
        
        msg_g = st.text_input("Escribir al grupo:", key="input_grupal")
        if st.button("Enviar al grupo"):
            f = datetime.now().strftime("%d/%m/%Y")
            ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
            db["mensajes"].append({"de": u, "a": "CHAT GRUPAL", "msg": traducir(msg_g, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
            guardar_db(db)
            st.rerun()

    # --- CHAT INDIVIDUAL ---
    with tabs[3]:
        st.subheader("👤 Chat Individual")
        dest = st.selectbox("Seleccionar operador:", [c for c in CUENTAS_PIN.keys() if c != u])
        db = cargar_db()
        m_i = [m for m in db["mensajes"] if (m['de'] == u and m['a'] == dest) or (m['de'] == dest and m['a'] == u)]
        for m in reversed(m_i):
            label = "📤 Tú" if m['de'] == u else f"📥 {m['de']}"
            st.write(f"**{label}** ({m['fecha']} | ID:{m['id']}): `{m['msg']}`")
            
        msg_i = st.text_input(f"Escribir a {dest}:", key="input_indiv")
        if st.button(f"Enviar mensaje privado"):
            f = datetime.now().strftime("%d/%m/%Y")
            ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
            db["mensajes"].append({"de": u, "a": dest, "msg": traducir(msg_i, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
            guardar_db(db)
            st.rerun()

    # --- PESTAÑAS RESTANTES ---
    with tabs[0]:
        t = st.text_area("Texto a cifrar:")
        if t: st.code(traducir(t, "cifrar"))
    with tabs[1]:
        t = st.text_area("Jeroglífico a descifrar:")
        if t: st.code(traducir(t, "descifrar"))
            
    if u == "MAQUINA ENIGMA":
        with tabs[-1]:
            st.subheader("🛠️ Auditoría de Inteligencia")
            sel_u = st.selectbox("Auditar cuenta:", list(CUENTAS_PIN.keys()))
            db = cargar_db()
            for m in [m for m in db["mensajes"] if m["de"] == sel_u or m["a"] == sel_u]:
                st.write(f"({m['fecha']}) De: {m['de']} | A: {m['a']} | `{m['msg']}`")
