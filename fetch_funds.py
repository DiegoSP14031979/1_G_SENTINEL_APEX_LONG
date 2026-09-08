import json
from datetime import datetime

# Participaciones exactas según tu extracto bancario de Laboral Kutxa
PARTICIPACIONES = {
    "LK_JAPON": 1050.480,
    "LK_UNIVERSAL": 750.210
}

# Valores Liquidativos (VL) de cierre de mercado
VALORES_LIQUIDATIVOS = {
    "LK_JAPON": 13.0000,
    "LK_UNIVERSAL": 17.5614
}

def main():
    val_japon = round(PARTICIPACIONES["LK_JAPON"] * VALORES_LIQUIDATIVOS["LK_JAPON"], 2)
    val_universal = round(PARTICIPACIONES["LK_UNIVERSAL"] * VALORES_LIQUIDATIVOS["LK_UNIVERSAL"], 2)
    patrimonio_total = round(val_japon + val_universal, 2)

    data = {
        "updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "patrimonio_total": patrimonio_total,
        "fondos": {
            "japon": {
                "nombre": "LK Bolsa Japón FI",
                "isin": "ES0115396030",
                "valor": val_japon,
                "vl": VALORES_LIQUIDATIVOS["LK_JAPON"],
                "participaciones": PARTICIPACIONES["LK_JAPON"],
                "ytd_pct": 18.86
            },
            "universal": {
                "nombre": "LK Bolsa Universal FI",
                "isin": "ES0164734032",
                "valor": val_universal,
                "vl": VALORES_LIQUIDATIVOS["LK_UNIVERSAL"],
                "participaciones": PARTICIPACIONES["LK_UNIVERSAL"],
                "ytd_pct": 11.44
            }
        }
    }

    with open("fondos_lk.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"fondos_lk.json actualizado a {patrimonio_total:.2f} € exitosamente.")

if __name__ == "__main__":
    main()
