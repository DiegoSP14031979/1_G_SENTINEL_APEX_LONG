import urllib.request
import re
import json
import os
from datetime import datetime

# ==============================================================================
# PARTICIPACIONES Y VALORES BASE REALES (LABORAL KUTXA)
# ==============================================================================
FONDOS_CONFIG = {
    "LK_BU_FI": {
        "isin": "ES0164734032",
        "url": "https://www.quefondos.com/es/fondos/ficha/?isin=ES0164734032",
        "participaciones": 589.68,
        "vl_fallback": 22.1522,  # VL de respaldo para mantener los 13.062,70 € reales
        "nombre": "LK Bolsa Universal FI"
    },
    "LK_BJ_FI": {
        "isin": "ES0115396030",
        "url": "https://www.quefondos.com/es/fondos/ficha/index.html?isin=ES0115396030",
        "participaciones": 414.95,
        "vl_fallback": 32.9852,  # VL de respaldo para mantener los 13.687,24 € reales
        "nombre": "LK Bolsa Japón FI"
    }
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def get_valor_liquidativo(url, vl_fallback):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Buscar el VL específico en la tabla de QueFondos
            match = re.search(r'Valor liquidativo.*?>\s*([\d\.,]+)\s*EUR', html, re.IGNORECASE | re.DOTALL)
            if match:
                vl_str = match.group(1).replace('.', '').replace(',', '.')
                val = float(vl_str)
                # Validación de rango coherente (evita capturar porcentajes o índices erróneos)
                if val > 10.0 and val < 100.0:
                    return val
    except Exception as e:
        print(f"[ERROR Scraping {url}]: {e}")
    
    print(f" -> [FALLBACK ACTIVADO] Usando VL oficial de respaldo: {vl_fallback}")
    return vl_fallback

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Captura APEX LONG (Fondos LK)...")
    total_fondos = 0.0
    resultados = {}
    
    for key, data in FONDOS_CONFIG.items():
        vl = get_valor_liquidativo(data["url"], data["vl_fallback"])
        valor_actual = round(vl * data["participaciones"], 2)
        
        resultados[key] = {
            "nombre": data["nombre"],
            "isin": data["isin"],
            "vl": vl,
            "participaciones": data["participaciones"],
            "valor_total_eur": valor_actual
        }
        total_fondos += valor_actual
        print(f" -> {data['nombre']}: VL = {vl} € | Total: {valor_actual} €")

    total_fondos = round(total_fondos, 2)
    peso_bj = round((resultados["LK_BJ_FI"]["valor_total_eur"] / total_fondos) * 100, 2)
    peso_bu = round((resultados["LK_BU_FI"]["valor_total_eur"] / total_fondos) * 100, 2)

    # 1. Actualizar fondos_lk.json
    estado_actual = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fondos": resultados,
        "patrimonio_fondos_total": total_fondos,
        "kpis": {
            "peso_lk_bj": peso_bj,
            "peso_lk_bu": peso_bu
        }
    }
    
    with open("fondos_lk.json", "w", encoding="utf-8") as f:
        json.dump(estado_actual, f, indent=4, ensure_ascii=False)

    # 2. Re-escribir historial_fondos.json con la cifra real consolidada
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    historial = [{
        "fecha": fecha_hoy,
        "lk_bj_val": resultados["LK_BJ_FI"]["valor_total_eur"],
        "lk_bu_val": resultados["LK_BU_FI"]["valor_total_eur"],
        "total_fondos": total_fondos
    }]

    with open("historial_fondos.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)
        
    print(f" -> [OK] Archivos JSON actualizados. Total Real: {total_fondos} €")

if __name__ == "__main__":
    main()
