import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Central Enigma O.I.M.C.", layout="wide")
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

if "usuario" not in st.session_state: st.session_state.usuario = None

if st.session_state.usuario is None:
    st.title("𓁺 Central Enigma O.I.M.C.")
    with st.form("login"):
        u_input = st.text_input("Nombre:")
        p_input = st.text_input("PIN:", type="password")
        if st.form_submit_button("Activar"):
            if u_input in CUENTAS_PIN and CUENTAS_PIN[u_input] == p_input:
                st.session_state.usuario = u_input; st.rerun()
            else: st.error("Acceso denegado")
else:
    u = st.session_state.usuario
    db = cargar_db()
    
    # --- MARCAR COMO LEÍDO AL ENTRAR ---
    cambio = False
    for m in db["mensajes"]:
        if m["a"] == u and not m.get("leido", False):
            m["leido"] = True
            cambio = True
    if cambio: guardar_db(db)
    
    # --- NOTIFICACIONES (solo los NO LEÍDOS) ---
    mensajes_no_leidos = [m for m in db["mensajes"] if m["a"] == u and not m.get("leido", False)]
    count_g = len([m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL" and not m.get("leido", False)])
    count_i = len(mensajes_no_leidos)
    
    st.sidebar.header(f"Operador: {u}")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state.usuario = None; st.rerun()
    
    st.sidebar.markdown("---")
    if count_g > 0: st.sidebar.warning(f"💬 Grupo: {count_g} nuevos")
    if count_i > 0: st.sidebar.error(f"👤 Privados: {count_i} nuevos")
    
    t_g = f"💬 Chat Grupal ({count_g})" if count_g > 0 else "💬 Chat Grupal"
    t_i = f"👤 Chat Individual ({count_i})" if count_i > 0 else "👤 Chat Individual"
    
    tabs = st.tabs(["🔑 Cifrar", "🔓 Descifrar", t_g, t_i] + (["🧹 Gestión"] if u == "MAQUINA ENIGMA" else []))
    
    with tabs[0]:
        t = st.text_area("Texto a cifrar:", height=150)
        if t: st.code(traducir(t, "cifrar"))
    with tabs[1]:
        t = st.text_area("Jeroglífico a descifrar:", height=150)
        if t: st.code(traducir(t, "descifrar"))
            
    with tabs[2]:
        st.subheader("💬 Chat Grupal")
        for m in [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]:
            st.markdown(f"**{m['de']}** ({m['fecha']})")
            st.code(m['msg'])
        msg_g = st.text_area("Mensaje al grupo:", height=100)
        if st.button("Enviar al grupo"):
            db["mensajes"].append({"de": u, "a": "CHAT GRUPAL", "msg": traducir(msg_g, "cifrar"), "fecha": datetime.now().strftime("%d/%m/%Y"), "leido": False})
            guardar_db(db); st.rerun()

    with tabs[3]:
        st.subheader("👤 Chat Individual")
        dest = st.selectbox("Seleccionar persona:", [c for c in CUENTAS_PIN.keys() if c != u])
        for m in [m for m in db["mensajes"] if (m['de'] == u and m['a'] == dest) or (m['de'] == dest and m['a'] == u)]:
            label = "📤 Tú" if m['de'] == u else f"📥 {m['de']}"
            st.markdown(f"**{label}** ({m['fecha']})")
            st.code(m['msg'])
        msg_i = st.text_area(f"Escribir a {dest}:", height=100)
        if st.button("Enviar mensaje privado"):
            db["mensajes"].append({"de": u, "a": dest, "msg": traducir(msg_i, "cifrar"), "fecha": datetime.now().strftime("%d/%m/%Y"), "leido": False})
            guardar_db(db); st.rerun()

    if u == "MAQUINA ENIGMA":
        with tabs[4]:
            st.subheader("🧹 Gestión")
            # (Lógica de auditoría igual que antes)
