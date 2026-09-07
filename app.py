import os, math, base64, string, secrets, sqlite3
from flask import Flask, session, request, redirect, url_for, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

# ================= BASE DE DATOS =================
DB = "boveda.db"

def init_db():
    con = sqlite3.connect(DB)
    c = con.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        hash TEXT NOT NULL,
        clave_cifrado TEXT NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS entradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        sitio TEXT NOT NULL,
        usuario_sitio TEXT NOT NULL,
        contrasena_cifrada TEXT NOT NULL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id))""")
    con.commit()
    con.close()

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

# ================= CIFRADO =================
def cifrar(clave_cifrado_b64, texto):
    return Fernet(clave_cifrado_b64.encode()).encrypt(texto.encode()).decode()

def descifrar(clave_cifrado_b64, token):
    return Fernet(clave_cifrado_b64.encode()).decrypt(token.encode()).decode()

# ================= GENERADOR DE CONTRASEÑAS =================
def generar(largo=16, mayus=True, num=True, simbolos=True):
    letras = string.ascii_lowercase
    if mayus: letras += string.ascii_uppercase
    if num: letras += string.digits
    if simbolos: letras += "!@#$%&*+-_?"
    return "".join(secrets.choice(letras) for _ in range(max(4, largo)))

def fuerza(contra):
    puntos = 0
    if len(contra) >= 8: puntos += 1
    if len(contra) >= 14: puntos += 1
    if any(c.islower() for c in contra) and any(c.isupper() for c in contra): puntos += 1
    if any(c.isdigit() for c in contra): puntos += 1
    if any(c in "!@#$%&*+-_?" for c in contra): puntos += 1
    return ["Muy débil", "Débil", "Aceptable", "Buena", "Fuerte", "Muy fuerte"][puntos]

# ================= PRUEBAS DE CONTRASEÑAS =================
COMUNES = {
    "123456", "password", "123456789", "12345678", "12345", "qwerty",
    "111111", "1234567", "dragon", "123123", "abc123", "iloveyou",
    "admin", "welcome", "monkey", "login", "princess", "qwerty123",
    "solosolo", "contrasena", "password1", "000000", "1234", "1234567890",
    "usuario", "hola123", "admin123", "root", "toor", "654321",
}

def analisis_completo(contra):
    resultado = {"advertencias": [], "positivos": []}

    # 1. ¿Está en la lista de contraseñas más usadas?
    if contra.lower() in COMUNES:
        resultado["advertencias"].append(
            "🚨 Está entre las contraseñas MÁS USADAS del mundo. Se descifra al instante.")

    # 2. Patrones y secuencias
    minus = sum(1 for c in contra if c.islower())
    mayus = sum(1 for c in contra if c.isupper())
    digs = sum(1 for c in contra if c.isdigit())
    sims = len(contra) - minus - mayus - digs

    if digs == len(contra) and contra:
        resultado["advertencias"].append("🔢 Solo tiene números: muy fácil de descifrar.")
    if minus == len(contra) and contra:
        resultado["advertencias"].append("🔡 Solo tiene minúsculas: añade mayúsculas, números y símbolos.")
    if contra.lower().startswith(("1234", "abc", "qwe", "0000")):
        resultado["advertencias"].append("📏 Empieza con una secuencia obvia (1234, abc, qwerty...).")
    if "qwerty" in contra.lower():
        resultado["advertencias"].append("⌨️ Contiene 'qwerty': patrón de teclado, muy predecible.")
    if contra.isdigit() and len(contra) in (4, 6, 8):
        resultado["advertencias"].append("📅 Parece un PIN o una fecha (año, DNI...).")

    # 3. Entropía = log2(tamaño_del_alfabeto^longitud)
    alfabeto = 0
    if minus: alfabeto += 26
    if mayus: alfabeto += 26
    if digs: alfabeto += 10
    if sims: alfabeto += 33
    entropia = len(contra) * math.log2(alfabeto) if alfabeto else 0
    resultado["entropia"] = round(entropia, 1)

    # 4. Tiempo de descifrado (10 mil millones de intentos/segundo)
    intentos = 2 ** entropia
    segundos = intentos / 2 / 10_000_000_000
    resultado["tiempo"] = tiempo_legible(segundos)

    # 5. Puntos positivos
    if len(contra) >= 16:
        resultado["positivos"].append("✅ Tiene 16 caracteres o más: excelente longitud.")
    if mayus and minus:
        resultado["positivos"].append("✅ Mezcla mayúsculas y minúsculas.")
    if sims:
        resultado["positivos"].append("✅ Contiene símbolos especiales.")
    if not resultado["advertencias"] and entropia > 60:
        resultado["positivos"].append("🛡️ Sin patrones conocidos y alta entropía. ¡Gran contraseña!")
    return resultado

def tiempo_legible(seg):
    if seg < 1: return "¡Menos de 1 segundo! 😱"
    unidades = [(31536000*100, "siglos"), (31536000, "años"),
                (2592000, "meses"), (86400, "días"),
                (3600, "horas"), (60, "minutos")]
    for s, nombre in unidades:
        if seg >= s:
            valor = seg / s
            return f"~{valor:.0f} {nombre}" if valor >= 10 else f"~{valor:.1f} {nombre}"
    return f"~{seg:.0f} segundos"

# ================= PLANTILLAS =================
ESTILO = """
<style>
  * { box-sizing:border-box; }
  body { font-family:'Segoe UI',Arial; background:#0f0f1a; color:#fff;
         text-align:center; padding:30px; margin:0; }
  .caja { background:#1c1c2e; padding:30px; border-radius:16px;
          max-width:600px; margin:auto; box-shadow:0 0 30px rgba(124,92,255,.2); }
  h1 { color:#a78bfa; }
  input, select { width:100%; padding:11px; margin:6px 0; border-radius:8px;
                  border:1px solid #333; background:#12121f; color:#fff; }
  button { background:#7c5cff; color:#fff; border:none; padding:12px 22px;
           border-radius:8px; font-size:15px; cursor:pointer; margin:4px; }
  button:hover { background:#9b7dff; }
  .rojo { background:#e5484d; padding:6px 12px; font-size:13px; }
  .rojo:hover { background:#ff6369; }
  table { width:100%; border-collapse:collapse; margin-top:15px; }
  th, td { padding:10px; border-bottom:1px solid #2d2d44; text-align:left;
           word-break:break-all; }
  th { color:#a78bfa; }
  .resultado { background:#1a1a2e; padding:15px; border-radius:10px;
               margin-top:15px; text-align:left; }
  .medidor { height:8px; background:#2d2d44; border-radius:4px;
             margin-top:8px; overflow:hidden; }
  .medidor div { height:100%; background:#7c5cff; width:0; transition:.3s; }
  a { color:#7c5cff; }
  .mono { font-family:monospace; color:#7ce7a2; }
</style>
<script>
  function medirFuerza() {
    const c = document.getElementById("contra").value;
    let p = 0;
    if (c.length >= 8) p++; if (c.length >= 14) p++;
    if (/[a-z]/.test(c) && /[A-Z]/.test(c)) p++;
    if (/[0-9]/.test(c)) p++; if (/[^a-zA-Z0-9]/.test(c)) p++;
    document.getElementById("barra").style.width = (p*20) + "%";
    document.getElementById("texto").innerText =
      ["Muy débil","Débil","Aceptable","Buena","Fuerte","Muy fuerte"][p];
  }
  async function generar() {
    const r = await fetch("/generar?largo=" + largo.value +
      "&mayus=" + mayus.checked + "&num=" + num.checked + "&sim=" + sim.checked);
    const t = await r.text();
    contra.value = t; medirFuerza();
  }
</script>
"""

LOGIN = """<!DOCTYPE html><html><head><title>Bóveda</title>%s</head>
<body><div class="caja">
  <h1>🔐 Bóveda de Contraseñas</h1>
  <p>Tus contraseñas, cifradas y seguras</p>
  <form method="post">
    <input name="usuario" placeholder="Usuario" required><br>
    <input name="contrasena" type="password" placeholder="Contraseña" required><br>
    <button type="submit" name="modo" value="login">Entrar</button>
    <button type="submit" name="modo" value="registro">Crear cuenta</button>
  </form>
  {% if error %}<p style="color:#ff6b6b">{{ error }}</p>{% endif %}
</div></body></html>""" % ESTILO

INICIO = """<!DOCTYPE html><html><head><title>Mi Bóveda</title>%s</head>
<body><div class="caja">
  <h1>🗝️ Mi Bóveda</h1>
  <p>Hola <b>{{ usuario }}</b> ·
     <a href="/pruebas">🧪 Pruebas de contraseñas</a> ·
     <a href="/salir">Cerrar sesión</a></p>

  <h3>➕ Añadir contraseña</h3>
  <form method="post">
    <input name="sitio" placeholder="Sitio web (ej: Gmail)" required>
    <input name="usuario_sitio" placeholder="Tu usuario o email" required>
    <input name="contrasena" id="contra" placeholder="Contraseña"
           oninput="medirFuerza()" required>
    <div class="medidor"><div id="barra"></div></div>
    <p id="texto" style="font-size:13px;color:#a78bfa"></p>
    <label><input type="checkbox" id="mayus" checked> Mayúsculas</label>
    <label><input type="checkbox" id="num" checked> Números</label>
    <label><input type="checkbox" id="sim" checked> Símbolos</label><br>
    Largo: <input type="number" id="largo" value="16" min="4" max="64"
                  style="width:70px">
    <button type="button" onclick="generar()">🎲 Generar</button><br>
    <button type="submit">💾 Guardar en la bóveda</button>
  </form>

  {% if error %}<p style="color:#ff6b6b">{{ error }}</p>{% endif %}

  <h3>📋 Contraseñas guardadas ({{ entradas|length }})</h3>
  <table>
    <tr><th>Sitio</th><th>Usuario</th><th>Contraseña</th><th></th></tr>
    {% for e in entradas %}
    <tr>
      <td><b>{{ e.sitio }}</b></td>
      <td>{{ e.usuario_sitio }}</td>
      <td class="mono">{{ e.contrasena }}</td>
      <td><form method="post" action="/borrar">
        <input type="hidden" name="id" value="{{ e.id }}">
        <button class="rojo">🗑️</button></form></td>
    </tr>
    {% endfor %}
  </table>
  {% if not entradas %}<p>Aún no tienes contraseñas guardadas.</p>{% endif %}
</div></body></html>""" % ESTILO

PRUEBAS = """<!DOCTYPE html><html><head><title>Pruebas de contraseñas</title>%s</head>
<body><div class="caja">
  <h1>🧪 Pruebas de Contraseñas</h1>
  <p>Pon a prueba una contraseña como lo haría un hacker</p>
  <p><a href="/inicio">← Volver a mi bóveda</a></p>

  <form method="post">
    <input name="contrasena" id="contra" placeholder="Escribe la contraseña a probar" required>
    <button type="submit">⚡ Analizar</button>
  </form>

  {% if r %}
    <div class="resultado">
      <h3>📊 Entropía: {{ r.entropia }} bits</h3>
      <p><b>⏱️ Tiempo estimado de descifrado</b> (fuerza bruta, 10 mil millones de intentos/segundo):<br>
      <span style="font-size:22px;color:{% if r.entropia > 70 %}#7ce7a2{% elif r.entropia > 45 %}#ffd166{% else %}#ff6b6b{% endif %}">{{ r.tiempo }}</span></p>
    </div>

    {% if r.advertencias %}
    <div class="resultado" style="border-left:4px solid #ff6b6b">
      <b>⚠️ Problemas detectados:</b><br>
      {% for a in r.advertencias %}{{ a }}<br>{% endfor %}
    </div>
    {% endif %}

    {% if r.positivos %}
    <div class="resultado" style="border-left:4px solid #7ce7a2">
      <b>👍 Puntos fuertes:</b><br>
      {% for p in r.positivos %}{{ p }}<br>{% endfor %}
    </div>
    {% endif %}
  {% endif %}
</div></body></html>""" % ESTILO

# ================= RUTAS =================
@app.route("/generar")
def ruta_generar():
    return generar(int(request.args.get("largo", 16)),
                   request.args.get("mayus") == "true",
                   request.args.get("num") == "true",
                   request.args.get("sim") == "true")

@app.route("/", methods=["GET", "POST"])
def login():
    if "uid" in session:
        return redirect(url_for("inicio"))
    error = None
    if request.method == "POST":
        u, c = request.form["usuario"].strip(), request.form["contrasena"]
        con = db()
        fila = con.execute("SELECT * FROM usuarios WHERE usuario=?", (u,)).fetchone()
        if request.form["modo"] == "registro":
            if fila:
                error = "Ese usuario ya existe"
            elif len(c) < 4:
                error = "La contraseña debe tener al menos 4 caracteres"
            else:
                clave = base64.urlsafe_b64encode(os.urandom(32)).decode()
                con.execute("INSERT INTO usuarios (usuario, hash, clave_cifrado) VALUES (?,?,?)",
                            (u, generate_password_hash(c), clave))
                con.commit()
                session["uid"] = con.execute("SELECT id FROM usuarios WHERE usuario=?", (u,)).fetchone()[0]
                session["usuario"] = u
                session["clave"] = clave
                con.close()
                return redirect(url_for("inicio"))
        else:
            if fila and check_password_hash(fila["hash"], c):
                session["uid"] = fila["id"]
                session["usuario"] = u
                session["clave"] = fila["clave_cifrado"]
                con.close()
                return redirect(url_for("inicio"))
            error = "Usuario o contraseña incorrectos"
        con.close()
    return render_template_string(LOGIN, error=error)

@app.route("/inicio", methods=["GET", "POST"])
def inicio():
    if "uid" not in session:
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        sitio = request.form["sitio"].strip()
        contra = request.form["contrasena"]
        if not sitio or not contra:
            error = "Rellena todos los campos"
        else:
            con = db()
            con.execute("INSERT INTO entradas (usuario_id, sitio, usuario_sitio, contrasena_cifrada) VALUES (?,?,?,?)",
                        (session["uid"], sitio, request.form["usuario_sitio"].strip(),
                         cifrar(session["clave"], contra)))
            con.commit()
            con.close()
    con = db()
    filas = con.execute("SELECT * FROM entradas WHERE usuario_id=?", (session["uid"],)).fetchall()
    con.close()
    entradas = [{"id": f["id"], "sitio": f["sitio"], "usuario_sitio": f["usuario_sitio"],
                 "contrasena": descifrar(session["clave"], f["contrasena_cifrada"])}
                for f in filas]
    return render_template_string(INICIO, usuario=session["usuario"],
                                  entradas=entradas, error=error)

@app.route("/pruebas", methods=["GET", "POST"])
def pruebas():
    if "uid" not in session:
        return redirect(url_for("login"))
    r = None
    if request.method == "POST":
        r = analisis_completo(request.form["contrasena"])
    return render_template_string(PRUEBAS, r=r)

@app.route("/borrar", methods=["POST"])
def borrar():
    if "uid" not in session:
        return redirect(url_for("login"))
    con = db()
    con.execute("DELETE FROM entradas WHERE id=? AND usuario_id=?",
                (request.form["id"], session["uid"]))
    con.commit()
    con.close()
    return redirect(url_for("inicio"))

@app.route("/salir")
def salir():
    session.clear()
    return redirect(url_for("login"))

init_db()
app.run(debug=True)
