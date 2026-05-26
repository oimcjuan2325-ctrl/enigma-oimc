import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Máquina Enigma O.I.M.C.", layout="wide")
DB_FILE = "mensajes.json"

JEROGLIFICOS = {
    "A": "⭡", "B": "𝌇", "C": "亗", "D": "⨂", "E": "⩦", "F": "⎔", "G": "▣", "H": "⫿", 
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
    
    tabs = st.tabs(["🔑 Cifrar", "🔓 Descifrar", "🚀 Enviar", "💬 Chat Grupal", "📥 Recibidos", "🖨️ Imprimir"] + (["🛠️ Admin"] if u == "MAQUINA ENIGMA" else []))
    
    with tabs[0]:
        t = st.text_area("Texto a cifrar:")
        if t: st.code(traducir(t, "cifrar"))
    with tabs[1]:
        t = st.text_area("Jeroglífico a descifrar:")
        if t: st.code(traducir(t, "descifrar"))
    with tabs[2]:
        dest = st.selectbox("Destinatario:", ["CHAT GRUPAL"] + list(CUENTAS_PIN.keys()))
        msg = st.text_input("Mensaje:")
        if st.button("Transmitir"):
            db = cargar_db()
            f = datetime.now().strftime("%d/%m/%Y")
            ids = len([m for m in db["mensajes"] if m["fecha"] == f]) + 1
            db["mensajes"].append({"de": u, "a": dest, "msg": traducir(msg, "cifrar"), "fecha": f, "id": f"{ids:03d}"})
            guardar_db(db)
            st.success(f"Mensaje enviado con ID: {ids:03d}")
    with tabs[3]:
        db = cargar_db()
        m_g = [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]
        if not m_g: st.info("De momento no se ha escrito ningún mensaje.")
        else:
            for m in m_g: st.markdown(f"**{m['de']}** ({m['fecha']} | ID:{m['id']}): `{m['msg']}`")
    with tabs[4]:
        db = cargar_db()
        m_r = [m for m in db["mensajes"] if m["a"] == u]
        if not m_r: st.info("De momento no has recibido ningún mensaje.")
        else:
            for m in m_r: st.markdown(f"**De {m['de']}** ({m['fecha']} | ID:{m['id']}): `{m['msg']}`")
    with tabs[5]:
        st.write("### 🖨️ Estación de Impresión O.I.M.C.")
        t_imp = st.text_area("Introduce tu texto aquí:")
        op = st.radio("Acción:", ["1. Dejar tal cual", "2. Cifrar texto", "3. Descifrar texto"])
        if st.button("Preparar documento"):
            if "2" in op: final = traducir(t_imp, "cifrar")
            elif "3" in op: final = traducir(t_imp, "descifrar")
            else: final = t_imp
            st.code(final)
            st.warning("⚠️ AHORA PARA IMPRIMIR TU MENSAJE TIENES QUE PULSAR CONTROL + P EN TU TECLADO.")
            
    if u == "MAQUINA ENIGMA":
        with tabs[-1]:
            st.subheader("🛠️ Auditoría de Inteligencia")
            sel_u = st.selectbox("Auditar cuenta:", list(CUENTAS_PIN.keys()))
            db = cargar_db()
            c1, c2 = st.columns(2)
            with c1:
                st.write("#### 📤 Enviados")
                for m in [m for m in db["mensajes"] if m["de"] == sel_u]: st.write(f"Para: {m['a']} | `{m['msg']}`")
            with c2:
                st.write("#### 📥 Recibidos")
                for m in [m for m in db["mensajes"] if m["a"] == sel_u]: st.write(f"De: {m['de']} | `{m['msg']}`")
            st.markdown("---")
            st.markdown("### 📜 Abecedario Universal")
            letras = list(JEROGLIFICOS.keys())
            t = "| C | Jeroglífico | | C | Jeroglífico |\n|:---:|:---:|:---:|:---:|:---:|\n"
            for i in range(13):
                t += f"| {letras[i]} | `{JEROGLIFICOS[letras[i]]}` | | {letras[i+13]} | `{JEROGLIFICOS[letras[i+13]]}` |\n"
            st.markdown(t)
