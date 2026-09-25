import json
import urllib.request
from datetime import datetime

# PARTICIPACIONES BASE REALES (Extracto Bancario - Septiembre 2026)
PARTICIPACIONES_BASE = {
    "LK_JAPON": 850.700297,
    "LK_UNIVERSAL": 922.402920
}

# Aportación recurrente en euros cada día 12
APORTACION_MENSUAL_EUR = 120.0

# Fecha base del último extracto validado (Mes 9 = Septiembre, Año 2026)
FECHA_BASE_MES = 9
FECHA_BASE_ANIO = 2026

TICKERS = {
    "LK_JAPON": "0P0000A1A2.F",
    "LK_UNIVERSAL": "0P0000A1A4.F"
}

def obtener_vl_yahoo(ticker, vl_fallback):
    """Extrae el Valor Liquidativo en tiempo real o recurre al valor base."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
            valid_prices = [p for p in prices if p is not None]
            if valid_prices:
                return round(valid_prices[-1], 6)
    except Exception as e:
        print(f"Aviso en consulta de {ticker}: {e}")
    return vl_fallback

def calcular_participaciones_acumuladas(vl_japon, vl_universal):
    """Calcula las participaciones totales sumando 120€ por fondo tras cada día 12 transcurrido."""
    hoy = datetime.utcnow()
    
    # 1. Calcular meses transcurridos desde Septiembre 2026
    meses_transcurridos = (hoy.year - FECHA_BASE_ANIO) * 12 + (hoy.month - FECHA_BASE_MES)
    
    # Si aún no hemos llegado al día 12 del mes actual, ese mes no se computa todavía
    if hoy.day < 12 and meses_transcurridos > 0:
        meses_transcurridos -= 1
        
    meses_aportados = max(0, meses_transcurridos)
    
    # 2. Sumar el acumulado de aportaciones de 120€
    part_japon = PARTICIPACIONES_BASE["LK_JAPON"] + (meses_aportados * (APORTACION_MENSUAL_EUR / vl_japon))
    part_universal = PARTICIPACIONES_BASE["LK_UNIVERSAL"] + (meses_aportados * (APORTACION_MENSUAL_EUR / vl_universal))
    
    return round(part_japon, 6), round(part_universal, 6), meses_aportados

def main():
    # 1. Obtenemos Valores Liquidativos actualizados
    vl_japon = obtener_vl_yahoo(TICKERS["LK_JAPON"], 16.273146)
    vl_universal = obtener_vl_yahoo(TICKERS["LK_UNIVERSAL"], 14.548783)

    # 2. Calculamos participaciones con la regla del día 12
    part_japon, part_universal, meses_aportados = calcular_participaciones_acumuladas(vl_japon, vl_universal)

    # 3. Valoración total
    val_japon = round(part_japon * vl_japon, 2)
    val_universal = round(part_universal * vl_universal, 2)
    patrimonio_total = round(val_japon + val_universal, 2)

    data = {
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "patrimonio_total": patrimonio_total,
        "fondos": {
            "japon": {
                "nombre": "LK Bolsa Japón FI",
                "isin": "ES0115396030",
                "valor": val_japon,
                "vl": vl_japon,
                "participaciones": part_japon,
                "ytd_pct": 18.86
            },
            "universal": {
                "nombre": "LK Bolsa Universal FI",
                "isin": "ES0164734032",
                "valor": val_universal,
                "vl": vl_universal,
                "participaciones": part_universal,
                "ytd_pct": 11.44
            }
        }
    }

    with open("fondos_lk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Sincronización OK. Aportaciones extra sumadas: {meses_aportados}. Total Patrimonio: {patrimonio_total:.2f} €")

if __name__ == "__main__":
    main()
