import json
import urllib.request
from datetime import datetime

# Configuración Base (Participaciones a fecha 1 de Septiembre 2026)
PARTICIPACIONES_BASE = {
    "LK_JAPON": 1041.250,      # Base anterior a la aportación de Sep
    "LK_UNIVERSAL": 743.380    # Base anterior a la aportación de Sep
}

APORTACION_MENSUAL_EUR = 120.0  # 120 € el día 12 de cada mes por fondo

TICKERS = {
    "LK_JAPON": "0P0000A1A2.F",
    "LK_UNIVERSAL": "0P0000A1A4.F"
}

def obtener_vl_yahoo(ticker):
    """Extrae el Valor Liquidativo en tiempo real desde Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            prices = data['chart']['result'][0]['indicators']['quote'][0]['close']
            valid_prices = [p for p in prices if p is not None]
            if valid_prices:
                return round(valid_prices[-1], 4)
    except Exception as e:
        print(f"Error extrayendo {ticker}: {e}")
    return None

def calcular_participaciones_actuales(vl_japon, vl_universal):
    """Calcula el incremento de participaciones si ya se ha superado el día 12 del mes."""
    hoy = datetime.utcnow()
    
    part_japon = PARTICIPACIONES_BASE["LK_JAPON"]
    part_universal = PARTICIPACIONES_BASE["LK_UNIVERSAL"]
    
    # Si estamos en o después del día 12, sumamos las nuevas participaciones compradas con los 120 €
    if hoy.day >= 12:
        nuevas_part_japon = APORTACION_MENSUAL_EUR / vl_japon
        nuevas_part_universal = APORTACION_MENSUAL_EUR / vl_universal
        
        part_japon += nuevas_part_japon
        part_universal += nuevas_part_universal
        
    return round(part_japon, 3), round(part_universal, 3)

def main():
    # 1. Obtener Valores Liquidativos (o valores de respaldo)
    vl_japon = obtener_vl_yahoo(TICKERS["LK_JAPON"]) or 13.0000
    vl_universal = obtener_vl_yahoo(TICKERS["LK_UNIVERSAL"]) or 17.5614

    # 2. Recalcular participaciones según la regla del día 12
    part_japon, part_universal = calcular_participaciones_actuales(vl_japon, vl_universal)

    # 3. Valoración total de la cartera
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

    print(f"Sincronización OK. Día {datetime.utcnow().day}. Participaciones -> Japón: {part_japon}, Universal: {part_universal}. Total: {patrimonio_total:.2f} €")

if __name__ == "__main__":
    main()
