# Asiakasdatan pikatarkastus

Työkalu, joka kertoo verkkokaupan tai kassajärjestelmän tilausdatasta kolmessa minuutissa:

1. **Onko data kunnossa?** Laatupisteet ja yleisimmät ongelmat (puuttuvat tunnisteet, duplikaatit, markkinointiluvat).
2. **Keistä asiakkaista liikevaihto tulee?** RFM-segmentointi (Recency, Frequency, Monetary).
3. **Mikä automaatio kannattaa rakentaa ensimmäisenä?** Segmenttikohtaiset suositukset ja euromääräinen potentiaali.

## Käyttö

- Avaa sovellus ja valitse sivupalkista **Esimerkkidata** tai **Lataa oma data**.
- Oma data: CSV tai Excel, jossa on vähintään asiakastunniste, tilauspäivä ja summa (tai määrä ja hinta). Sarakkeet valitaan latauksen jälkeen, joten nimillä ei ole väliä.
- Valinnainen asiakastiedosto tuo mukaan sähköpostit ja markkinointiluvat.
- Konversio-oletuksia voi säätää sivupalkista.
- Segmentit voi ladata CSV:nä esim. Klaviyoon tai Custobariin.

Testattu mm. [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) -datalla (CC BY 4.0) sekä suomalaisilla CSV-muodoilla (puolipiste, desimaalipilkku, pp.kk.vvvv).

## Tietosuoja

Ladattua dataa käsitellään vain istunnon ajan, eikä sitä tallenneta. Suosittelen silti poistamaan nimet ja muut suorat tunnisteet ennen latausta.

## Laskentaperiaatteet

- "Tänään" = viimeisin tilaus datassa + 1 päivä, joten myös vanha data toimii.
- R, F ja M pisteytetään 1–5 persentiilien mukaan; segmentit muodostetaan R- ja F-pisteistä.
- Potentiaali = asiakkaat × markkinointilupa × oletettu konversio × keskiostos. Ilman lupatietoja oletetaan, että kaikki ovat tavoitettavissa.

## Ajo omalla koneella

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Esimerkkidatan voi luoda uudelleen komennolla `python3 generate_data.py`.

## Tiedostot

| Tiedosto | Sisältö |
|---|---|
| `app.py` | Streamlit-käyttöliittymä |
| `analysis.py` | Datan valmistelu, laatu, RFM ja suositukset |
| `generate_data.py` | Kuvitteellisen esimerkkidatan luonti |
| `data/` | Esimerkkidata |
