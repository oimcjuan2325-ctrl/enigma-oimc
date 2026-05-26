import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Máquina Enigma O.I.M.C.", layout="wide")
DB_FILE = "mensajes.json"

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
    st.sidebar.header(f"Operador: {u}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.usuario = None
        st.rerun()
    
    lista_tabs = ["🔑 Cifrar", "🔓 Descifrar", "💬 Chat Grupal", "👤 Chat Individual"]
    if u == "MAQUINA ENIGMA":
        lista_tabs.append("🧹 Gestión y Auditoría")
    
    tabs = st.tabs(lista_tabs)
    
    # Mantenemos las áreas de texto multilínea para los párrafos
    with tabs[0]:
        t = st.text_area("Texto a cifrar:", height=150)
        if t: st.markdown(f"**Resultado:**\n\n{traducir(t, 'cifrar')}")
            
    with tabs[1]:
        t = st.text_area("Jeroglífico a descifrar:", height=150)
        if t: st.markdown(f"**Resultado:**\n\n{traducir(t, 'descifrar')}")
            
    with tabs[2]:
        st.subheader("💬 Chat Grupal")
        db = cargar_db()
        m_g = [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]
        for m in m_g: 
            st.markdown(f"**{m['de']}** ({m['fecha']} | ID:{m['id']}):")
            st.markdown(f"```\n{m['msg']}\n```") # Usamos bloque de código visual pero respetando saltos
        st.divider()
        msg_g = st.text_area("Escribir al grupo:", key="input_grupal", height=100)
        if st.button("Enviar al grupo"):
            if msg_g:
                f = datetime.now().strftime("%d/%m/%Y")
                ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
                db["mensajes"].append({"de": u, "a": "CHAT GRUPAL", "msg": traducir(msg_g, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
                guardar_db(db); st.rerun()

    with tabs[3]:
        st.subheader("👤 Chat Individual")
        dest = st.selectbox("Seleccionar operador:", [c for c in CUENTAS_PIN.keys() if c != u])
        db = cargar_db()
        m_i = [m for m in db["mensajes"] if (m['de'] == u and m['a'] == dest) or (m['de'] == dest and m['a'] == u)]
        for m in m_i:
            label = "📤 Tú" if m['de'] == u else f"📥 {m['de']}"
            st.markdown(f"**{label}** ({m['fecha']} | ID:{m['id']}):")
            st.markdown(f"```\n{m['msg']}\n```")
        st.divider()
        msg_i = st.text_area(f"Escribir a {dest}:", key="input_indiv", height=100)
        if st.button(f"Enviar mensaje privado"):
            if msg_i:
                f = datetime.now().strftime("%d/%m/%Y")
                ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
                db["mensajes"].append({"de": u, "a": dest, "msg": traducir(msg_i, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
                guardar_db(db); st.rerun()
            
    if u == "MAQUINA ENIGMA":
        with tabs[4]:
            st.subheader("🧹 Gestión y Auditoría")
            # ... (Lógica de gestión igual que antes) ...
            db = cargar_db()
            # Mostrando mensajes de forma multilínea
            for m in db["mensajes"]:
                col1, col2 = st.columns([0.8, 0.2])
                with col1:
                    st.markdown(f"**{m['fecha']} | ID:{m['id']} | De:{m['de']} | A:{m['a']}**")
                    st.markdown(f"```\n{m['msg']}\n```")
                with col2:
                    if st.button(f"Borrar {m['id']}", key=f"del_{m['id']}_{m['de']}_{m['fecha']}"):
                        db["mensajes"] = [x for x in db["mensajes"] if x != m]
                        guardar_db(db); st.rerun()
