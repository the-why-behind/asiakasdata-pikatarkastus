# Asiakasdatan pikatarkastus

**Kokeile sovellusta:** https://asiakasdata-pikatarkastus.streamlit.app/

Ei tarvitse kirjautua tai asentaa mitään, sovellus aukeaa suoraan selaimessa.



https://github.com/user-attachments/assets/4763de53-4c4a-43bf-a06f-53a3ed687224



---

## Ongelma ja ratkaisu

### Taustatoedot
Tutustuin 70/30 Digitaliin yrityksen julkisten tietojen kautta. Yritys kertoo olevansa Suomen ainoa markkinointitoimisto, joka keskittyy kokonaan asiakkaidensa omaan dataan. Sen palveluihin kuuluvat muun muassa asiakasdatan auditointi ja segmentointi. Asiakkaista suuri osa on vähittäiskauppoja, kuten Robers Coffee ja Pentik. Työntekijöitä yrityksessä on 1–10, eli kyse on pienestä yrityksestä.

### Ongelma lyhyesti
Ennen kuin asiakkaalle voi suunnitella automaatioita tai kanta-asiakasohjelmaa, on selvitettävä, onko data käyttökelpoista ja keitä asiakkaat ovat. Tämä vaihe toistuu jokaisen asiakkaan kohdalla lähes samanlaisena, ja pienessä tiimissä se on pois varsinaisesta asiantuntijatyöstä.

### Ratkaisu
Siksi tein työkalun, joka hoitaa auditoinnin ja segmentoinnin ensimmäisen vaiheen automaattisesti. Työkalu ryhmittelee asiakkaat ja tekee niistä listan, jota voi käyttää jatkotyössä. Koska yrityksen asiakkaat ovat pääosin vähittäiskauppoja, työkalu on suunniteltu tilaus- ja kanta-asiakasdatalle.

Näin uuden asiakkaan datan läpikäynti nopeutuu huomattavasti.

Johtopäätökseni perustuvat julkisiin tietoihin, joten osa niistä on oletuksia.

## Mikä sovellus on

Selaimessa toimiva työkalu, johon ladataan yrityksen tilaus- ja asiakasdata CSV- tai Excel-tiedostona. Se vastaa kolmeen kysymykseen:

1. **Onko data kunnossa?**
   Työkalu tekee datalle 11 tarkistusta. Se etsii esimerkiksi puuttuvat asiakastunnisteet, tuplarivit, virheelliset päivämäärät ja summat, poikkeavat summat sekä asiakkaat, jotka on kirjattu kahteen kertaan. Lisäksi se tarkistaa, kuinka monelta asiakkaalta puuttuu sähköposti tai markkinointilupa. Tuloksena on laatupisteet asteikolla 0–100 ja arvosana.
2. **Keistä asiakkaista liikevaihto tulee?**
   Asiakkaat jaetaan ryhmiin sen mukaan, milloin he ovat viimeksi ostaneet, kuinka usein he ostavat ja kuinka paljon he ostavat yhteensä (RFM-segmentointi). Ryhmiä ovat esimerkiksi *Parhaat asiakkaat*, *Poistumisvaarassa* ja *Passiiviset*.
3. **Mistä automaatiosta kannattaa aloittaa?**
   Työkalu ehdottaa jokaiselle ryhmälle sopivaa toimenpidettä ja arvioi, kuinka paljon lisämyyntiä se voisi tuoda. Asiakkaiden ryhmät voi ladata CSV-tiedostona ja tuoda esimerkiksi Klaviyoon tai Custobariin.

**Ominaisuudet**
- Työkalu toimii eri järjestelmistä ladatuilla tiedostoilla ja tunnistaa sarakkeet automaattisesti. Sitä on testattu itse tehdyillä testitiedostoilla, jotka jäljittelevät Custobarin, Shopifyn, Klaviyon ja kassajärjestelmän tiedostomuotoja, sekä kahdella julkisella verkkokauppa-aineistolla.
- Jos data on jaettu useaan tiedostoon, työkalu yhdistää ne automaattisesti.
- Työkalu ymmärtää suomalaiset tiedostomuodot, kuten desimaalipilkun ja päivämäärät muodossa 24.11.2025, sekä senteissä ilmoitetut summat.
- Perutut ja palautetut tilaukset jätetään laskelmista pois.
- Lisämyyntiarvion oletuksia voi muuttaa omien kampanjatulosten perusteella.

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
