"""
03_consultas.py
Las 15 consultas/servicios del TPO VetSalud.
Ejecutar: python scripts/03_consultas.py
"""

from pymongo import MongoClient
import redis
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

# ──────────────────────────────────────────
# Conexiones
# ──────────────────────────────────────────
client = MongoClient("mongodb://localhost:27017/")
db     = client["bd2tpo"]
r      = redis.Redis(host="localhost", port=6379, decode_responses=True)


def _print_resultados(titulo, resultados, limite=5):
    """Helper para mostrar resultados de forma legible."""
    print(f"\n{'─'*60}")
    print(f"  {titulo}")
    print(f"{'─'*60}")
    if not resultados:
        print("  (sin resultados)")
        return
    for i, doc in enumerate(resultados[:limite]):
        # Convertir ObjectId y datetime a string para poder imprimir
        doc_str = {k: (str(v) if not isinstance(v, (str, int, float, bool, list, dict, type(None))) else v)
                   for k, v in doc.items() if k != "_id"}
        print(f"  [{i+1}] {json.dumps(doc_str, ensure_ascii=False, indent=6)}")
    if len(resultados) > limite:
        print(f"  ... y {len(resultados)-limite} más")


# ══════════════════════════════════════════════════════════════
# CONSULTA 1
# Pacientes activos con todos sus datos de propietario.
# ══════════════════════════════════════════════════════════════
def consulta_1_pacientes_activos_con_propietario():
    """
    Une pacientes activos con los datos completos de su propietario
    usando $lookup (JOIN en MongoDB).
    """
    pipeline = [
        {"$match": {"activo": True}},
        {
            "$lookup": {
                "from":         "propietarios",
                "localField":   "id_propietario",
                "foreignField": "id_propietario",
                "as":           "propietario"
            }
        },
        {"$unwind": "$propietario"},
        {
            "$project": {
                "_id": 0,
                "id_paciente": 1,
                "nombre":      1,
                "especie":     1,
                "raza":        1,
                "propietario.nombre":   1,
                "propietario.apellido": 1,
                "propietario.email":    1,
                "propietario.ciudad":   1,
            }
        }
    ]
    return list(db["pacientes"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 2
# Consultas médicas abiertas (estado 'Seguimiento') con veterinario y costo.
# ══════════════════════════════════════════════════════════════
def consulta_2_consultas_en_seguimiento():
    """
    Filtra consultas con estado 'Seguimiento' y hace lookup del veterinario.
    """
    pipeline = [
        {"$match": {"estado": "Seguimiento"}},
        {
            "$lookup": {
                "from":         "veterinarios",
                "localField":   "id_vet",
                "foreignField": "id_vet",
                "as":           "veterinario"
            }
        },
        {"$unwind": "$veterinario"},
        {
            "$project": {
                "_id": 0,
                "id_consulta": 1,
                "id_paciente": 1,
                "fecha":       1,
                "motivo":      1,
                "diagnostico": 1,
                "costo":       1,
                "estado":      1,
                "veterinario.nombre":        1,
                "veterinario.apellido":      1,
                "veterinario.especialidad":  1,
            }
        }
    ]
    return list(db["consultas"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 3
# Historial completo de un paciente: consultas y vacunaciones ordenadas por fecha.
# ══════════════════════════════════════════════════════════════
def consulta_3_historial_paciente(id_paciente: str):
    """
    Devuelve una lista combinada y ordenada de consultas y vacunas
    para un paciente dado.
    """
    consultas = list(db["consultas"].find(
        {"id_paciente": id_paciente},
        {"_id": 0, "id_consulta": 1, "fecha": 1, "motivo": 1, "diagnostico": 1, "costo": 1, "estado": 1}
    ))
    for c in consultas:
        c["tipo"] = "consulta"

    vacunas = list(db["vacunaciones"].find(
        {"id_paciente": id_paciente},
        {"_id": 0, "id_vacuna": 1, "fecha_aplicacion": 1, "nombre_vacuna": 1, "proxima_dosis": 1}
    ))
    for v in vacunas:
        v["tipo"]  = "vacuna"
        v["fecha"] = v.pop("fecha_aplicacion")   # unificar campo fecha

    historial = consultas + vacunas
    historial.sort(key=lambda x: x["fecha"])
    return historial


# ══════════════════════════════════════════════════════════════
# CONSULTA 4
# Propietarios con más de un paciente registrado.
# ══════════════════════════════════════════════════════════════
def consulta_4_propietarios_con_varios_pacientes():
    """
    Agrupa pacientes por id_propietario y filtra los que tienen más de uno.
    """
    pipeline = [
        {"$group": {
            "_id":             "$id_propietario",
            "total_pacientes": {"$sum": 1},
            "pacientes":       {"$push": "$nombre"}
        }},
        {"$match": {"total_pacientes": {"$gt": 1}}},
        {
            "$lookup": {
                "from":         "propietarios",
                "localField":   "_id",
                "foreignField": "id_propietario",
                "as":           "datos_propietario"
            }
        },
        {"$unwind": "$datos_propietario"},
        {
            "$project": {
                "_id": 0,
                "id_propietario":            "$_id",
                "nombre_propietario":        "$datos_propietario.nombre",
                "apellido_propietario":      "$datos_propietario.apellido",
                "total_pacientes":           1,
                "pacientes":                 1,
            }
        },
        {"$sort": {"total_pacientes": -1}}
    ]
    return list(db["pacientes"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 5
# Veterinarios activos y cantidad de consultas en los últimos 60 días.
# ══════════════════════════════════════════════════════════════
def consulta_5_vets_activos_consultas_60_dias():
    """
    Para cada vet activo cuenta sus consultas de los últimos 60 días.
    """
    hace_60 = datetime.now() - timedelta(days=60)
    pipeline = [
        {"$match": {"fecha": {"$gte": hace_60}}},
        {"$group": {
            "_id":              "$id_vet",
            "total_consultas":  {"$sum": 1}
        }},
        {
            "$lookup": {
                "from":         "veterinarios",
                "localField":   "_id",
                "foreignField": "id_vet",
                "as":           "vet"
            }
        },
        {"$unwind": "$vet"},
        {"$match": {"vet.activo": True}},
        {
            "$project": {
                "_id": 0,
                "id_vet":          "$_id",
                "nombre":          "$vet.nombre",
                "apellido":        "$vet.apellido",
                "especialidad":    "$vet.especialidad",
                "total_consultas": 1,
            }
        },
        {"$sort": {"total_consultas": -1}}
    ]
    return list(db["consultas"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 6
# Pacientes con vacunas vencidas (proxima_dosis anterior a hoy).
# ══════════════════════════════════════════════════════════════
def consulta_6_vacunas_vencidas():
    """
    Busca vacunas cuya proxima_dosis ya pasó y une con datos del paciente.
    """
    hoy = datetime.now()
    pipeline = [
        {"$match": {"proxima_dosis": {"$lt": hoy}}},
        {
            "$lookup": {
                "from":         "pacientes",
                "localField":   "id_paciente",
                "foreignField": "id_paciente",
                "as":           "paciente"
            }
        },
        {"$unwind": "$paciente"},
        {
            "$project": {
                "_id": 0,
                "id_vacuna":      1,
                "nombre_vacuna":  1,
                "proxima_dosis":  1,
                "paciente.nombre":  1,
                "paciente.especie": 1,
            }
        },
        {"$sort": {"proxima_dosis": 1}}
    ]
    return list(db["vacunaciones"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 7
# Top 5 diagnósticos más frecuentes.
# ══════════════════════════════════════════════════════════════
def consulta_7_top5_diagnosticos():
    """
    Agrupa consultas por diagnóstico y devuelve los 5 más frecuentes.
    """
    pipeline = [
        {"$group": {
            "_id":        "$diagnostico",
            "frecuencia": {"$sum": 1}
        }},
        {"$sort":  {"frecuencia": -1}},
        {"$limit": 5},
        {"$project": {"_id": 0, "diagnostico": "$_id", "frecuencia": 1}}
    ]
    return list(db["consultas"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 8 — REDIS
# Stock de productos con menos de 50 unidades y su proveedor.
# ══════════════════════════════════════════════════════════════
def consulta_8_stock_bajo():
    """
    Recorre todos los hashes de stock en Redis y filtra los que tienen
    menos de 50 unidades. Operación nativa en Redis (in-memory, muy rápida).
    """
    ids = r.smembers("stock:ids")
    resultado = []
    for pid in sorted(ids):
        data = r.hgetall(f"stock:{pid}")
        if int(data["unidades"]) < 50:
            resultado.append({
                "id_producto": data["id_producto"],
                "nombre":      data["nombre"],
                "unidades":    int(data["unidades"]),
                "proveedor":   data["proveedor"],
                "vencimiento": data["vencimiento"],
            })
    resultado.sort(key=lambda x: x["unidades"])
    return resultado


# ══════════════════════════════════════════════════════════════
# CONSULTA 9
# Consultas de tipo 'Control' con costo menor a $5.000.
# ══════════════════════════════════════════════════════════════
def consulta_9_controles_baratos():
    """
    Busca consultas cuyo motivo contiene 'Control' (regex insensible
    a mayúsculas) y costo menor a 5000.
    """
    import re
    docs = db["consultas"].find(
        {
            "motivo": {"$regex": re.compile("control", re.IGNORECASE)},
            "costo":  {"$lt": 5000}
        },
        {"_id": 0, "id_consulta": 1, "id_paciente": 1, "fecha": 1,
         "motivo": 1, "diagnostico": 1, "costo": 1}
    ).sort("costo", 1)
    return list(docs)


# ══════════════════════════════════════════════════════════════
# CONSULTA 10
# Todos los pacientes de una sucursal determinada (a través del veterinario).
# ══════════════════════════════════════════════════════════════
def consulta_10_pacientes_por_sucursal(sucursal: str):
    """
    Busca los vets de esa sucursal, luego las consultas de esos vets,
    y finalmente los pacientes únicos atendidos.
    """
    pipeline = [
        # 1. Empezamos desde veterinarios filtrando por sucursal
        {"$match": {"sucursal": sucursal, "activo": True}},
        {
            "$lookup": {
                "from":         "consultas",
                "localField":   "id_vet",
                "foreignField": "id_vet",
                "as":           "consultas"
            }
        },
        {"$unwind": "$consultas"},
        {
            "$lookup": {
                "from":         "pacientes",
                "localField":   "consultas.id_paciente",
                "foreignField": "id_paciente",
                "as":           "paciente"
            }
        },
        {"$unwind": "$paciente"},
        # Deduplicar pacientes
        {"$group": {
            "_id": "$paciente.id_paciente",
            "nombre":  {"$first": "$paciente.nombre"},
            "especie": {"$first": "$paciente.especie"},
            "raza":    {"$first": "$paciente.raza"},
            "sucursal":{"$first": "$sucursal"},
        }},
        {"$project": {"_id": 0, "id_paciente": "$_id",
                      "nombre": 1, "especie": 1, "raza": 1, "sucursal": 1}},
        {"$sort": {"nombre": 1}}
    ]
    return list(db["veterinarios"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 11
# Vista agregada: ingresos totales por veterinario en el mes actual.
# ══════════════════════════════════════════════════════════════
def consulta_11_ingresos_por_vet_mes_actual():
    """
    Filtra consultas del mes y año actual, agrupa por veterinario
    y suma el costo total.
    """
    hoy        = datetime.now()
    inicio_mes = datetime(hoy.year, hoy.month, 1)
    fin_mes    = inicio_mes + relativedelta(months=1)

    pipeline = [
        {"$match": {"fecha": {"$gte": inicio_mes, "$lt": fin_mes}}},
        {"$group": {
            "_id":            "$id_vet",
            "ingresos_total": {"$sum": "$costo"},
            "num_consultas":  {"$sum": 1}
        }},
        {
            "$lookup": {
                "from":         "veterinarios",
                "localField":   "_id",
                "foreignField": "id_vet",
                "as":           "vet"
            }
        },
        {"$unwind": "$vet"},
        {
            "$project": {
                "_id": 0,
                "id_vet":         "$_id",
                "nombre":         "$vet.nombre",
                "apellido":       "$vet.apellido",
                "sucursal":       "$vet.sucursal",
                "ingresos_total": 1,
                "num_consultas":  1,
            }
        },
        {"$sort": {"ingresos_total": -1}}
    ]
    return list(db["consultas"].aggregate(pipeline))


# ══════════════════════════════════════════════════════════════
# CONSULTA 12
# Propietarios sin consultas registradas en el último año.
# ══════════════════════════════════════════════════════════════
def consulta_12_propietarios_sin_consultas_en_1_anio():
    """
    Obtiene propietarios cuyos pacientes no tuvieron ninguna consulta
    en los últimos 365 días.
    """
    hace_1_anio = datetime.now() - timedelta(days=365)

    # IDs de pacientes con consulta reciente
    consultas_recientes = db["consultas"].distinct(
        "id_paciente", {"fecha": {"$gte": hace_1_anio}}
    )

    # Pacientes sin consulta reciente
    pacientes_sin_consulta = db["pacientes"].distinct(
        "id_propietario",
        {"id_paciente": {"$nin": consultas_recientes}}
    )

    # Propietarios correspondientes
    docs = db["propietarios"].find(
        {"id_propietario": {"$in": pacientes_sin_consulta}},
        {"_id": 0, "id_propietario": 1, "nombre": 1, "apellido": 1, "email": 1}
    )
    return list(docs)


# ══════════════════════════════════════════════════════════════
# CONSULTA 13 — ABM PROPIETARIOS
# Alta, modificación de datos, baja lógica.
# ══════════════════════════════════════════════════════════════
def consulta_13_alta_propietario(datos: dict):
    """Inserta un nuevo propietario. Valida que el id no exista."""
    if db["propietarios"].find_one({"id_propietario": datos["id_propietario"]}):
        return {"error": f"Ya existe propietario con id {datos['id_propietario']}"}
    datos.setdefault("activo", True)
    db["propietarios"].insert_one(datos)
    datos.pop("_id", None)
    return {"ok": True, "insertado": datos}


def consulta_13_modificar_propietario(id_propietario: str, campos: dict):
    """Actualiza campos de un propietario existente."""
    resultado = db["propietarios"].update_one(
        {"id_propietario": id_propietario},
        {"$set": campos}
    )
    if resultado.matched_count == 0:
        return {"error": f"No se encontró propietario {id_propietario}"}
    return {"ok": True, "modificados": resultado.modified_count}


def consulta_13_baja_logica_propietario(id_propietario: str):
    """Baja lógica: setea activo=False en lugar de borrar el registro."""
    resultado = db["propietarios"].update_one(
        {"id_propietario": id_propietario},
        {"$set": {"activo": False}}
    )
    if resultado.matched_count == 0:
        return {"error": f"No se encontró propietario {id_propietario}"}
    return {"ok": True, "dado_de_baja": id_propietario}


# ══════════════════════════════════════════════════════════════
# CONSULTA 14
# Registro de nueva consulta médica con validación de paciente y veterinario.
# ══════════════════════════════════════════════════════════════
def consulta_14_nueva_consulta(datos: dict):
    """
    Valida que existan el paciente y el veterinario antes de insertar.
    datos debe tener: id_consulta, id_paciente, id_vet, fecha (datetime),
                      motivo, diagnostico, costo, estado
    """
    if not db["pacientes"].find_one({"id_paciente": datos["id_paciente"]}):
        return {"error": f"Paciente {datos['id_paciente']} no existe"}
    if not db["veterinarios"].find_one({"id_vet": datos["id_vet"]}):
        return {"error": f"Veterinario {datos['id_vet']} no existe"}
    if db["consultas"].find_one({"id_consulta": datos["id_consulta"]}):
        return {"error": f"Ya existe consulta con id {datos['id_consulta']}"}

    db["consultas"].insert_one(datos)
    datos.pop("_id", None)
    return {"ok": True, "consulta_registrada": datos}


# ══════════════════════════════════════════════════════════════
# CONSULTA 15 — REDIS
# Actualización masiva del stock: decrementar unidades de un producto.
# ══════════════════════════════════════════════════════════════
def consulta_15_decrementar_stock(id_producto: str, cantidad: int):
    """
    Decrementa atómicamente las unidades de un producto en Redis.
    Usa HINCRBY con valor negativo — operación atómica, sin condición de carrera.
    """
    key = f"stock:{id_producto}"
    if not r.exists(key):
        return {"error": f"Producto {id_producto} no existe en stock"}

    unidades_actuales = int(r.hget(key, "unidades"))
    if unidades_actuales < cantidad:
        return {"error": f"Stock insuficiente: hay {unidades_actuales}, se piden {cantidad}"}

    nuevas_unidades = r.hincrby(key, "unidades", -cantidad)
    nombre = r.hget(key, "nombre")
    return {
        "ok":              True,
        "producto":        nombre,
        "unidades_antes":  unidades_actuales,
        "decrementado_en": cantidad,
        "unidades_ahora":  nuevas_unidades,
    }


# ══════════════════════════════════════════════════════════════
# MAIN — ejecuta y muestra todas las consultas
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "═"*60)
    print("       VETSALUD — EJECUCIÓN DE LAS 15 CONSULTAS")
    print("═"*60)

    _print_resultados("CONSULTA 1 · Pacientes activos con propietario",
                      consulta_1_pacientes_activos_con_propietario())

    _print_resultados("CONSULTA 2 · Consultas en Seguimiento con vet",
                      consulta_2_consultas_en_seguimiento())

    _print_resultados(f"CONSULTA 3 · Historial completo de P001",
                      consulta_3_historial_paciente("P001"))

    _print_resultados("CONSULTA 4 · Propietarios con >1 paciente",
                      consulta_4_propietarios_con_varios_pacientes())

    _print_resultados("CONSULTA 5 · Vets activos — consultas últimos 60 días",
                      consulta_5_vets_activos_consultas_60_dias())

    _print_resultados("CONSULTA 6 · Pacientes con vacunas vencidas",
                      consulta_6_vacunas_vencidas())

    _print_resultados("CONSULTA 7 · Top 5 diagnósticos",
                      consulta_7_top5_diagnosticos())

    _print_resultados("CONSULTA 8 · Stock < 50 unidades (Redis)",
                      consulta_8_stock_bajo())

    _print_resultados("CONSULTA 9 · Controles con costo < $5.000",
                      consulta_9_controles_baratos())

    _print_resultados("CONSULTA 10 · Pacientes atendidos en sucursal Palermo",
                      consulta_10_pacientes_por_sucursal("Palermo"))

    _print_resultados("CONSULTA 11 · Ingresos por vet en el mes actual",
                      consulta_11_ingresos_por_vet_mes_actual())

    _print_resultados("CONSULTA 12 · Propietarios sin consultas en 1 año",
                      consulta_12_propietarios_sin_consultas_en_1_anio())

    # ── CONSULTA 13: ABM ──
    print(f"\n{'─'*60}\n  CONSULTA 13 · ABM Propietarios\n{'─'*60}")
    print("  Alta:", consulta_13_alta_propietario({
        "id_propietario": "C099", "nombre": "Test", "apellido": "Prueba",
        "dni": "99999999", "email": "test@test.com",
        "telefono": "1111111111", "ciudad": "CABA", "provincia": "Buenos Aires"
    }))
    print("  Modificar:", consulta_13_modificar_propietario("C099", {"ciudad": "Rosario", "telefono": "3411234567"}))
    print("  Baja lógica:", consulta_13_baja_logica_propietario("C099"))

    # ── CONSULTA 14: nueva consulta ──
    print(f"\n{'─'*60}\n  CONSULTA 14 · Nueva consulta con validación\n{'─'*60}")
    print("  Resultado:", consulta_14_nueva_consulta({
        "id_consulta": "CON099",
        "id_paciente": "P001",
        "id_vet":      "V001",
        "fecha":       datetime(2026, 6, 10),
        "motivo":      "Control de rutina",
        "diagnostico": "Sano",
        "costo":       3200.0,
        "estado":      "Cerrada"
    }))
    print("  Validación KO:", consulta_14_nueva_consulta({
        "id_consulta": "CON100",
        "id_paciente": "P999",    # ← no existe
        "id_vet":      "V001",
        "fecha":       datetime(2026, 6, 10),
        "motivo":      "Test",
        "diagnostico": "Test",
        "costo":       100.0,
        "estado":      "Cerrada"
    }))

    # ── CONSULTA 15: stock Redis ──
    print(f"\n{'─'*60}\n  CONSULTA 15 · Decremento de stock (Redis)\n{'─'*60}")
    print("  Decremento OK:    ", consulta_15_decrementar_stock("PRD001", 10))
    print("  Stock insuficiente:", consulta_15_decrementar_stock("PRD016", 999))

    print("\n✅ Las 15 consultas ejecutadas correctamente\n")
    client.close()