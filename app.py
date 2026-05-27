import datetime
import os

# --- CONFIGURACIÓN DEL SISTEMA ---
ABECEDARIO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
ARCHIVO_LOG = "historial_secreto.txt"

def calcular_desplazamiento():
    # El rotor gira según la fecha: (Día * Mes) + (Año % 100)
    hoy = datetime.date.today()
    clave = (hoy.day * hoy.month) + (hoy.year % 100)
    return clave % len(ABECEDARIO)

def motor_enigma(texto, modo='cifrar'):
    n = len(ABECEDARIO)
    desplazamiento = calcular_desplazamiento()
    
    if modo == 'descifrar':
        desplazamiento = -desplazamiento
        
    resultado = ""
    for char in texto.upper():
        if char in ABECEDARIO:
            indice = ABECEDARIO.index(char)
            nuevo_indice = (indice + desplazamiento) % n
            resultado += ABECEDARIO[nuevo_indice]
        else:
            resultado += char
    return resultado

def registrar_mensaje(accion, original, resultado):
    # Guarda el movimiento en un archivo oculto
    with open(ARCHIVO_LOG, "a") as f:
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{fecha}] {accion.upper()} | Orig: {original} | Result: {resultado}\n")

# --- INTERFAZ ---
def ejecutar():
    print("==========================================")
    print("   SISTEMA DE CIFRADO ENIGMA O.I.M.C.      ")
    print(f"   Fecha Activa: {datetime.date.today()}")
    print("==========================================")
    
    opcion = input("1: Cifrar | 2: Descifrar: ")
    mensaje = input("Introduce mensaje: ")
    
    if opcion == '1':
        res = motor_enigma(mensaje, 'cifrar')
        print(f"\nRESULTADO CIFRADO: {res}")
        registrar_mensaje("Cifrado", mensaje, res)
    elif opcion == '2':
        res = motor_enigma(mensaje, 'descifrar')
        print(f"\nRESULTADO DESCIFRADO: {res}")
        registrar_mensaje("Descifrado", mensaje, res)
    else:
        print("Error en protocolo.")

if __name__ == "__main__":
    ejecutar()
