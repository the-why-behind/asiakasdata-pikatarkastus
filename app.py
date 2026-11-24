"""Asiakasdatan pikatarkastus – Streamlit-sovellus.

Ajo:  streamlit run app.py
"""
from io import BytesIO
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from analysis import (SEGMENT_INFO, SEGMENT_ORDER, combine_tables, data_quality, guess_column,
                      prepare_customers, prepare_orders, reference_date, rfm,
                      segment_summary)

DATA = Path(__file__).parent / "data"
NONE = "— ei valittu —"

st.set_page_config(page_title="Asiakasdatan pikatarkastus", page_icon="📊", layout="wide")


# ---------- Apufunktiot ----------

@st.cache_data(show_spinner="Luetaan tiedostoa…")
def read_file(name: str, content: bytes) -> pd.DataFrame:
    if name.lower().endswith(".xlsx"):
        sheets = pd.read_excel(BytesIO(content), sheet_name=None)
        frames = list(sheets.values())
        same = all(list(f.columns) == list(frames[0].columns) for f in frames)
        return pd.concat(frames, ignore_index=True) if same else frames[0]
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(BytesIO(content), sep=None, engine="python", encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Tiedoston merkistöä ei tunnistettu.")


@st.cache_data(show_spinner="Yhdistetään tiedostoja…")
def read_and_combine(files: tuple) -> tuple[pd.DataFrame, list]:
    tables = {name: read_file(name, content) for name, content in files}
    return combine_tables(tables)


def pick(label: str, columns, kind: str | None, key: str, optional: bool = False, help=None):
    options = ([NONE] if optional else []) + list(columns)
    guess = guess_column(columns, kind) if kind else None
    index = options.index(guess) if guess in options else 0
    choice = st.selectbox(label, options, index=index, key=key, help=help)
    return None if choice == NONE else choice


CURRENCIES = {"€ – euro": "€", "£ – Englannin punta": "£", "$ – dollari": "$",
              "R$ – Brasilian real": "R$", "kr – kruunu": "kr"}
CUR = "€"  # päivitetään, kun käyttäjä valitsee valuutan


def eur(v: float) -> str:
    """Muotoilee rahasumman valitulla valuutalla, esim. 12 345 €."""
    return f"{v:,.0f} {CUR}".replace(",", " ")


def guess_currency(df: pd.DataFrame) -> str:
    """Arvaa valuutan valuuttasarakkeesta tai maasarakkeesta. Oletus euro."""
    for col in df.columns:
        low = str(col).lower()
        if "currency" in low or "valuutta" in low:
            top = str(df[col].mode().iat[0]).upper() if df[col].notna().any() else ""
            for label, sym in CURRENCIES.items():
                code = {"€": "EUR", "£": "GBP", "$": "USD", "R$": "BRL", "kr": "SEK"}[sym]
                if top in (code, sym.upper()):
                    return label
        if low in ("country", "maa"):
            top = str(df[col].mode().iat[0]).lower() if df[col].notna().any() else ""
            if top in ("united kingdom", "uk"):
                return "£ – Englannin punta"
            if top in ("brazil", "brasil"):
                return "R$ – Brasilian real"
            if top in ("united states", "usa"):
                return "$ – dollari"
        if "state" in low and not pd.api.types.is_numeric_dtype(df[col]):
            # Brasilian osavaltiokoodit (esim. Olist-data)
            br = {"SP", "RJ", "MG", "RS", "PR", "BA", "SC"}
            if df[col].astype(str).str.upper().isin(br).mean() > 0.5:
                return "R$ – Brasilian real"
    return "€ – euro"


def template_csv() -> bytes:
    return pd.DataFrame({
        "order_id": ["1001", "1002", "1003"],
        "customer_id": ["A1", "A2", "A1"],
        "order_date": ["2026-01-15", "2026-02-03", "2026-03-20"],
        "order_value": [59.90, 120.00, 34.50],
    }).to_csv(index=False).encode("utf-8")


# ---------- Sivupalkki: datan lähde ja oletukset ----------

with st.sidebar:
    st.header("Data")
    source = st.radio("Datan lähde", ["Esimerkkidata", "Lataa oma data"], label_visibility="collapsed")
    st.info(
        "**Tietosuoja:** ladattua dataa käsitellään vain tämän istunnon ajan, eikä sitä "
        "tallenneta. Poista silti nimet ja muut suorat tunnisteet ennen latausta – "
        "asiakasnumero riittää.", icon="🔒")
    st.download_button("Lataa CSV-mallipohja", template_csv(), "tilaukset_malli.csv",
                       mime="text/csv", width="stretch")

    with st.expander("Lisäasetukset: konversio-oletukset"):
        st.caption("Vapaaehtoinen. Kuinka moni sadasta tavoitettavasta asiakkaasta ostaa "
                   "kampanjan ansiosta. Vaikuttaa vain Potentiaali-sarakkeeseen. "
                   "Jos tiedät luvut aiemmista kampanjoista, syötä ne tähän.")
        conversion = {
            seg: st.slider(seg, 0, 30, int(SEGMENT_INFO[seg][2] * 100), format="%d %%",
                           key=f"conv_{seg}") / 100
            for seg in SEGMENT_ORDER
        }


# ---------- Otsikko ----------

st.title("Asiakasdatan pikatarkastus")
st.markdown("Lataa verkkokaupan tai kassajärjestelmän tilausdata ja näe kolmessa minuutissa: "
            "**onko data kunnossa, keistä asiakkaista liikevaihto tulee ja mikä automaatio "
            "kannattaa rakentaa ensimmäisenä.**")


# ---------- Datan lataus ja sarakkeiden valinta ----------

customers = None
if source == "Esimerkkidata":
    st.caption("Käytössä kuvitteellinen suomalainen sisustus- ja lahjatavaraketju (verkkokauppa ja "
               "viisi myymälää, kanta-asiakasohjelma) Custobarin vientimuodossa, 2023–2026. "
               "Datassa on tyypillisiä vähittäiskaupan ongelmia. Valitse sivupalkista "
               "*Lataa oma data* kokeillaksesi omalla datallasi.")
    with st.expander("Lataa esimerkkitiedostot itsellesi"):
        st.download_button("custobar_sales.csv", (DATA / "custobar_sales.csv").read_bytes(),
                           "custobar_sales.csv", mime="text/csv")
        st.download_button("custobar_customers.csv", (DATA / "custobar_customers.csv").read_bytes(),
                           "custobar_customers.csv", mime="text/csv")
    sales_raw = pd.read_csv(DATA / "custobar_sales.csv")
    orders, report = prepare_orders(sales_raw, "sale_customer_id", "sale_date", value="total",
                                    order="sale_external_id", cents=True)
    customers = prepare_customers(pd.read_csv(DATA / "custobar_customers.csv"), "external_id",
                                  "email", "can_email")
else:
    up_o = st.file_uploader("**1. Tilausdata** (pakollinen) – yksi tai useampi CSV/Excel",
                            type=["csv", "xlsx"], key="orders", accept_multiple_files=True,
                            help="Jos data on jaettu useaan tiedostoon (esim. tilaukset, maksut ja "
                                 "asiakkaat), lataa ne kaikki – sovellus yhdistää ne yhteisten "
                                 "sarakkeiden avulla.")
    if not up_o:
        st.markdown("""
**Mitä tiedostossa pitää olla?** Yksi rivi per tilaus tai per tilausrivi, ja vähintään:
- asiakastunniste (asiakasnumero tai sähköposti)
- tilauksen päivämäärä
- summa – tai määrä ja yksikköhinta

Sarakkeiden nimillä ei ole väliä, ne valitaan latauksen jälkeen. Jos tiedot ovat eri
tiedostoissa (esim. tilaukset, maksut ja asiakkaat), lataa kaikki kerralla – sovellus
yhdistää ne. Sopii esim. Shopify-, WooCommerce-, Custobar-, Klaviyo- tai
kassajärjestelmäviennille. Mallin saat sivupalkista.
""")
        st.stop()
    try:
        raw_o, join_log = read_and_combine(tuple((f.name, f.getvalue()) for f in up_o))
    except Exception as e:  # noqa: BLE001
        st.error(f"Tiedoston lukeminen epäonnistui: {e}")
        st.stop()
    if join_log:
        with st.expander(f"Tiedostot yhdistetty ({len(up_o)} kpl)"):
            for line in join_log:
                st.markdown(f"- {line}")

    with st.expander("Tilausdatan sarakkeet", expanded=True):
        st.dataframe(raw_o.head(5), hide_index=True, width="stretch")
        cols = raw_o.columns
        k = "|".join(sorted(f.name for f in up_o))  # uusi tiedostojoukko saa uudet arvaukset
        c1, c2, c3 = st.columns(3)
        with c1:
            col_cust = pick("Asiakastunniste", cols, "customer", f"o_cust_{k}")
        with c2:
            col_date = pick("Tilauspäivä", cols, "date", f"o_date_{k}")
        with c3:
            col_order = pick("Tilausnumero (jos rivitasoista dataa)", cols, "order",
                             f"o_order_{k}", optional=True,
                             help="Jos samalla tilauksella on useita rivejä, ne yhdistetään.")
        value_mode = st.radio("Tilauksen arvo", ["Summa-sarake", "Määrä × hinta"], horizontal=True,
                              index=0 if guess_column(cols, "value") or not guess_column(cols, "qty")
                              else 1, key=f"o_mode_{k}")
        if value_mode == "Summa-sarake":
            col_value = pick("Summa", cols, "value", f"o_value_{k}")
            col_qty = col_price = None
        else:
            col_value = None
            col_qty = pick("Määrä", cols, "qty", f"o_qty_{k}")
            col_price = pick("Yksikköhinta", cols, "price", f"o_price_{k}")
        col_status = pick("Tilauksen tila (perutut jätetään pois)", cols, "status", f"o_status_{k}",
                          optional=True,
                          help="Rivit, joiden tila sisältää esim. canceled/peruttu, jätetään pois.")
        cur_guess = guess_currency(raw_o)
        cur_label = st.selectbox("Valuutta", list(CURRENCIES), key=f"o_cur_{k}",
                                 index=list(CURRENCIES).index(cur_guess),
                                 help="Valuuttaa ei muunneta – valinta vaikuttaa vain siihen, "
                                      "millä merkillä summat näytetään.")
        CUR = CURRENCIES[cur_label]
        looks_custobar = any(str(c).startswith("sale_") for c in cols)
        cents = st.checkbox("Summat ovat senteissä (esim. Custobar-vienti)", value=looks_custobar,
                            key=f"o_cents_{k}",
                            help="Custobar ja monet kassajärjestelmät tallentavat 12,00 € muodossa 1200.")

    try:
        orders, report = prepare_orders(raw_o, col_cust, col_date, value=col_value,
                                        qty=col_qty, price=col_price, order=col_order,
                                        cents=cents, status=col_status)
    except Exception as e:  # noqa: BLE001
        st.error(f"Sarakkeita ei voitu käsitellä – tarkista valinnat. ({e})")
        st.stop()

    up_c = st.file_uploader("**2. Asiakasdata** (vapaaehtoinen) – tuo mukaan sähköpostit ja "
                            "markkinointiluvat", type=["csv", "xlsx"], key="customers")
    if up_c is not None:
        try:
            raw_c = read_file(up_c.name, up_c.getvalue())
            with st.expander("Asiakasdatan sarakkeet", expanded=True):
                st.dataframe(raw_c.head(5), hide_index=True, width="stretch")
                cc, kc = raw_c.columns, up_c.name
                cust_c = pick("Asiakastunniste (sama kuin tilauksissa)", cc, "customer", f"c_cust_{kc}")
                email_c = pick("Sähköposti", cc, "email", f"c_email_{kc}", optional=True)
                consent_c = pick("Markkinointilupa", cc, "consent", f"c_consent_{kc}", optional=True,
                                 help="Arvot kuten true/1/kyllä/yes tulkitaan luvaksi.")
            customers = prepare_customers(raw_c, cust_c, email_c, consent_c)
            match = customers["customer_id"].isin(orders["customer_id"]).mean()
            if match < 0.1:
                st.warning(f"Vain {match:.0%} asiakkaista löytyy tilausdatasta. "
                           "Tarkista, että asiakastunniste on sama molemmissa tiedostoissa.")
        except Exception as e:  # noqa: BLE001
            st.error(f"Asiakasdatan käsittely epäonnistui: {e}")
            customers = None

if orders.empty:
    st.error("Datasta ei löytynyt yhtään kelvollista tilausta. Tarkista sarakevalinnat: "
             "asiakastunniste, päivämäärä ja positiivinen summa.")
    st.stop()
if source != "Esimerkkidata":
    if report.get("cancelled"):
        st.caption(f"Perutut tilaukset jätettiin pois ({report['cancelled']:.1%} riveistä).")
    if report.get("duplicate_rows"):
        st.caption(f"Tuplarivit poistettiin ({report['duplicate_rows']:.1%} riveistä), "
                   "jotta myyntiä ei lasketa kahteen kertaan.")
    if report.get("order_level_total"):
        st.info("Summa-sarake näyttää olevan koko tilauksen summa, joka toistuu jokaisella "
                "rivillä – se laskettiin kerran per tilaus.")
    whole = (orders["order_value"] % 1 == 0).mean() > 0.95  # sentit näkyvät kokonaislukuina
    if not cents and whole and orders["order_value"].median() > 1000:
        st.info("Tilausten mediaani on yli 1 000 €. Jos summat ovat senteissä, "
                "rastita *Summat ovat senteissä* sarakevalinnoista.")
    repeat = orders.groupby("customer_id")["order_id"].nunique()
    if len(repeat) > 100 and (repeat > 1).mean() < 0.01:
        st.info("Lähes jokaisella asiakkaalla on vain yksi tilaus. Jos datassa on pysyvämpi "
                "asiakastunniste (esim. *customer_unique_id* tai sähköposti), valitse se "
                "Asiakastunniste-kohtaan – muuten saman ihmisen tilaukset eivät yhdisty.")
if orders["customer_id"].nunique() < 10:
    st.warning("Datassa on alle 10 asiakasta, joten segmentit ovat suuntaa-antavia.")

today = reference_date(orders)
r = rfm(orders, today)
s = segment_summary(r, customers, conversion)
q = data_quality(orders, report, customers)
has_consent = customers is not None and "email_consent" in customers


# ---------- Yhteenveto ----------

def compact(v: float) -> str:
    """Lyhyt rahasumma tunnuslukuihin, esim. 15,7 milj. €."""
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.1f}".replace(".", ",") + f" milj. {CUR}"
    return eur(v)


y0, y1 = orders["order_date"].min().year, orders["order_date"].max().year
kpis = [
    ("Ostaneita asiakkaita", f"{orders['customer_id'].nunique():,}".replace(",", " "), ""),
    ("Tilauksia", f"{len(orders):,}".replace(",", " "), ""),
    ("Liikevaihto", compact(orders["order_value"].sum()), eur(orders["order_value"].sum())),
    ("Aikaväli", str(y0) if y0 == y1 else f"{y0}–{y1}",
     f"{orders['order_date'].min():%d.%m.%Y} – {orders['order_date'].max():%d.%m.%Y}"),
]
# Kortit rivittyvät automaattisesti kapealla näytöllä, joten luvut eivät katkea
cards = "".join(
    f'<div title="{tip}" style="flex:1 1 170px;padding:0.6rem 0.9rem;border-radius:8px;'
    f'background:rgba(128,128,128,0.08)"><div style="font-size:0.85rem;opacity:0.75">{label}</div>'
    f'<div style="font-size:1.7rem;font-weight:500;white-space:nowrap">{value}</div></div>'
    for label, value, tip in kpis)
st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin:0.5rem 0 1rem">{cards}</div>',
            unsafe_allow_html=True)


# ---------- 1. Datan laatu ----------

st.header("1. Datan laatu")
c1, c2 = st.columns([1, 3])
c1.metric("Laatupisteet", f"{q['score']}/100",
          help="Hyvä ≥ 90, kohtalainen 75–89, heikko < 75. Pisteisiin vaikuttaa ongelmien koko "
               "(jo muutaman prosentin virhe näkyy) ja määrä: jokainen löydetty ongelmatyyppi "
               "vähentää lisäksi 2 pistettä.")
c1.markdown(f"**{q['grade']}**" + (f" – {q['issue_types']} erilaista ongelmaa"
                                     if q["issue_types"] else ""))
n_checks, max_checks = len(q["checks"]), 11
c1.caption(f"{n_checks}/{max_checks} tarkistusta tehty. " + f"Luettu {report['rows']:,} riviä, joista {report['kept_rows']:,} kelvollisia."
           .replace(",", " "))
checks = pd.Series(q["checks"]).mul(100).round(1)
ok = checks[checks == 0].index.tolist()
qdf = checks[checks > 0].rename_axis("Tarkistus").reset_index(name="Osuus (%)")
if qdf.empty:
    c2.success("Kaikki tehdyt tarkistukset kunnossa." if n_checks < max_checks
               else "Kaikki tarkistukset kunnossa.")
else:
    c2.altair_chart(
        alt.Chart(qdf).mark_bar(color="#D85A30").encode(
            x=alt.X("Osuus (%):Q", title="Osuus riveistä tai asiakkaista (%)"),
            y=alt.Y("Tarkistus:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
            tooltip=["Tarkistus", "Osuus (%)"],
        ).properties(height=max(120, 40 * len(qdf))),
        width="stretch",
    )
if ok:
    ok_text = {
        "Rivit ilman asiakastunnistetta": "kaikilla riveillä on asiakastunniste",
        "Virheellinen päivämäärä": "kaikki päivämäärät ovat kelvollisia",
        "Palautukset tai virheelliset summat": "ei palautuksia tai virheellisiä summia",
        "Duplikaattiasiakkaat": "ei duplikaattiasiakkaita",
        "Ei yhtään ostoa": "kaikilla asiakkailla on ostoja",
        "Sähköposti puuttuu": "kaikilla asiakkailla on sähköposti",
        "Sama sähköposti usealla asiakkaalla": "ei päällekkäisiä sähköposteja",
        "Ei markkinointilupaa": "kaikilla asiakkailla on markkinointilupa",
        "Tuplarivit (sama rivi kahdesti)": "ei tuplarivejä",
        "Päivämäärä tulevaisuudessa": "ei tulevaisuuteen päivättyjä tilauksia",
        "Poikkeavan suuret tai pienet summat": "ei poikkeavia summia",
    }
    c2.caption("✓ Kunnossa: " + ", ".join(ok_text.get(x, x.lower()) for x in ok) + ".")
if n_checks < max_checks:
    st.info(f"Laatupisteet perustuvat vain {n_checks} tarkistukseen {max_checks}:sta. Lataa myös "
            "asiakasdata (sähköpostit ja markkinointiluvat), niin loput voidaan tarkistaa ja näet, "
            "kuinka suuren osan asiakkaista voit oikeasti tavoittaa.", icon="💡")


# ---------- 2. Segmentit ----------

st.header("2. Asiakassegmentit (RFM)")
st.caption("Asiakkaat ryhmitellään sen mukaan, kuinka äskettäin (R), kuinka usein (F) ja kuinka "
           "paljon (M) he ovat ostaneet. Kaavio näyttää, kuinka suuri osa asiakkaista tuo "
           "kuinka suuren osan liikevaihdosta.")
seg = pd.DataFrame({
    "Segmentti": s.index,
    "Osuus asiakkaista": s["asiakas_osuus"] * 100,
    "Osuus liikevaihdosta": s["lv_osuus"] * 100,
}).melt("Segmentti", var_name="Mittari", value_name="Osuus (%)")
seg["Osuus (%)"] = seg["Osuus (%)"].round(1)
st.altair_chart(
    alt.Chart(seg).mark_bar().encode(
        y=alt.Y("Segmentti:N", sort=SEGMENT_ORDER, title=None, axis=alt.Axis(labelLimit=200)),
        yOffset=alt.YOffset("Mittari:N", sort=["Osuus asiakkaista", "Osuus liikevaihdosta"]),
        x=alt.X("Osuus (%):Q", title="Osuus (%)"),
        color=alt.Color("Mittari:N", scale=alt.Scale(range=["#B4B2A9", "#1D9E75"]),
                        legend=alt.Legend(title=None, orient="top")),
        tooltip=["Segmentti", "Mittari", "Osuus (%)"],
    ).properties(height=60 * len(s)),
    width="stretch",
)
if "Parhaat asiakkaat" in s.index:
    m = s.loc["Parhaat asiakkaat"]
    st.markdown(f"**Parhaat asiakkaat** ovat {m['asiakas_osuus'] * 100:.0f} % asiakkaista mutta tuovat "
                f"{m['lv_osuus'] * 100:.0f} % liikevaihdosta.")


# ---------- 3. Toimenpiteet ----------

st.header("3. Suositellut automaatiot")
st.caption("Potentiaali = asiakkaat × markkinointilupa × oletettu konversio × keskiostos. "
           "Konversio-oletuksia voi säätää sivupalkin lisäasetuksista.")
show = s.sort_values("potentiaali_eur", ascending=False).reset_index()
table = pd.DataFrame({
    "Segmentti": show["segment"],
    "Asiakkaita": show["asiakkaita"],
    "Keskiostos": show["keskiostos"].map(eur),
    "Suositeltu toimenpide": show["toimenpide"],
    "Potentiaali": show["potentiaali_eur"].round(-1).map(eur),
})
if has_consent:
    table.insert(2, "Lupa", (show["lupa_osuus"] * 100).round().astype(int).astype(str) + " %")
st.table(table.set_index("Segmentti"))  # kaikki sarakkeet näkyvät, teksti rivittyy
with st.expander("Mitä segmentit tarkoittavat?"):
    for seg_name in SEGMENT_ORDER:
        st.markdown(f"- **{seg_name}:** {SEGMENT_INFO[seg_name][0].lower()}")

top = show.iloc[0]
st.success(f"**Suurin nopea voitto: {top['segment']}** – {top['toimenpide']}. "
           f"Arvioitu lisämyynti ~{eur(round(top['potentiaali_eur'], -1))} yhdellä kampanjalla.")
if not has_consent:
    st.caption("Ilman lupatietoja potentiaali olettaa, että kaikki asiakkaat ovat tavoitettavissa.")

export = r.reset_index()[["customer_id", "segment", "recency", "frequency", "monetary"]]
export.columns = ["customer_id", "segmentti", "paivia_viime_ostosta", "tilauksia", "ostot_yht"]
st.download_button("Lataa asiakkaiden segmentit (CSV) – esim. tuontiin Klaviyoon tai Custobariin",
                   export.to_csv(index=False).encode("utf-8"), "segmentit.csv", mime="text/csv")

st.divider()
st.caption(f"Laskettu {today - pd.Timedelta(days=1):%d.%m.%Y} tilanteen mukaan "
           "(viimeisin tilaus datassa). Segmentointi: RFM-kvintiilit. "
           "Ladattua dataa ei tallenneta.")