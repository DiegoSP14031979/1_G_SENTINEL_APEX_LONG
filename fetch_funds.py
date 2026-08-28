import json
import os
from datetime import datetime

# ==============================================================================
# FONDOS LABORAL KUTXA - VALORACIÓN Y PARTICIPACIONES EXACTAS
# ==============================================================================
FONDOS_CONFIG = {
    "LK_BU_FI": {
        "nombre": "LK Bolsa Universal FI",
        "isin": "ES0164734032",
        "vl": 22.1522,
        "participaciones": 589.68,
        "valor_total_eur": 13062.70
    },
    "LK_BJ_FI": {
        "nombre": "LK Bolsa Japón FI",
        "isin": "ES0115396030",
        "vl": 32.9852,
        "participaciones": 414.95,
        "valor_total_eur": 13687.24
    }
}

def main():
    timestamp_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp_actual}] Generando consolidación APEX LONG...")

    val_bu = FONDOS_CONFIG["LK_BU_FI"]["valor_total_eur"]
    val_bj = FONDOS_CONFIG["LK_BJ_FI"]["valor_total_eur"]
    total_fondos = round(val_bu + val_bj, 2)

    peso_bj = round((val_bj / total_fondos) * 100, 2)
    peso_bu = round((val_bu / total_fondos) * 100, 2)

    # 1. Guardar Estado Actual en fondos_lk.json
    estado_actual = {
        "timestamp": timestamp_actual,
        "fondos": FONDOS_CONFIG,
        "patrimonio_fondos_total": total_fondos,
        "kpis": {
            "peso_lk_bj": peso_bj,
            "peso_lk_bu": peso_bu
        }
    }

    with open("fondos_lk.json", "w", encoding="utf-8") as f:
        json.dump(estado_actual, f, indent=4, ensure_ascii=False)

    # 2. Cargar y Actualizar historial_fondos.json manteniendo el pasado
    historial = []
    if os.path.exists("historial_fondos.json"):
        try:
            with open("historial_fondos.json", "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception as e:
            print(f"[ADVERTENCIA] Error leyendo historial existente: {e}")
            historial = []

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    
    # Reemplazar la entrada de hoy si ya existe para evitar duplicados en el mismo dia
    historial = [h for h in historial if h.get("fecha") != fecha_hoy]

    # Añadir el registro del dia actual
    historial.append({
        "fecha": fecha_hoy,
        "lk_bj_val": val_bj,
        "lk_bu_val": val_bu,
        "total_fondos": total_fondos
    })

    with open("historial_fondos.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)

    print(f" -> [OK] Proceso completado. Patrimonio Total Real: {total_fondos} €")

if __name__ == "__main__":
    main()
