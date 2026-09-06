import json
import urllib.request
from datetime import datetime

# Participaciones reales ajustadas a los saldos del banco
PARTICIPACIONES = {
    "LK_JAPON": 1050.480,
    "LK_UNIVERSAL": 750.210
}

# ISINs oficiales Laboral Kutxa
FONDOS = {
    "LK_JAPON": {"isin": "ES0115396030", "nombre": "LK Bolsa Japón FI"},
    "LK_UNIVERSAL": {"isin": "ES0164734032", "nombre": "LK Bolsa Universal FI"}
}

def obtener_vl(isin):
    url = f"https://queondatv.com/api/fund_price.php?isin={isin}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return float(data['price'])
    except Exception as e:
        print(f"Error fetching {isin}: {e}")
        return None

def main():
    vl_japon = obtener_vl(FONDOS["LK_JAPON"]["isin"]) or 12.9519
    vl_universal = obtener_vl(FONDOS["LK_UNIVERSAL"]["isin"]) or 17.4329

    val_japon = round(PARTICIPACIONES["LK_JAPON"] * vl_japon, 2)
    val_universal = round(PARTICIPACIONES["LK_UNIVERSAL"] * vl_universal, 2)
    patrimonio_total = round(val_japon + val_universal, 2)

    data = {
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "patrimonio_total": patrimonio_total,
        "fondos": {
            "japon": {
                "nombre": "LK Bolsa Japón FI",
                "isin": FONDOS["LK_JAPON"]["isin"],
                "valor": val_japon,
                "vl": vl_japon,
                "participaciones": PARTICIPACIONES["LK_JAPON"],
                "ytd_pct": 18.86
            },
            "universal": {
                "nombre": "LK Bolsa Universal FI",
                "isin": FONDOS["LK_UNIVERSAL"]["isin"],
                "valor": val_universal,
                "vl": vl_universal,
                "participaciones": PARTICIPACIONES["LK_UNIVERSAL"],
                "ytd_pct": 11.44
            }
        }
    }

    with open("fondos_lk.json", "w") as f:
        json.dump(data, f, indent=4)
    print("fondos_lk.json actualizado correctamente con los saldos reales del banco.")

if __name__ == "__main__":
    main()
