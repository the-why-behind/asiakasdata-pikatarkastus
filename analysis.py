"""Analyysilogiikka: datan valmistelu, laatu, RFM-segmentointi ja suositukset.

Kaikki funktiot toimivat ilman Streamlitiä, joten niitä voi testata erikseen.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEGMENT_ORDER = ["Parhaat asiakkaat", "Vakioasiakkaat", "Uudet asiakkaat", "Poistumisvaarassa", "Passiiviset", "Satunnaiset ostajat"]

SEGMENT_INFO = {
    "Parhaat asiakkaat": ("Ostaneet äskettäin ja usein", "VIP-/kanta-asiakasetu, ennakkomyynti", 0.05),
    "Vakioasiakkaat": ("Ostavat säännöllisesti", "Ristiinmyynti- ja suosittelukampanja", 0.08),
    "Uudet asiakkaat": ("Ostaneet äskettäin, mutta vasta vähän", "Toisen oston kannustin (onboarding-flow)", 0.10),
    "Poistumisvaarassa": ("Ostivat ennen usein, nyt hiljaista", "Win-back-flow: muistutus + etu", 0.15),
    "Passiiviset": ("Ostaneet harvoin ja kauan sitten", "Reaktivointi tai listan siivous", 0.05),
    "Satunnaiset ostajat": ("Ei selvää ostorytmiä", "Yleinen uutiskirje", 0.02),
}

TRUE_VALUES = {"true", "1", "yes", "y", "kyllä", "k", "x", "subscribed", "opted in", "on"}


# ---------- Sarakkeiden arvaus ----------

GUESS = {
    "customer": ["customer_unique_id", "customer_id", "sale_customer_id", "customer id", "customerid", "asiakas",
                 "asiakasnumero", "client", "external_id", "email", "sähköposti", "user"],
    "order": ["order_id", "order id", "sale_external_id", "invoice", "tilaus", "tilausnumero",
              "order number", "kuitti"],
    "date": ["order_date", "sale_date", "invoicedate", "order_purchase_timestamp", "purchase",
             "date", "päivä", "pvm", "created", "aika", "time"],
    "value": ["order_value", "total", "summa", "amount", "revenue", "arvo", "myynti", "value"],
    "status": ["order_status", "sale_state", "status", "tila", "tilauksen tila", "state"],
    "qty": ["quantity", "qty", "määrä", "kpl"],
    "price": ["price", "unit price", "unitprice", "hinta", "yksikköhinta"],
    "email": ["email", "e-mail", "sähköposti", "mail"],
    "consent": ["email_consent", "can_email", "consent", "lupa", "markkinointilupa", "subscribed",
                "accepts marketing", "opt"],
}


def guess_column(columns, kind: str):
    """Palauttaa todennäköisimmän sarakkeen nimen tai None."""
    lowered = {c: str(c).lower().strip() for c in columns}
    for key in GUESS[kind]:
        for col, low in lowered.items():
            if low == key:
                return col
    for key in GUESS[kind]:
        for col, low in lowered.items():
            if key in low:
                return col
    return None


# ---------- Usean tiedoston yhdistäminen ----------

def combine_tables(tables: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, list[str]]:
    """Yhdistää useita taulukoita yhteisten sarakkeiden perusteella.

    1. Päätauluksi valitaan taulu, jossa on asiakas-, päivämäärä- ja tilaussarake.
    2. Muut taulut liitetään siihen yhteisellä sarakkeella (esim. order_id).
    3. Jos liitettävässä taulussa avain toistuu (esim. useita maksuja per tilaus),
       rivit kootaan ensin: numerot summataan, muista otetaan ensimmäinen arvo.
    Palauttaa yhdistetyn taulun ja selkokielisen lokin.
    """
    if len(tables) == 1:
        return next(iter(tables.values())), []

    # 0. Samanmuotoiset tiedostot (esim. kuukausiviennit) pinotaan allekkain
    log = []
    groups: dict[tuple, list[str]] = {}
    for name, df in tables.items():
        groups.setdefault(tuple(sorted(map(str, df.columns))), []).append(name)
    stacked = {}
    for names_in_group in groups.values():
        if len(names_in_group) == 1:
            stacked[names_in_group[0]] = tables[names_in_group[0]]
        else:
            label = " + ".join(names_in_group)
            stacked[label] = pd.concat([tables[n] for n in names_in_group], ignore_index=True)
            log.append(f"Pinottu allekkain samanmuotoiset tiedostot: **{label}** "
                       f"({len(stacked[label]):,} riviä)".replace(",", " "))
    tables = stacked
    if len(tables) == 1:
        return next(iter(tables.values())), log

    def score(df):
        return sum(guess_column(df.columns, k) is not None for k in ("customer", "date", "order"))

    names = sorted(tables, key=lambda n: (score(tables[n]), len(tables[n])), reverse=True)
    main = names[0]
    merged = tables[main].copy()
    log.append(f"Päätaulu: **{main}** ({len(merged):,} riviä)".replace(",", " "))
    remaining = names[1:]
    progress = True
    while remaining and progress:
        progress = False
        for name in list(remaining):
            df = tables[name]
            shared = [c for c in df.columns if c in merged.columns]
            if not shared:
                continue
            # Avaimeksi sarake, joka on toisessa taulussa mahdollisimman yksilöivä
            key = max(shared, key=lambda c: (str(c).lower().endswith("id"),
                                             df[c].nunique() / max(len(df), 1)))
            extra = [c for c in df.columns if c not in merged.columns]
            if not extra:
                remaining.remove(name)
                continue
            part = df[[key] + extra]
            note = ""
            if part[key].duplicated().any():
                num = [c for c in extra if pd.api.types.is_numeric_dtype(part[c])]
                agg = {c: ("sum" if c in num else "first") for c in extra}
                part = part.groupby(key, as_index=False).agg(agg)
                note = " – toistuvat rivit koottiin (numerot summattiin)"
            merged = merged.merge(part, on=key, how="left")
            log.append(f"Liitetty **{name}** sarakkeella `{key}`{note}")
            remaining.remove(name)
            progress = True
    for name in remaining:
        log.append(f"Ei liitetty **{name}** – ei yhteistä saraketta")
    return merged, log


# ---------- Datan valmistelu ----------

def _to_number(s: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(s):
        return s.astype(float)
    cleaned = (s.astype(str).str.replace(" ", "", regex=False)
                .str.replace(" ", "", regex=False)
                .str.replace("€", "", regex=False))
    # Desimaalipilkku -> piste, jos pisteitä ei käytetä desimaaleina
    if cleaned.str.contains(",").mean() > cleaned.str.contains(r"\.").mean():
        cleaned = cleaned.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


DATE_FORMATS = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S",
                "%d.%m.%Y", "%d.%m.%Y %H:%M", "%d.%m.%Y %H:%M:%S",
                "%d/%m/%Y", "%d/%m/%Y %H:%M", "%m/%d/%Y", "%m/%d/%Y %H:%M"]


def _to_date(s: pd.Series) -> pd.Series:
    """Kokeilee yleisimmät muodot ja valitsee sen, joka tulkitsee eniten rivejä."""
    if pd.api.types.is_datetime64_any_dtype(s):
        return s.dt.tz_localize(None) if s.dt.tz is not None else s
    text = s.astype("string").str.strip()
    best, best_n = None, -1
    for fmt in DATE_FORMATS:
        parsed = pd.to_datetime(text, format=fmt, errors="coerce")
        if parsed.notna().sum() > best_n:
            best, best_n = parsed, parsed.notna().sum()
    if best_n >= 0.8 * text.notna().sum():
        return best
    fallback = pd.to_datetime(text, errors="coerce", format="mixed", utc=True).dt.tz_localize(None)
    return fallback if fallback.notna().sum() > best_n else best


def prepare_orders(raw: pd.DataFrame, customer: str, date: str, value: str | None = None,
                   qty: str | None = None, price: str | None = None,
                   order: str | None = None, cents: bool = False,
                   status: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Muuttaa minkä tahansa tilaus- tai rivitason viennin muotoon
    order_id, customer_id, order_date, order_value. Palauttaa myös siivousraportin."""
    n_raw = len(raw)
    df = pd.DataFrame({
        "customer_id": raw[customer].astype("string").str.strip()
                         .str.replace(r"\.0$", "", regex=True),
        "order_date": _to_date(raw[date]),
    })
    if value:
        df["line_value"] = _to_number(raw[value])
    else:
        df["line_value"] = _to_number(raw[qty]) * _to_number(raw[price])
    if cents:
        df["line_value"] = df["line_value"] / 100
    df["order_id"] = raw[order].astype(str) if order else pd.RangeIndex(n_raw).astype(str)

    # Jos summa-sarake on koko tilauksen summa toistettuna jokaisella rivillä
    # (esim. Custobarin sale_total), rivejä ei saa laskea yhteen.
    order_level = False
    if order and value:
        multi = df.groupby("order_id")["line_value"].agg(["size", "nunique"])
        multi = multi[multi["size"] > 1]
        order_level = len(multi) > 20 and (multi["nunique"] == 1).mean() > 0.95

    missing_cust = df["customer_id"].isna() | (df["customer_id"] == "") | \
        df["customer_id"].str.lower().isin(["nan", "none"])
    bad_date = df["order_date"].isna()
    bad_value = df["line_value"].isna() | (df["line_value"] <= 0)
    cancelled = pd.Series(False, index=df.index)
    if status:
        cancelled = raw[status].astype(str).str.lower().str.contains(
            "cancel|peru|refund|unavailable|void|hylät", regex=True)
    # Täsmälleen samat rivit kahteen kertaan = todennäköisesti tuplalataus
    duplicate = raw.duplicated(keep="first").reindex(df.index, fill_value=False)
    # Tilaukset tulevaisuudessa (yli vuorokausi nykyhetkestä)
    future = df["order_date"] > pd.Timestamp.now().normalize() + pd.Timedelta(days=1)
    keep = ~(missing_cust | bad_date | bad_value | cancelled | duplicate | future)

    report = {
        "rows": n_raw,
        "missing_customer": float(missing_cust.mean()) if n_raw else 0.0,
        "bad_date": float(bad_date.mean()) if n_raw else 0.0,
        "bad_value": float(bad_value.mean()) if n_raw else 0.0,
        "kept_rows": int(keep.sum()),
        "order_level_total": bool(order_level),
        "cancelled": float(cancelled.mean()) if n_raw else 0.0,
        "duplicate_rows": float(duplicate.mean()) if n_raw else 0.0,
        "future_date": float(future.mean()) if n_raw else 0.0,
    }
    df = df[keep]
    orders = (df.groupby("order_id", as_index=False)
                .agg(customer_id=("customer_id", "first"),
                     order_date=("order_date", "min"),
                     order_value=("line_value", "max" if order_level else "sum")))
    report["outliers"] = outlier_share(orders["order_value"])
    return orders, report


def outlier_share(values: pd.Series, k: float = 3.0) -> float:
    """Osuus tilauksista, joiden summa poikkeaa selvästi muista.
    Summat ovat yleensä vinosti jakautuneita, joten raja lasketaan logaritmeista
    (IQR-menetelmä, kerroin 3 = vain selvät poikkeamat)."""
    v = values[values > 0]
    if len(v) < 30:
        return 0.0
    logv = np.log10(v)
    q1, q3 = logv.quantile([0.25, 0.75])
    iqr = q3 - q1
    if iqr == 0:
        return 0.0
    return float(((logv < q1 - k * iqr) | (logv > q3 + k * iqr)).mean())


def prepare_customers(raw: pd.DataFrame, customer: str, email: str | None = None,
                      consent: str | None = None) -> pd.DataFrame:
    df = pd.DataFrame({"customer_id": raw[customer].astype("string").str.strip()
                                        .str.replace(r"\.0$", "", regex=True)})
    if email:
        e = raw[email].astype("string").str.strip().str.lower()
        df["email"] = e.where(e.str.contains("@", na=False))
    if consent:
        df["email_consent"] = raw[consent].astype(str).str.strip().str.lower().isin(TRUE_VALUES)
    return df[df["customer_id"].notna() & (df["customer_id"] != "")]


# ---------- Analyysit ----------

def reference_date(orders: pd.DataFrame) -> pd.Timestamp:
    """"Tänään" = viimeisin tilaus + 1 päivä, jotta vanhakin data toimii."""
    return orders["order_date"].max().normalize() + pd.Timedelta(days=1)


def data_quality(orders: pd.DataFrame, report: dict,
                 customers: pd.DataFrame | None = None) -> dict:
    checks, weights = {}, {}

    def add(name, value, w):
        checks[name], weights[name] = float(value), w

    add("Rivit ilman asiakastunnistetta", report["missing_customer"], 25)
    add("Virheellinen päivämäärä", report["bad_date"], 10)
    add("Palautukset tai virheelliset summat", report["bad_value"], 10)
    add("Tuplarivit (sama rivi kahdesti)", report.get("duplicate_rows", 0.0), 15)
    add("Päivämäärä tulevaisuudessa", report.get("future_date", 0.0), 10)
    add("Poikkeavan suuret tai pienet summat", report.get("outliers", 0.0), 10)
    if customers is not None and len(customers):
        add("Duplikaattiasiakkaat", customers["customer_id"].duplicated().mean(), 15)
        add("Ei yhtään ostoa", 1 - customers["customer_id"].isin(orders["customer_id"]).mean(), 10)
        if "email" in customers:
            add("Sähköposti puuttuu", customers["email"].isna().mean(), 15)
            em = customers["email"].dropna()
            if len(em):
                add("Sama sähköposti usealla asiakkaalla", em.duplicated().mean(), 10)
        if "email_consent" in customers:
            add("Ei markkinointilupaa", 1 - customers["email_consent"].mean(), 20)
    # Pisteytys:
    # 1) Ongelman koko: jo 20 %:n ongelma vie tarkistuksen koko painon, 2 % vie 10 %.
    # 2) Ongelmien määrä: jokainen löydetty ongelmatyyppi vähentää lisäksi 2 pistettä,
    #    koska monta erilaista virhettä kertoo tiedonkeruun prosessiongelmista.
    total_w = sum(weights.values())
    penalty = sum(min(1.0, 5 * checks[k]) * weights[k] for k in checks)
    n_issue_types = sum(v > 0 for v in checks.values())
    score = max(0, round(100 * (1 - penalty / total_w) - 2 * n_issue_types))
    grade = "Hyvä" if score >= 90 else "Kohtalainen" if score >= 75 else "Heikko"
    return {"score": score, "grade": grade, "issue_types": n_issue_types, "checks": checks}


def _score(series: pd.Series, higher_is_better: bool = True, ties: str = "first") -> pd.Series:
    """Pisteet 1–5 persentiilien perusteella; toimii myös pienellä datalla.
    ties="min": samanarvoiset saavat saman (alimman) pisteen – tärkeä ostokerroille,
    koska usein valtaosa asiakkaista on ostanut vain kerran."""
    pct = series.rank(method=ties, pct=True)
    if not higher_is_better:
        pct = 1 - pct + 1 / len(series)
    return np.ceil(pct * 5).clip(1, 5).astype(int)


def rfm(orders: pd.DataFrame, today: pd.Timestamp) -> pd.DataFrame:
    r = orders.groupby("customer_id").agg(
        recency=("order_date", lambda d: (today - d.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("order_value", "sum"),
    )
    r["R"] = _score(r["recency"], higher_is_better=False)
    r["F"] = _score(r["frequency"], ties="min")
    r["M"] = _score(r["monetary"])
    r["segment"] = [_segment(R, F) for R, F in zip(r["R"], r["F"])]
    return r


def _segment(R: int, F: int) -> str:
    if R >= 4 and F >= 4:
        return "Parhaat asiakkaat"
    if R >= 3 and F >= 3:
        return "Vakioasiakkaat"
    if R >= 4 and F <= 2:
        return "Uudet asiakkaat"
    if R <= 2 and F >= 3:
        return "Poistumisvaarassa"
    if R <= 2 and F <= 2:
        return "Passiiviset"
    return "Satunnaiset ostajat"


def segment_summary(r: pd.DataFrame, customers: pd.DataFrame | None = None,
                    conversion: dict | None = None) -> pd.DataFrame:
    conversion = conversion or {k: v[2] for k, v in SEGMENT_INFO.items()}
    df = r.copy()
    has_consent = customers is not None and "email_consent" in customers
    if has_consent:
        consent = customers.drop_duplicates("customer_id").set_index("customer_id")["email_consent"]
        df["email_consent"] = df.index.map(consent).fillna(False).astype(float)
    else:
        df["email_consent"] = 1.0
    df["aov"] = df["monetary"] / df["frequency"]
    s = df.groupby("segment").agg(
        asiakkaita=("monetary", "size"),
        liikevaihto=("monetary", "sum"),
        ostot_per_asiakas=("monetary", "mean"),
        keskiostos=("aov", "mean"),
        lupa_osuus=("email_consent", "mean"),
    )
    s["asiakas_osuus"] = s["asiakkaita"] / s["asiakkaita"].sum()
    s["lv_osuus"] = s["liikevaihto"] / s["liikevaihto"].sum()
    s["kuvaus"] = [SEGMENT_INFO[i][0] for i in s.index]
    s["toimenpide"] = [SEGMENT_INFO[i][1] for i in s.index]
    s["konversio"] = [conversion.get(i, 0) for i in s.index]
    # Potentiaali = tavoitettavat asiakkaat × konversio × yksi keskiostos
    s["potentiaali_eur"] = s["asiakkaita"] * s["lupa_osuus"] * s["konversio"] * s["keskiostos"]
    if not has_consent:
        s["lupa_osuus"] = np.nan
    return s.reindex([x for x in SEGMENT_ORDER if x in s.index])