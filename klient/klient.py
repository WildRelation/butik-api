import requests
import os

DATALAKE_URL = os.getenv("DATALAKE_URL", "https://misty-abnormally-educated.app.cloud.cbh.kth.se")


def hamta_kunder():
    svar = requests.get(f"{DATALAKE_URL}/api/kunder")
    svar.raise_for_status()
    return svar.json()


def hamta_produkter():
    svar = requests.get(f"{DATALAKE_URL}/api/produkter")
    svar.raise_for_status()
    return svar.json()


def hamta_ordrar():
    svar = requests.get(f"{DATALAKE_URL}/api/ordrar")
    svar.raise_for_status()
    return svar.json()


def skapa_kund(namn: str, email: str, telefon: str = None):
    svar = requests.post(f"{DATALAKE_URL}/api/kunder", json={
        "namn": namn,
        "email": email,
        "telefon": telefon
    })
    svar.raise_for_status()
    return svar.json()


def skapa_produkt(namn: str, pris: float, lagersaldo: int = 0):
    svar = requests.post(f"{DATALAKE_URL}/api/produkter", json={
        "namn": namn,
        "pris": pris,
        "lagersaldo": lagersaldo
    })
    svar.raise_for_status()
    return svar.json()


def skapa_order(kund_id: int, produkt_id: int, antal: int):
    svar = requests.post(f"{DATALAKE_URL}/api/ordrar", json={
        "kund_id": kund_id,
        "produkt_id": produkt_id,
        "antal": antal
    })
    svar.raise_for_status()
    return svar.json()


def radera_kund(kund_id: int):
    svar = requests.delete(f"{DATALAKE_URL}/api/kunder/{kund_id}")
    svar.raise_for_status()
    return svar.json()


if __name__ == "__main__":
    print("=== Hämtar kunder från datalaken ===")
    kunder = hamta_kunder()
    for k in kunder:
        print(f"  {k['id']}. {k['namn']} ({k['email']})")

    print("\n=== Hämtar produkter ===")
    produkter = hamta_produkter()
    for p in produkter:
        print(f"  {p['id']}. {p['namn']} — {p['pris']} kr (lager: {p['lagersaldo']})")

    print("\n=== Hämtar ordrar ===")
    ordrar = hamta_ordrar()
    for o in ordrar:
        print(f"  Order {o['id']}: {o['kund']} köpte {o['produkt']} x{o['antal']}")

    print("\n=== Skapar ny kund ===")
    ny = skapa_kund("Python Klient", "python@klient.se", "070-9999999")
    print(f"  Skapad: {ny}")

    print("\n=== Verifierar att kunden finns ===")
    kunder = hamta_kunder()
    print(f"  Antal kunder nu: {len(kunder)}")

    print("\n=== Raderar testkunden ===")
    radera_kund(ny["id"])
    print("  Raderad!")
