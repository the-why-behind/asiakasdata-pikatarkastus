"""Luo realistisen testidatan suomalaiselle sisustus- ja lahjatavaraketjulle
Custobarin CSV-vientimuodossa (summat sentteinä, rivitasoinen myyntidata).

Ajo:  python3 tools/generate_custobar_data.py
Tulos: data/custobar_sales.csv ja data/custobar_customers.csv (sovelluksen esimerkkidata)

Kaikki data on kuvitteellista. Mukana tarkoituksella todellisen elämän ongelmia:
- myymäläostot ilman asiakastunnistetta (ei kanta-asiakaskorttia)
- sama henkilö kahdella asiakasnumerolla (verkko + myymälä)
- puuttuvat sähköpostit ja markkinointiluvat
- palautukset negatiivisina riveinä
"""
from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

START, END = pd.Timestamp("2023-11-24"), pd.Timestamp("2026-11-23")
N_CUSTOMERS = 8000

SHOPS = ["Verkkokauppa", "Helsinki Kamppi", "Espoo Iso Omena", "Tampere Ratina",
         "Turku Hansa", "Oulu Valkea"]
SHOP_P = [0.42, 0.18, 0.12, 0.11, 0.09, 0.08]
CITIES = ["Helsinki", "Espoo", "Vantaa", "Tampere", "Turku", "Oulu", "Jyväskylä", "Lahti", "Kuopio"]
CITY_P = [0.24, 0.13, 0.09, 0.14, 0.11, 0.09, 0.07, 0.07, 0.06]

PRODUCTS = pd.DataFrame({
    "product_id": [f"SKU{i:04d}" for i in range(1, 41)],
    "category": (["Astiat"] * 10 + ["Kynttilät"] * 6 + ["Tekstiilit"] * 8
                 + ["Sisustus"] * 10 + ["Joulu"] * 6),
    "unit_price": np.concatenate([
        rng.integers(1490, 6990, 10), rng.integers(590, 2490, 6), rng.integers(1990, 8990, 8),
        rng.integers(2490, 14990, 10), rng.integers(990, 3990, 6)]),  # sentteinä
})

# --- Kausivaihtelu: joulu, äitienpäivä, Black Friday ---
days = pd.date_range(START, END, freq="D")
weight = np.ones(len(days))
weight[(days.month == 12) & (days.day <= 23)] *= 3.2
weight[(days.month == 11) & (days.day >= 20)] *= 2.4          # Black Friday -viikko
weight[(days.month == 5) & (days.day <= 12)] *= 1.8           # äitienpäivä
weight[days.month.isin([1, 7])] *= 0.7
weight[days.day_of_week >= 5] *= 1.3
weight /= weight.sum()

# --- Asiakkaat ---
cust = pd.DataFrame({"external_id": [f"K{100000 + i}" for i in range(N_CUSTOMERS)]})
cust["loyalty"] = rng.random(N_CUSTOMERS) < 0.55
cust["web_only"] = rng.random(N_CUSTOMERS) < 0.30
cust["city"] = rng.choice(CITIES, N_CUSTOMERS, p=CITY_P)
cust["zip_code"] = [f"{rng.integers(0, 99):02d}{rng.integers(0, 9)}{rng.integers(0, 9)}0" for _ in range(N_CUSTOMERS)]
# Aktiivisuusprofiili: osa ostaa paljon, osa kerran ja katoaa
activity = rng.lognormal(mean=0.6, sigma=0.9, size=N_CUSTOMERS) * np.where(cust["loyalty"], 1.8, 1.0)
cust["n_tx"] = np.clip(np.round(activity), 1, 60).astype(int)
# Ostoskorin koko vaihtelee asiakkaittain: aktiiviset ja kanta-asiakkaat ostavat isompia koreja
cust["basket"] = (rng.lognormal(0, 0.35, N_CUSTOMERS)
                  * (1 + 0.12 * np.log1p(cust["n_tx"]))
                  * np.where(cust["loyalty"], 1.15, 1.0))
# Elinkaari: milloin asiakas aloitti ja lopetti
first_idx = rng.integers(0, len(days) - 30, N_CUSTOMERS)
churned = rng.random(N_CUSTOMERS) < 0.45
life = np.where(churned, rng.integers(30, 500, N_CUSTOMERS), len(days))
last_idx = np.minimum(first_idx + life, len(days) - 1)

cust["date_joined"] = days[first_idx]
cust["email"] = cust["external_id"].str.lower() + "@esimerkki.fi"
no_email = (~cust["web_only"]) & (rng.random(N_CUSTOMERS) < 0.25)   # myymäläasiakkailla puuttuu usein
cust.loc[no_email, "email"] = None
cust["can_email"] = np.where(cust["email"].isna(), False,
                             rng.random(N_CUSTOMERS) < np.where(cust["loyalty"], 0.72, 0.38))
cust["can_sms"] = rng.random(N_CUSTOMERS) < np.where(cust["loyalty"], 0.35, 0.08)
cust["kanta_asiakas"] = cust["loyalty"]

# --- Transaktiot ---
rows, sale_no = [], 500000
for i, c in cust.iterrows():
    span = days[first_idx[i]: last_idx[i] + 1]
    w = weight[first_idx[i]: last_idx[i] + 1]
    dates = rng.choice(span, size=c.n_tx, p=w / w.sum())
    for d in sorted(dates):
        sale_no += 1
        shop = "Verkkokauppa" if c.web_only else rng.choice(SHOPS, p=SHOP_P)
        n_lines = int(np.clip(round(rng.choice([1, 1, 1, 2, 2, 3, 4]) * c.basket), 1, 8))
        prods = PRODUCTS.sample(n_lines, random_state=int(rng.integers(1e9)))
        if pd.Timestamp(d).month != 12:
            prods = prods[prods["category"] != "Joulu"] if (prods["category"] != "Joulu").any() else prods
        ts = pd.Timestamp(d) + pd.Timedelta(minutes=int(rng.integers(9 * 60, 21 * 60)))
        for j, p in enumerate(prods.itertuples()):
            q = int(rng.choice([1, 1, 1, 2, 2, 4]))
            rows.append((f"S{sale_no}", ts, c.external_id, shop, f"S{sale_no}-{j + 1}",
                         p.product_id, q, int(p.unit_price), q * int(p.unit_price)))

# Anonyymit myymäläostot (ei kanta-asiakaskorttia) – tyypillisesti iso osa myymälämyynnistä
n_anon = int(len({r[0] for r in rows}) * 0.38)
for _ in range(n_anon):
    sale_no += 1
    d = pd.Timestamp(rng.choice(days, p=weight)) + pd.Timedelta(minutes=int(rng.integers(540, 1260)))
    shop = rng.choice(SHOPS[1:], p=np.array(SHOP_P[1:]) / sum(SHOP_P[1:]))
    p = PRODUCTS.iloc[int(rng.integers(len(PRODUCTS)))]
    q = int(rng.choice([1, 1, 2]))
    rows.append((f"S{sale_no}", d, None, shop, f"S{sale_no}-1", p.product_id, q,
                 int(p.unit_price), q * int(p.unit_price)))

sales = pd.DataFrame(rows, columns=["sale_external_id", "sale_date", "sale_customer_id", "sale_shop",
                                    "external_id", "product_id", "quantity", "unit_price", "total"])

# Palautukset: 3 % riveistä palautetaan myöhemmin negatiivisena rivinä
ret = sales[sales["sale_customer_id"].notna()].sample(frac=0.03, random_state=1).copy()
ret["sale_external_id"] = "R" + ret["sale_external_id"].str[1:]
ret["external_id"] = "R" + ret["external_id"].str[1:]
ret["sale_date"] = ret["sale_date"] + pd.to_timedelta(rng.integers(2, 20, len(ret)), unit="D")
ret["quantity"] *= -1
ret["total"] *= -1
ret = ret[ret["sale_date"] <= END]
sales = pd.concat([sales, ret], ignore_index=True)

# Sama henkilö kahdella asiakasnumerolla: 4 % asiakkaista saa myymälässä uuden numeron
dupe_src = cust[cust["email"].notna() & ~cust["web_only"]].sample(frac=0.06, random_state=2)
dupes = dupe_src.copy()
dupes["external_id"] = ["K" + str(900000 + k) for k in range(len(dupes))]
dupes["can_email"] = False
for old, new in zip(dupe_src["external_id"], dupes["external_id"]):
    idx = sales.index[sales["sale_customer_id"] == old]
    move = idx[rng.random(len(idx)) < 0.4]
    sales.loc[move, "sale_customer_id"] = new
cust = pd.concat([cust, dupes], ignore_index=True)

# sale_total = koko kuitin summa jokaisella rivillä (kuten Custobarissa)
sales["sale_total"] = sales.groupby("sale_external_id")["total"].transform("sum")
sales["sale_date"] = sales["sale_date"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
sales = sales.sort_values("sale_date")[
    ["sale_external_id", "sale_date", "sale_customer_id", "sale_shop", "sale_total",
     "external_id", "product_id", "quantity", "unit_price", "total"]]

customers = cust[["external_id", "email", "city", "zip_code", "date_joined",
                  "can_email", "can_sms", "kanta_asiakas"]].copy()
customers["date_joined"] = pd.to_datetime(customers["date_joined"]).dt.strftime("%Y-%m-%d")
customers = customers.sample(frac=1, random_state=3)

sales.to_csv(OUT / "custobar_sales.csv", index=False)
customers.to_csv(OUT / "custobar_customers.csv", index=False)
n_tx = sales["sale_external_id"].nunique()
print(f"Myyntirivejä {len(sales):,}, kuitteja {n_tx:,}, asiakkaita {len(customers):,}")
print(f"Liikevaihto {sales['total'].sum() / 100:,.0f} €")
print(f"Kuitit ilman asiakasta: {sales.drop_duplicates('sale_external_id')['sale_customer_id'].isna().mean():.0%}")