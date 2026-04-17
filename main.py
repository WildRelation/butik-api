from fastapi import FastAPI, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pg_database import get_pg, init_pg, seed_pg
import os

DUCKLAKE_ENABLED = bool(os.getenv("CATALOG_PATH"))

if DUCKLAKE_ENABLED:
    from database import get_conn, init_db
    init_db()

app = FastAPI(title="Butik API")

init_pg()
seed_pg()

NAV = '<a href="/">← Tillbaka</a>'
STYLE = """
<style>
  body { font-family: Arial, sans-serif; max-width: 960px; margin: 60px auto; background: #f0f4f8; color: #333; }
  h1, h2 { color: #2c7a7b; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 12px;
          overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 16px; }
  th { background: #2c7a7b; color: white; padding: 12px; text-align: left; }
  td { padding: 10px 12px; border-bottom: 1px solid #eee; }
  a { color: #2c7a7b; }
  .card { background: white; border-radius: 12px; padding: 30px;
          box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-bottom: 24px; }
  nav a { margin-right: 16px; font-weight: bold; }
  .badge { background: #2c7a7b; color: white; padding: 2px 10px; border-radius: 20px;
           font-size: 0.8rem; margin-left: 8px; vertical-align: middle; }
  form { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; align-items: flex-end; }
  input, select { padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 0.95rem; }
  label { font-size: 0.85rem; color: #555; display: block; margin-bottom: 2px; }
  .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 0.95rem; }
  .btn-add  { background: #2c7a7b; color: white; }
  .btn-del  { background: #e53e3e; color: white; padding: 4px 10px; font-size: 0.85rem; }
  .btn-edit { background: #d69e2e; color: white; padding: 4px 10px; font-size: 0.85rem; }
</style>
"""


def page(title: str, body: str) -> str:
    return f"<!DOCTYPE html><html lang='sv'><head><meta charset='UTF-8'><title>{title}</title>{STYLE}</head><body>{body}</body></html>"


def redirect(url: str):
    return RedirectResponse(url=url, status_code=303)


@app.get("/", response_class=HTMLResponse)
async def index():
    ducklake_section = """
        <h3>DuckLake <span class='badge'>Parquet</span></h3>
        <nav>
            <a href='/kunder'>Kunder</a>
            <a href='/produkter'>Produkter</a>
            <a href='/ordrar'>Ordrar</a>
            <a href='/snapshots'>Snapshots</a>
        </nav><br>
    """ if DUCKLAKE_ENABLED else ""
    return page("Butik", f"""
        <div class='card'>
            <h1>Välkommen till Butik-API</h1>
            {ducklake_section}
            <h3>PostgreSQL <span class='badge'>KTH Cloud</span></h3>
            <nav>
                <a href='/pg/kunder'>Kunder</a>
                <a href='/pg/produkter'>Produkter</a>
                <a href='/pg/ordrar'>Ordrar</a>
            </nav><br>
            <a href='/docs'>API-dokumentation</a>
        </div>
    """)


# ── KUNDER ────────────────────────────────────────────────────────────────────

@app.get("/pg/kunder", response_class=HTMLResponse)
async def pg_kunder(db: Session = Depends(get_pg)):
    rows = db.execute(text("SELECT id, namn, email, telefon FROM kunder ORDER BY id")).fetchall()
    rader = "".join(f"""
        <tr>
            <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3] or ''}</td>
            <td>
                <form method='post' action='/pg/kunder/{r[0]}/radera' style='display:inline'>
                    <button class='btn btn-del'>Ta bort</button>
                </form>
            </td>
        </tr>""" for r in rows)
    return page("Kunder", f"""
        <h1>Kunder <span class='badge'>PostgreSQL</span></h1>{NAV}
        <div class='card'>
            <h2>Lägg till kund</h2>
            <form method='post' action='/pg/kunder/ny'>
                <div><label>Namn</label><input name='namn' required></div>
                <div><label>E-post</label><input name='email' type='email' required></div>
                <div><label>Telefon</label><input name='telefon'></div>
                <button class='btn btn-add'>Lägg till</button>
            </form>
        </div>
        <table>
            <tr><th>ID</th><th>Namn</th><th>E-post</th><th>Telefon</th><th></th></tr>
            {rader}
        </table>
    """)


@app.post("/pg/kunder/ny")
async def ny_kund(namn: str = Form(...), email: str = Form(...), telefon: str = Form(""), db: Session = Depends(get_pg)):
    db.execute(text("INSERT INTO kunder (namn, email, telefon) VALUES (:namn, :email, :telefon)"),
               {"namn": namn, "email": email, "telefon": telefon or None})
    db.commit()
    return redirect("/pg/kunder")


@app.post("/pg/kunder/{kund_id}/radera")
async def radera_kund(kund_id: int, db: Session = Depends(get_pg)):
    db.execute(text("DELETE FROM ordrar WHERE kund_id = :id"), {"id": kund_id})
    db.execute(text("DELETE FROM kunder WHERE id = :id"), {"id": kund_id})
    db.commit()
    return redirect("/pg/kunder")


# ── PRODUKTER ─────────────────────────────────────────────────────────────────

@app.get("/pg/produkter", response_class=HTMLResponse)
async def pg_produkter(db: Session = Depends(get_pg)):
    rows = db.execute(text("SELECT id, namn, pris, lagersaldo FROM produkter ORDER BY id")).fetchall()
    rader = "".join(f"""
        <tr>
            <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]:.2f} kr</td><td>{r[3]}</td>
            <td>
                <form method='post' action='/pg/produkter/{r[0]}/radera' style='display:inline'>
                    <button class='btn btn-del'>Ta bort</button>
                </form>
            </td>
        </tr>""" for r in rows)
    return page("Produkter", f"""
        <h1>Produkter <span class='badge'>PostgreSQL</span></h1>{NAV}
        <div class='card'>
            <h2>Lägg till produkt</h2>
            <form method='post' action='/pg/produkter/ny'>
                <div><label>Namn</label><input name='namn' required></div>
                <div><label>Pris (kr)</label><input name='pris' type='number' step='0.01' required></div>
                <div><label>Lagersaldo</label><input name='lagersaldo' type='number' value='0'></div>
                <button class='btn btn-add'>Lägg till</button>
            </form>
        </div>
        <table>
            <tr><th>ID</th><th>Namn</th><th>Pris</th><th>Lagersaldo</th><th></th></tr>
            {rader}
        </table>
    """)


@app.post("/pg/produkter/ny")
async def ny_produkt(namn: str = Form(...), pris: float = Form(...), lagersaldo: int = Form(0), db: Session = Depends(get_pg)):
    db.execute(text("INSERT INTO produkter (namn, pris, lagersaldo) VALUES (:namn, :pris, :lagersaldo)"),
               {"namn": namn, "pris": pris, "lagersaldo": lagersaldo})
    db.commit()
    return redirect("/pg/produkter")


@app.post("/pg/produkter/{produkt_id}/radera")
async def radera_produkt(produkt_id: int, db: Session = Depends(get_pg)):
    db.execute(text("DELETE FROM ordrar WHERE produkt_id = :id"), {"id": produkt_id})
    db.execute(text("DELETE FROM produkter WHERE id = :id"), {"id": produkt_id})
    db.commit()
    return redirect("/pg/produkter")


# ── ORDRAR ────────────────────────────────────────────────────────────────────

@app.get("/pg/ordrar", response_class=HTMLResponse)
async def pg_ordrar(db: Session = Depends(get_pg)):
    rows = db.execute(text("""
        SELECT o.id, k.namn, p.namn, o.antal, o.skapad
        FROM ordrar o
        JOIN kunder k ON k.id = o.kund_id
        JOIN produkter p ON p.id = o.produkt_id
        ORDER BY o.id
    """)).fetchall()
    kunder = db.execute(text("SELECT id, namn FROM kunder ORDER BY namn")).fetchall()
    produkter = db.execute(text("SELECT id, namn FROM produkter ORDER BY namn")).fetchall()

    rader = "".join(f"""
        <tr>
            <td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{str(r[4])[:16]}</td>
            <td>
                <form method='post' action='/pg/ordrar/{r[0]}/radera' style='display:inline'>
                    <button class='btn btn-del'>Ta bort</button>
                </form>
            </td>
        </tr>""" for r in rows)

    kund_options = "".join(f"<option value='{k[0]}'>{k[1]}</option>" for k in kunder)
    produkt_options = "".join(f"<option value='{p[0]}'>{p[1]}</option>" for p in produkter)

    return page("Ordrar", f"""
        <h1>Ordrar <span class='badge'>PostgreSQL</span></h1>{NAV}
        <div class='card'>
            <h2>Lägg till order</h2>
            <form method='post' action='/pg/ordrar/ny'>
                <div><label>Kund</label><select name='kund_id'>{kund_options}</select></div>
                <div><label>Produkt</label><select name='produkt_id'>{produkt_options}</select></div>
                <div><label>Antal</label><input name='antal' type='number' value='1' min='1' required></div>
                <button class='btn btn-add'>Lägg till</button>
            </form>
        </div>
        <table>
            <tr><th>ID</th><th>Kund</th><th>Produkt</th><th>Antal</th><th>Datum</th><th></th></tr>
            {rader}
        </table>
    """)


@app.post("/pg/ordrar/ny")
async def ny_order(kund_id: int = Form(...), produkt_id: int = Form(...), antal: int = Form(...), db: Session = Depends(get_pg)):
    db.execute(text("INSERT INTO ordrar (kund_id, produkt_id, antal) VALUES (:kund_id, :produkt_id, :antal)"),
               {"kund_id": kund_id, "produkt_id": produkt_id, "antal": antal})
    db.commit()
    return redirect("/pg/ordrar")


@app.post("/pg/ordrar/{order_id}/radera")
async def radera_order(order_id: int, db: Session = Depends(get_pg)):
    db.execute(text("DELETE FROM ordrar WHERE id = :id"), {"id": order_id})
    db.commit()
    return redirect("/pg/ordrar")


# ── DUCKLAKE (valfri) ─────────────────────────────────────────────────────────

@app.get("/kunder", response_class=HTMLResponse)
async def visa_kunder():
    con = get_conn()
    rows = con.execute("SELECT id, namn, email, telefon FROM butik.kunder ORDER BY id").fetchall()
    con.close()
    rader = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>" for r in rows)
    return page("Kunder", f"<h1>Kunder</h1>{NAV}<table><tr><th>ID</th><th>Namn</th><th>E-post</th><th>Telefon</th></tr>{rader}</table>")


@app.get("/produkter", response_class=HTMLResponse)
async def visa_produkter():
    con = get_conn()
    rows = con.execute("SELECT id, namn, pris, lagersaldo FROM butik.produkter ORDER BY id").fetchall()
    con.close()
    rader = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]:.2f} kr</td><td>{r[3]}</td></tr>" for r in rows)
    return page("Produkter", f"<h1>Produkter</h1>{NAV}<table><tr><th>ID</th><th>Namn</th><th>Pris</th><th>Lagersaldo</th></tr>{rader}</table>")


@app.get("/ordrar", response_class=HTMLResponse)
async def visa_ordrar():
    con = get_conn()
    rows = con.execute("""
        SELECT o.id, k.namn, p.namn, o.antal, o.skapad
        FROM butik.ordrar o
        JOIN butik.kunder k ON k.id = o.kund_id
        JOIN butik.produkter p ON p.id = o.produkt_id
        ORDER BY o.id
    """).fetchall()
    con.close()
    rader = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td>{str(r[4])[:16]}</td></tr>" for r in rows)
    return page("Ordrar", f"<h1>Ordrar</h1>{NAV}<table><tr><th>ID</th><th>Kund</th><th>Produkt</th><th>Antal</th><th>Datum</th></tr>{rader}</table>")


@app.get("/snapshots", response_class=HTMLResponse)
async def visa_snapshots():
    con = get_conn()
    rows = con.execute("""
        SELECT snapshot_id, snapshot_time, schema_version, changes
        FROM ducklake_snapshots('butik')
        ORDER BY snapshot_id DESC
        LIMIT 50
    """).fetchall()
    con.close()
    rader = "".join(
        f"<tr><td>{r[0]}</td><td>{str(r[1])[:19]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
        for r in rows
    )
    return page("Snapshots", f"""
        <h1>Snapshots <span class='badge'>Time Travel</span></h1>{NAV}
        <p>Varje skrivoperation skapar en snapshot — du kan läsa historiska versioner.</p>
        <table>
            <tr><th>Snapshot ID</th><th>Tidpunkt</th><th>Schema-version</th><th>Ändringar</th></tr>
            {rader}
        </table>
    """)
