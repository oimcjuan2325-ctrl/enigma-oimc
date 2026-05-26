with tabs[5]: # Pestaña de Gestión (Eliminación)
            st.subheader("🧹 Gestión de Archivos (Eliminación)")
            tipo_chat = st.selectbox("Tipo de chat a gestionar:", ["CHAT GRUPAL", "CHAT INDIVIDUAL"])
            db = cargar_db()
            
            mensajes_filtrados = []
            
            if tipo_chat == "CHAT GRUPAL":
                mensajes_filtrados = [m for m in db["mensajes"] if m["a"] == "CHAT GRUPAL"]
            else:
                # Segundo filtro para Chat Individual
                opciones_usuarios = [c for c in CUENTAS_PIN.keys() if c != "MAQUINA ENIGMA"]
                usuario_seleccionado = st.selectbox("Elegir cuenta para gestionar:", opciones_usuarios)
                mensajes_filtrados = [m for m in db["mensajes"] if (m["de"] == usuario_seleccionado or m["a"] == usuario_seleccionado) and m["a"] != "CHAT GRUPAL"]
                
            if not mensajes_filtrados: 
                st.info("No hay mensajes encontrados en este canal.")
            else:
                st.write(f"Mostrando {len(mensajes_filtrados)} mensajes:")
                for m in mensajes_filtrados:
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1: st.code(f"{m['fecha']} | ID:{m['id']} | De:{m['de']} | A:{m['a']} | Msg:{m['msg']}")
                    with c2:
                        if st.button(f"Borrar {m['id']}", key=f"del_{m['id']}_{m['de']}_{m['fecha']}"):
                            db["mensajes"] = [x for x in db["mensajes"] if x != m]
                            guardar_db(db)
                            st.rerun()
