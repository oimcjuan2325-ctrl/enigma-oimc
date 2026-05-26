if u == "MAQUINA ENIGMA":
        with tabs[4]:
            st.subheader("🧹 Gestión y Auditoría de Inteligencia")
            db = cargar_db()
            
            # 1. Elegir tipo de auditoría
            tipo_gestion = st.radio("¿Qué deseas gestionar?", ["Chat Grupal", "Chat Individual"])
            
            if tipo_gestion == "Chat Grupal":
                st.subheader("Auditoría: Chat Grupal")
                mensajes_g = [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]
                for m in mensajes_g:
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1: st.code(f"{m['fecha']} | De:{m['de']} | {m['msg']}")
                    with col2:
                        if st.button("Borrar", key=f"del_g_{m['fecha']}_{m['de']}"):
                            db["mensajes"].remove(m)
                            guardar_db(db); st.rerun()
            
            else:
                st.subheader("Auditoría: Chat Individual")
                # Listar personas con las que se ha chateado (todos los usuarios menos Enigma)
                usuarios_activos = [c for c in CUENTAS_PIN.keys() if c != "MAQUINA ENIGMA"]
                persona_sel = st.selectbox("Elige cuenta para gestionar:", usuarios_activos)
                
                # Buscar con quién ha chateado esa persona
                st.write(f"Revisando historial de: **{persona_sel}**")
                mensajes_p = [m for m in db["mensajes"] if (m['de'] == persona_sel or m['a'] == persona_sel) and m['a'] != "CHAT GRUPAL"]
                
                if not mensajes_p:
                    st.info("No hay historial individual para este usuario.")
                else:
                    for m in mensajes_p:
                        col1, col2 = st.columns([0.8, 0.2])
                        with col1: st.code(f"{m['fecha']} | De:{m['de']} | A:{m['a']} | Msg:{m['msg']}")
                        with col2:
                            if st.button("Borrar", key=f"del_p_{m['fecha']}_{m['de']}_{m['a']}"):
                                db["mensajes"].remove(m)
                                guardar_db(db); st.rerun()
