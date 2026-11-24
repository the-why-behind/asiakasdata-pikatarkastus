# Asiakasdatan pikatarkastus

**Kokeile sovellusta:** https://asiakasdata-pikatarkastus.streamlit.app/

Ei tarvitse kirjautua tai asentaa mitään, sovellus aukeaa suoraan selaimessa.

🎬 **VIDEO 0 TÄHÄN** – koko sovellus lyhyesti (n. 30 s)

---

## Miksi tein tämän

Tutustuin 70/30 Digitaliin yrityksen julkisten tietojen kautta. Yritys kertoo olevansa Suomen ainoa markkinointitoimisto, joka keskittyy kokonaan asiakkaidensa omaan dataan. Sen palveluihin kuuluvat muun muassa asiakasdatan auditointi ja segmentointi. Asiakkaista suuri osa on vähittäiskauppoja, kuten Robers Coffee ja Pentik. Työntekijöitä yrityksessä on 1–10, eli kyse on pienestä yrityksestä.

Ennen kuin asiakkaalle voi suunnitella automaatioita tai kanta-asiakasohjelmaa, on selvitettävä, onko data käyttökelpoista ja keitä asiakkaat ovat. Tämä vaihe toistuu jokaisen asiakkaan kohdalla lähes samanlaisena, ja pienessä tiimissä se on pois varsinaisesta asiantuntijatyöstä.

Siksi tein työkalun, joka hoitaa auditoinnin ja segmentoinnin ensimmäisen vaiheen automaattisesti. Koska yrityksen asiakkaat ovat pääosin vähittäiskauppoja, työkalu on suunniteltu tilaus- ja kanta-asiakasdatalle.

Näin jokaisen uuden asiakkaan datan ensikatsaus hoituu paljon nopeammin.

Johtopäätökseni perustuvat julkisiin tietoihin, joten osa niistä on oletuksia.

## Mikä sovellus on

Selaimessa toimiva työkalu, johon ladataan verkkokaupan tai kassajärjestelmän vienti. Se vastaa kolmeen kysymykseen:

1. **Onko data kunnossa?**
   11 tarkistusta: puuttuvat asiakastunnisteet, tuplarivit, virheelliset päivämäärät ja summat, poikkeavat summat, duplikaattiasiakkaat, puuttuvat sähköpostit ja markkinointiluvat. Tuloksena laatupisteet (0–100) ja arvosana.
2. **Keistä asiakkaista liikevaihto tulee?**
   RFM-segmentointi: asiakkaat ryhmitellään sen mukaan, kuinka äskettäin, kuinka usein ja kuinka paljon he ostavat (esim. *Parhaat asiakkaat*, *Poistumisvaarassa*, *Passiiviset*).
3. **Mikä automaatio kannattaa rakentaa ensimmäisenä?**
   Jokaiselle segmentille suositeltu toimenpide ja arvioitu lisämyynti euroina. Segmentit voi ladata CSV-tiedostona esimerkiksi Klaviyoon tai Custobariin.

**Ominaisuuksia**
- Toimii eri järjestelmien vienneillä: sarakkeet tunnistetaan automaattisesti (testattu mm. Custobar-, Shopify-, Klaviyo- ja kassajärjestelmämuodoilla).
- Useaan tiedostoon jaettu data yhdistetään automaattisesti yhteisten sarakkeiden avulla.
- Ymmärtää suomalaiset muodot (puolipiste, desimaalipilkku, 24.11.2025) ja senteissä olevat summat.
- Perutut ja palautetut tilaukset jätetään pois.
- Konversio-oletuksia voi säätää omien kampanjatulosten mukaan.

---

## Näin kokeilet sovellusta

### Vaihtoehto 1: Esimerkkidata (1 minuutti)

1. Avaa https://asiakasdata-pikatarkastus.streamlit.app/
   *Jos sivulla lukee "Yes, get this app back up!", paina painiketta ja odota noin 30 sekuntia – sovellus on ollut lepotilassa.*
2. Sovellus aukeaa valmiiksi esimerkkidatalla: kuvitteellinen suomalainen sisustus- ja lahjatavaraketju (verkkokauppa + viisi myymälää, kanta-asiakasohjelma) Custobarin vientimuodossa.
3. Vieritä sivua alaspäin ja katso kolme osiota:
   - **1. Datan laatu** – mitä datassa on vialla
   - **2. Asiakassegmentit** – keistä asiakkaista liikevaihto tulee
   - **3. Suositellut automaatiot** – mistä kannattaa aloittaa

🎬 **VIDEO 1 TÄHÄN** – sovelluksen avaaminen ja vierittäminen osioiden läpi (n. 20 s)

### Vaihtoehto 2: Oma tai testidata

1. Lataa testitiedostot tämän sivun **testidata**-kansiosta (avaa tiedosto ja paina oikeasta yläkulmasta latausnuolta).
   - **A – verkkokauppa:** `A_shopify_orders.csv` (tilaukset) ja `A_klaviyo_profiles.csv` (asiakkaat ja luvat)
   - **B – kassajärjestelmä:** `B_kassa_kuitit.csv` (kuitit) ja `B_kassa_asiakasrekisteri.csv` (asiakasrekisteri)

🎬 **VIDEO 2 TÄHÄN** – testitiedostojen lataaminen GitHubista (n. 10 s)

2. Valitse sovelluksen vasemmasta sivupalkista **Lataa oma data**.
3. Lataa **tilaustiedosto** kenttään **1. Tilausdata**.
4. Lataa **asiakastiedosto** kenttään **2. Asiakasdata**.
   *Muistisääntö: tilaukset ylös, asiakkaat alas.*

🎬 **VIDEO 3 TÄHÄN** – tiedostojen lataaminen oikeisiin kenttiin (n. 20 s)

5. Tarkista kohdasta **Tilausdatan sarakkeet**, että sovellus valitsi oikeat sarakkeet (asiakastunniste, päivämäärä, summa). Yleensä ne ovat valmiiksi oikein.
6. Vieritä alas tuloksiin.

🎬 **VIDEO 4 TÄHÄN** – sarakevalintojen tarkistus ja tulokset (n. 20 s)

### Lisäksi voit kokeilla

- **Konversio-oletukset:** avaa sivupalkista *Lisäasetukset* ja liikuta säätimiä – Potentiaali-sarake päivittyy heti.
- **Segmenttien lataus:** paina sivun lopusta *Lataa asiakkaiden segmentit (CSV)*.

🎬 **VIDEO 5 TÄHÄN** – säätimet ja segmenttien lataus (n. 15 s)

---

## Tietosuoja

Ladattua dataa käsitellään vain istunnon ajan, eikä sitä tallenneta. Kaikki tämän sivun esimerkki- ja testidata on kuvitteellista. Omaa dataa kokeiltaessa nimet ja muut suorat tunnisteet kannattaa poistaa ennen latausta – asiakasnumero riittää.

## Laskentaperiaatteet

- **Laatupisteet:** ongelman koko (2 % virhe vie 10 % tarkistuksen painosta, 20 % koko painon) ja jokainen löydetty ongelmatyyppi −2 pistettä. Hyvä ≥ 90, kohtalainen 75–89, heikko < 75.
- **RFM:** R, F ja M pisteytetään 1–5 persentiilien mukaan; segmentit muodostetaan R- ja F-pisteistä. "Tänään" = viimeisin tilaus datassa + 1 päivä.
- **Potentiaali** = asiakkaat × markkinointilupa × oletettu konversio × keskiostos. Konversio-oletukset ovat tarkoituksella säädettäviä, koska oikeat luvut tulevat asiakkaan omasta kampanjahistoriasta.

## Testattu datalla

- Esimerkkidata Custobarin vientimuodossa (kuvitteellinen)
- Testidata A: Shopify + Klaviyo (kuvitteellinen)
- Testidata B: suomalainen kassajärjestelmä (kuvitteellinen)
- [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) – oikea verkkokauppadata, n. 100 000 tilausta
- [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii) – oikea verkkokauppadata, yli miljoona riviä (CC BY 4.0)

## Tekniikka

Python, pandas, Streamlit ja Altair. Sovellus pyörii Streamlit Community Cloudissa.

| Tiedosto | Sisältö |
|---|---|
| `app.py` | Käyttöliittymä |
| `analysis.py` | Datan valmistelu, laatutarkistukset, RFM ja suositukset |
| `data/` | Esimerkkidata (Custobar-muoto) |
| `testidata/` | Testitiedostot A ja B |
| `tools/generate_custobar_data.py` | Esimerkkidatan luonti |

**Ajo omalla koneella**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
