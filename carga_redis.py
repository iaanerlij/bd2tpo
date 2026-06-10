"""
02_carga_redis.py
Carga el stock farmacéutico en Redis usando estructuras Hash.
Estructura de cada producto: HSET stock:<id> campo valor ...
Ejecutar: python scripts/02_carga_redis.py
"""

import pandas as pd
import redis
import os

# ──────────────────────────────────────────
# Conexión
# ──────────────────────────────────────────
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def limpiar_stock():
    """Borra todas las keys de stock antes de recargar."""
    keys = r.keys("stock:*")
    if keys:
        r.delete(*keys)
    print("✓ Stock Redis limpiado")


def cargar_stock():
    df = pd.read_csv(os.path.join(DATA_DIR, "stock_farmaceutico.csv"), dtype=str)

    # 10 productos propios adicionales
    extras = [
        {"id_producto": "PRD007", "nombre": "Doxiciclina 100mg",      "categoria": "Antibiótico",       "unidades": "90",  "precio_unit": "1100", "vencimiento": "2027-03-15", "proveedor": "VetFarma SA"},
        {"id_producto": "PRD008", "nombre": "Tramadol 50mg",           "categoria": "Analgésico",        "unidades": "45",  "precio_unit": "2200", "vencimiento": "2026-11-20", "proveedor": "BioVet SRL"},
        {"id_producto": "PRD009", "nombre": "Omeprazol 20mg",          "categoria": "Gastrointestinal",  "unidades": "110", "precio_unit": "750",  "vencimiento": "2027-06-01", "proveedor": "MediAnimal"},
        {"id_producto": "PRD010", "nombre": "Metronidazol 250mg",      "categoria": "Antibiótico",       "unidades": "30",  "precio_unit": "900",  "vencimiento": "2026-08-10", "proveedor": "VetFarma SA"},
        {"id_producto": "PRD011", "nombre": "Prednisolona 5mg",        "categoria": "Corticoide",        "unidades": "75",  "precio_unit": "1350", "vencimiento": "2027-01-25", "proveedor": "BioVet SRL"},
        {"id_producto": "PRD012", "nombre": "Furosemida 40mg",         "categoria": "Diurético",         "unidades": "20",  "precio_unit": "680",  "vencimiento": "2026-07-30", "proveedor": "MediAnimal"},
        {"id_producto": "PRD013", "nombre": "Enalapril 5mg",           "categoria": "Cardiovascular",    "unidades": "55",  "precio_unit": "1500", "vencimiento": "2027-04-15", "proveedor": "VetFarma SA"},
        {"id_producto": "PRD014", "nombre": "Vitamina B12 inyectable", "categoria": "Suplemento",        "unidades": "40",  "precio_unit": "450",  "vencimiento": "2026-10-01", "proveedor": "BioVet SRL"},
        {"id_producto": "PRD015", "nombre": "Clorhexidina spray",      "categoria": "Antiséptico",       "unidades": "35",  "precio_unit": "2800", "vencimiento": "2027-02-20", "proveedor": "MediAnimal"},
        {"id_producto": "PRD016", "nombre": "Fenobarbital 30mg",       "categoria": "Anticonvulsivante", "unidades": "15",  "precio_unit": "3200", "vencimiento": "2026-09-05", "proveedor": "VetFarma SA"},
    ]

    todos = df.to_dict("records") + extras
    pipeline = r.pipeline()

    for prod in todos:
        key = f"stock:{prod['id_producto']}"
        pipeline.hset(key, mapping={
            "id_producto": prod["id_producto"],
            "nombre":      prod["nombre"],
            "categoria":   prod["categoria"],
            "unidades":    prod["unidades"],
            "precio_unit": prod["precio_unit"],
            "vencimiento": prod["vencimiento"],
            "proveedor":   prod["proveedor"],
        })
        # Set auxiliar con todos los IDs para poder listarlos
        pipeline.sadd("stock:ids", prod["id_producto"])

    pipeline.execute()
    print(f"✓ stock: {len(df)} CSV + {len(extras)} propios = {len(todos)} productos en Redis")


# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Cargando datos en Redis ===\n")
    limpiar_stock()
    cargar_stock()
    print("\n✅ Carga Redis completa\n")