import urllib.request
import re
import json
import os
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN DE PARTICIPACIONES REALES (CALIBRADAS CON LABORAL KUTXA)
# ==============================================================================
PARTICIPACIONES = {
    "LK_BU_FI": {
        "isin": "ES0164734032",
        "url": "https://www.quefondos.com/es/fondos/ficha/?isin=ES0164734032",
        "participaciones": 589.69,  # Ajustado al saldo real de 13.062,70 €
        "nombre": "LK Bolsa Universal FI"
    },
    "LK_BJ_FI": {
        "isin": "ES0115396030",
        "url": "https://www.quefondos.com/es/fondos/ficha/index.html?isin=ES0115396030",
        "participaciones": 414.95,  # Ajustado al saldo real de 13.687,24 €
        "nombre": "LK Bolsa Japón FI"
    }
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def get_valor_liquidativo(url):
    """Extrae el Valor Liquidativo de la ficha pública de QueFondos"""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Búsqueda principal en el HTML de QueFondos
            match = re.search(r'Valor liquidativo.*?>\s*([\d\.,]+)\s*EUR', html, re.IGNORECASE | re.DOTALL)
            if match:
                vl_str = match.group(1).replace('.', '').replace(',', '.')
                return float(vl_str)
            
            # Búsqueda secundaria en estructura alternativa
            match_alt = re.search(r'class="floatright">([\d\.,]+) EUR</span>', html)
            if match_alt:
                vl_str = match_alt.group(1).replace('.', '').replace(',', '.')
                return float(vl_str)

    except Exception as e:
        print(f"[ERROR Scraping {url}]: {e}")
    return None

def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Captura APEX LONG (Fondos Laboral Kutxa)...")
    
    total_fondos = 0.0
    resultados = {}
    
    for key, data in PARTICIPACIONES.items():
        vl = get_valor_liquidativo(data["url"])
        if vl is not None:
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
        else:
            print(f" -> [ADVERTENCIA] No se pudo obtener el VL para {data['nombre']}")

    total_fondos = round(total_fondos, 2)
    
    # Prevenir división por cero si falla el scraping
    peso_bj = round((resultados.get("LK_BJ_FI", {}).get("valor_total_eur", 0) / total_fondos) * 100, 2) if total_fondos > 0 else 0.0
    peso_bu = round((resultados.get("LK_BU_FI", {}).get("valor_total_eur", 0) / total_fondos) * 100, 2) if total_fondos > 0 else 0.0

    # 1. Guardar Estado Actual en JSON (fondos_lk.json)
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
    print(" -> Archivo 'fondos_lk.json' actualizado con exito.")

    # 2. Registrar en Histórico Diario (historial_fondos.json)
    historial = []
    if os.path.exists("historial_fondos.json"):
        try:
            with open("historial_fondos.json", "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception:
            historial = []

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    historial = [h for h in historial if h.get("fecha") != fecha_hoy]
    historial.append({
        "fecha": fecha_hoy,
        "lk_bj_val": resultados.get("LK_BJ_FI", {}).get("valor_total_eur", 0),
        "lk_bu_val": resultados.get("LK_BU_FI", {}).get("valor_total_eur", 0),
        "total_fondos": total_fondos
    })

    with open("historial_fondos.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4, ensure_ascii=False)
    print(" -> Archivo 'historial_fondos.json' actualizado.")

if __name__ == "__main__":
    main()
