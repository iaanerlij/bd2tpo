
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import os

# ──────────────────────────────────────────
# Conexión
# ──────────────────────────────────────────
client = MongoClient("mongodb://localhost:27017/")
db = client["bd2tpo"]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def limpiar_colecciones():
    """Borra todo antes de recargar (útil para re-ejecutar sin duplicados)."""
    for col in ["pacientes", "propietarios", "veterinarios", "consultas", "vacunaciones"]:
        db[col].drop()
    print("✓ Colecciones limpiadas")


# ──────────────────────────────────────────
# PROPIETARIOS
# ──────────────────────────────────────────
def cargar_propietarios():
    df = pd.read_csv(os.path.join(DATA_DIR, "propietarios.csv"), dtype=str)
    docs_csv = df.to_dict("records")

    # 10 registros propios
    extras = [
        {"id_propietario": "C007", "nombre": "Lucía",    "apellido": "Fernández", "dni": "39001122", "email": "lucia@gmail.com",   "telefono": "3514001234", "ciudad": "Tucumán",        "provincia": "Tucumán",        "activo": True},
        {"id_propietario": "C008", "nombre": "Martín",   "apellido": "Gómez",     "dni": "33445566", "email": "martin@gmail.com",  "telefono": "2994002345", "ciudad": "Neuquén",         "provincia": "Neuquén",        "activo": True},
        {"id_propietario": "C009", "nombre": "Sofía",    "apellido": "Torres",    "dni": "44556677", "email": "sofia@gmail.com",   "telefono": "3434003456", "ciudad": "Paraná",          "provincia": "Entre Ríos",     "activo": True},
        {"id_propietario": "C010", "nombre": "Nicolás",  "apellido": "Peralta",   "dni": "31223344", "email": "nico@gmail.com",    "telefono": "3514004567", "ciudad": "San Miguel de TM","provincia": "Tucumán",        "activo": True},
        {"id_propietario": "C011", "nombre": "Camila",   "apellido": "Méndez",    "dni": "40112233", "email": "cami@gmail.com",    "telefono": "2616005678", "ciudad": "San Juan",        "provincia": "San Juan",       "activo": True},
        {"id_propietario": "C012", "nombre": "Ezequiel", "apellido": "Ruiz",      "dni": "37889900", "email": "eze@gmail.com",     "telefono": "3835006789", "ciudad": "La Rioja",        "provincia": "La Rioja",       "activo": True},
        {"id_propietario": "C013", "nombre": "Florencia","apellido": "Castro",    "dni": "36001199", "email": "flor@gmail.com",    "telefono": "2615007890", "ciudad": "Mendoza",         "provincia": "Mendoza",        "activo": True},
        {"id_propietario": "C014", "nombre": "Agustín",  "apellido": "Romero",    "dni": "43221100", "email": "agus@gmail.com",    "telefono": "3875008901", "ciudad": "Jujuy",           "provincia": "Jujuy",          "activo": True},
        {"id_propietario": "C015", "nombre": "Valeria",  "apellido": "Suárez",    "dni": "38990011", "email": "vale2@gmail.com",   "telefono": "3815009012", "ciudad": "Santiago del Estero","provincia": "Santiago del Estero","activo": True},
        {"id_propietario": "C016", "nombre": "Rodrigo",  "apellido": "Vargas",    "dni": "34556677", "email": "rodri@gmail.com",   "telefono": "2975010123", "ciudad": "Bahía Blanca",    "provincia": "Buenos Aires",   "activo": False},
    ]

    # Agregar activo=True a los del CSV (no tienen esa columna)
    for d in docs_csv:
        d["activo"] = True

    db["propietarios"].insert_many(docs_csv + extras)
    print(f"✓ propietarios: {len(docs_csv)} CSV + {len(extras)} propios = {len(docs_csv)+len(extras)} docs")


# ──────────────────────────────────────────
# VETERINARIOS
# ──────────────────────────────────────────
def cargar_veterinarios():
    df = pd.read_csv(os.path.join(DATA_DIR, "veterinarios.csv"), dtype=str)
    docs_csv = df.to_dict("records")

    # Convertir activo a bool
    for d in docs_csv:
        d["activo"] = d["activo"].strip() == "True"

    extras = [
        {"id_vet": "V006", "nombre": "Pablo",    "apellido": "Navarro",   "matricula": "VET-0130", "especialidad": "Clínica General",  "sucursal": "Belgrano",  "activo": True},
        {"id_vet": "V007", "nombre": "Mariana",  "apellido": "Pérez",     "matricula": "VET-0145", "especialidad": "Neurología",        "sucursal": "Palermo",   "activo": True},
        {"id_vet": "V008", "nombre": "Sebastián","apellido": "López",     "matricula": "VET-0160", "especialidad": "Traumatología",     "sucursal": "Caballito", "activo": True},
        {"id_vet": "V009", "nombre": "Andrea",   "apellido": "Morales",   "matricula": "VET-0175", "especialidad": "Oftalmología",      "sucursal": "Belgrano",  "activo": True},
        {"id_vet": "V010", "nombre": "Carlos",   "apellido": "Vega",      "matricula": "VET-0190", "especialidad": "Cardiología",       "sucursal": "Palermo",   "activo": True},
        {"id_vet": "V011", "nombre": "Natalia",  "apellido": "Reyes",     "matricula": "VET-0205", "especialidad": "Clínica General",  "sucursal": "Caballito", "activo": False},
        {"id_vet": "V012", "nombre": "Fernando", "apellido": "Acosta",    "matricula": "VET-0220", "especialidad": "Cirugía",           "sucursal": "Belgrano",  "activo": True},
        {"id_vet": "V013", "nombre": "Daniela",  "apellido": "Ortega",    "matricula": "VET-0235", "especialidad": "Dermatología",      "sucursal": "Palermo",   "activo": True},
        {"id_vet": "V014", "nombre": "Julián",   "apellido": "Mendoza",   "matricula": "VET-0250", "especialidad": "Odontología",       "sucursal": "Caballito", "activo": True},
        {"id_vet": "V015", "nombre": "Patricia", "apellido": "Silva",     "matricula": "VET-0265", "especialidad": "Clínica General",  "sucursal": "Belgrano",  "activo": True},
    ]

    db["veterinarios"].insert_many(docs_csv + extras)
    print(f"✓ veterinarios: {len(docs_csv)} CSV + {len(extras)} propios = {len(docs_csv)+len(extras)} docs")


# ──────────────────────────────────────────
# PACIENTES
# ──────────────────────────────────────────
def cargar_pacientes():
    df = pd.read_csv(os.path.join(DATA_DIR, "pacientes.csv"), dtype=str)
    docs_csv = df.to_dict("records")

    for d in docs_csv:
        d["activo"] = d["activo"].strip() == "True"

    extras = [
        {"id_paciente": "P009", "nombre": "Tortuga",  "especie": "Reptil",   "raza": "Tortuga de tierra",  "fecha_nac": "2015-03-10", "id_propietario": "C007", "activo": True},
        {"id_paciente": "P010", "nombre": "Hammy",    "especie": "Roedor",   "raza": "Hámster sirio",       "fecha_nac": "2023-06-01", "id_propietario": "C008", "activo": True},
        {"id_paciente": "P011", "nombre": "Canela",   "especie": "Gato",     "raza": "Maine Coon",          "fecha_nac": "2022-09-15", "id_propietario": "C009", "activo": True},
        {"id_paciente": "P012", "nombre": "Thor",     "especie": "Perro",    "raza": "Rottweiler",          "fecha_nac": "2021-04-20", "id_propietario": "C010", "activo": True},
        {"id_paciente": "P013", "nombre": "Princesa", "especie": "Perro",    "raza": "Chihuahua",           "fecha_nac": "2020-11-30", "id_propietario": "C011", "activo": True},
        {"id_paciente": "P014", "nombre": "Nemo",     "especie": "Pez",      "raza": "Pez payaso",          "fecha_nac": "2023-01-05", "id_propietario": "C012", "activo": True},
        {"id_paciente": "P015", "nombre": "Bala",     "especie": "Perro",    "raza": "Bulldog Francés",     "fecha_nac": "2022-07-18", "id_propietario": "C013", "activo": True},
        {"id_paciente": "P016", "nombre": "Copito",   "especie": "Conejo",   "raza": "Mini Lop",            "fecha_nac": "2023-03-22", "id_propietario": "C014", "activo": True},
        {"id_paciente": "P017", "nombre": "Simba",    "especie": "Gato",     "raza": "Bengalí",             "fecha_nac": "2021-12-10", "id_propietario": "C001", "activo": True},
        {"id_paciente": "P018", "nombre": "Rocco",    "especie": "Perro",    "raza": "Dóberman",            "fecha_nac": "2019-08-25", "id_propietario": "C002", "activo": False},
    ]

    db["pacientes"].insert_many(docs_csv + extras)
    print(f"✓ pacientes: {len(docs_csv)} CSV + {len(extras)} propios = {len(docs_csv)+len(extras)} docs")


# ──────────────────────────────────────────
# CONSULTAS
# ──────────────────────────────────────────
def cargar_consultas():
    df = pd.read_csv(os.path.join(DATA_DIR, "consultas.csv"), dtype=str)
    docs_csv = df.to_dict("records")

    for d in docs_csv:
        d["costo"] = float(d["costo"])
        d["fecha"] = datetime.strptime(d["fecha"].strip(), "%Y-%m-%d")

    extras = [
        {"id_consulta": "CON009", "id_paciente": "P009", "id_vet": "V006", "fecha": datetime(2026, 5, 1),  "motivo": "Control anual",        "diagnostico": "Sano",               "costo": 3500.0,  "estado": "Cerrada"},
        {"id_consulta": "CON010", "id_paciente": "P010", "id_vet": "V007", "fecha": datetime(2026, 5, 5),  "motivo": "Convulsiones",          "diagnostico": "Epilepsia leve",     "costo": 8500.0,  "estado": "Seguimiento"},
        {"id_consulta": "CON011", "id_paciente": "P011", "id_vet": "V003", "fecha": datetime(2026, 5, 8),  "motivo": "Caída de pelo",         "diagnostico": "Dermatitis seborreica","costo": 5200.0, "estado": "Cerrada"},
        {"id_consulta": "CON012", "id_paciente": "P012", "id_vet": "V008", "fecha": datetime(2026, 5, 12), "motivo": "Cojera",                "diagnostico": "Fractura radio",     "costo": 14000.0, "estado": "Seguimiento"},
        {"id_consulta": "CON013", "id_paciente": "P013", "id_vet": "V005", "fecha": datetime(2026, 5, 15), "motivo": "Control post-vacuna",   "diagnostico": "Sin novedades",      "costo": 2000.0,  "estado": "Cerrada"},
        {"id_consulta": "CON014", "id_paciente": "P015", "id_vet": "V001", "fecha": datetime(2026, 5, 20), "motivo": "Vómitos recurrentes",   "diagnostico": "Gastritis",          "costo": 5500.0,  "estado": "Cerrada"},
        {"id_consulta": "CON015", "id_paciente": "P016", "id_vet": "V006", "fecha": datetime(2026, 5, 22), "motivo": "Control anual",         "diagnostico": "Sano",               "costo": 3000.0,  "estado": "Cerrada"},
        {"id_consulta": "CON016", "id_paciente": "P017", "id_vet": "V013", "fecha": datetime(2026, 6, 1),  "motivo": "Alergia cutánea",       "diagnostico": "Dermatitis atópica", "costo": 6200.0,  "estado": "Seguimiento"},
        {"id_consulta": "CON017", "id_paciente": "P018", "id_vet": "V002", "fecha": datetime(2026, 6, 3),  "motivo": "Extracción dentaria",   "diagnostico": "Periodontitis",      "costo": 12500.0, "estado": "Cerrada"},
        {"id_consulta": "CON018", "id_paciente": "P001", "id_vet": "V010", "fecha": datetime(2026, 6, 5),  "motivo": "Control anual",         "diagnostico": "Soplo cardíaco leve","costo": 9000.0,  "estado": "Seguimiento"},
    ]

    db["consultas"].insert_many(docs_csv + extras)
    print(f"✓ consultas: {len(docs_csv)} CSV + {len(extras)} propios = {len(docs_csv)+len(extras)} docs")


# ──────────────────────────────────────────
# VACUNACIONES
# ──────────────────────────────────────────
def cargar_vacunaciones():
    df = pd.read_csv(os.path.join(DATA_DIR, "vacunaciones.csv"), dtype=str)
    docs_csv = df.to_dict("records")

    for d in docs_csv:
        d["fecha_aplicacion"] = datetime.strptime(d["fecha_aplicacion"].strip(), "%Y-%m-%d")
        d["proxima_dosis"]    = datetime.strptime(d["proxima_dosis"].strip(),    "%Y-%m-%d")

    extras = [
        {"id_vacuna": "VAC007", "id_paciente": "P009", "id_vet": "V006", "fecha_aplicacion": datetime(2026, 5, 1),  "nombre_vacuna": "Reptivac",       "proxima_dosis": datetime(2027, 5, 1)},
        {"id_vacuna": "VAC008", "id_paciente": "P011", "id_vet": "V003", "fecha_aplicacion": datetime(2026, 5, 8),  "nombre_vacuna": "Triple Felina",  "proxima_dosis": datetime(2027, 5, 8)},
        {"id_vacuna": "VAC009", "id_paciente": "P012", "id_vet": "V006", "fecha_aplicacion": datetime(2026, 5, 12), "nombre_vacuna": "Sextuple",       "proxima_dosis": datetime(2027, 5, 12)},
        {"id_vacuna": "VAC010", "id_paciente": "P013", "id_vet": "V005", "fecha_aplicacion": datetime(2026, 5, 15), "nombre_vacuna": "Antirrábica",    "proxima_dosis": datetime(2027, 5, 15)},
        {"id_vacuna": "VAC011", "id_paciente": "P015", "id_vet": "V001", "fecha_aplicacion": datetime(2026, 5, 20), "nombre_vacuna": "Sextuple",       "proxima_dosis": datetime(2027, 5, 20)},
        {"id_vacuna": "VAC012", "id_paciente": "P016", "id_vet": "V006", "fecha_aplicacion": datetime(2026, 5, 22), "nombre_vacuna": "Antirrábica",    "proxima_dosis": datetime(2027, 5, 22)},
        {"id_vacuna": "VAC013", "id_paciente": "P017", "id_vet": "V013", "fecha_aplicacion": datetime(2026, 6, 1),  "nombre_vacuna": "Triple Felina",  "proxima_dosis": datetime(2025, 6, 1)},   # ← vencida, útil para consulta 6
        {"id_vacuna": "VAC014", "id_paciente": "P018", "id_vet": "V002", "fecha_aplicacion": datetime(2025, 3, 1),  "nombre_vacuna": "Sextuple",       "proxima_dosis": datetime(2026, 3, 1)},   # ← vencida
        {"id_vacuna": "VAC015", "id_paciente": "P003", "id_vet": "V001", "fecha_aplicacion": datetime(2025, 1, 15), "nombre_vacuna": "Antirrábica",    "proxima_dosis": datetime(2026, 1, 15)},  # ← vencida
        {"id_vacuna": "VAC016", "id_paciente": "P007", "id_vet": "V005", "fecha_aplicacion": datetime(2025, 12, 1), "nombre_vacuna": "Sextuple",       "proxima_dosis": datetime(2026, 12, 1)},
    ]

    db["vacunaciones"].insert_many(docs_csv + extras)
    print(f"✓ vacunaciones: {len(docs_csv)} CSV + {len(extras)} propios = {len(docs_csv)+len(extras)} docs")


# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Cargando datos en MongoDB ===\n")
    limpiar_colecciones()
    cargar_propietarios()
    cargar_veterinarios()
    cargar_pacientes()
    cargar_consultas()
    cargar_vacunaciones()
    print("\n✅ Carga MongoDB completa\n")
    client.close()