# Asiakasdatan pikatarkastus

**Kokeile sovellusta:** https://asiakasdata-pikatarkastus.streamlit.app/

Ei tarvitse kirjautua tai asentaa mitään, sovellus aukeaa suoraan selaimessa.



https://github.com/user-attachments/assets/4763de53-4c4a-43bf-a06f-53a3ed687224



---

## Ongelma ja ratkaisu

### Taustatoedot
Tutustuin 70/30 Digitaliin yrityksen julkisten tietojen kautta. Yritys kertoo olevansa Suomen ainoa markkinointitoimisto, joka keskittyy kokonaan asiakkaidensa omaan dataan. Sen palveluihin kuuluvat muun muassa asiakasdatan auditointi ja segmentointi. Asiakkaina on muun muassa vähittäiskauppoja, kuten Gugguu ja Pentik. Työntekijöitä yrityksessä on 1–10, eli kyse on pienestä yrityksestä.

### Ongelma lyhyesti
Ennen kuin asiakkaalle voi suunnitella automaatioita tai kanta-asiakasohjelmaa, on selvitettävä, onko data käyttökelpoista ja keitä asiakkaat ovat. Tämä vaihe toistuu jokaisen asiakkaan kohdalla lähes samanlaisena, ja pienessä tiimissä se on pois varsinaisesta asiantuntijatyöstä.

### Ratkaisu
Siksi tein työkalun, joka hoitaa auditoinnin ja segmentoinnin ensimmäisen vaiheen automaattisesti. Työkalu ryhmittelee asiakkaat ja tekee niistä listan, jota voi käyttää jatkotyössä. Koska yrityksen asiakkaisiin kuuluu vähittäiskauppoja, työkalu on suunniteltu tilaus- ja kanta-asiakasdatalle.

Näin uuden asiakkaan datan läpikäynti nopeutuu huomattavasti.

Johtopäätökseni perustuvat julkisiin tietoihin, joten osa niistä on oletuksia.

## Näin työkalu toimii

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

### Vaihtoehto 1: Esimerkkidata

1. Avaa https://asiakasdata-pikatarkastus.streamlit.app/
   *Jos sivulla lukee "Yes, get this app back up!", työkalu on ollut lepotilassa. Paina painiketta ja odota noin 30 sekuntia.*
2. Työkalu avautuu valmiiksi esimerkkidatan kanssa. Data on kuvitteellisen suomalaisen sisustus- ja lahjatavaraketjun, jolla on verkkokauppa, viisi myymälää ja kanta-asiakasohjelma. Data on samassa muodossa kuin Custobarista ladattu tiedosto.
3. Vieritä sivua alaspäin. Tulokset näkyvät kolmessa osiossa:
   - **1. Datan laatu:** mitä datassa on vialla
   - **2. Asiakassegmentit:** keistä asiakkaista liikevaihto tulee
   - **3. Suositellut automaatiot:** mistä kannattaa aloittaa

### Vaihtoehto 2: Oma tai testidata

1. Lataa testitiedostot tämän sivun **testidata**-kansiosta (avaa tiedosto ja paina oikeasta yläkulmasta latausnuolta).
   - **A – verkkokauppa:** [A_shopify_orders.csv](testidata/A_shopify_orders.csv) (tilaukset) ja [A_klaviyo_profiles.csv](testidata/A_klaviyo_profiles.csv) (asiakkaat ja markkinointiluvat)
   - **B – kassajärjestelmä:** [B_kassa_kuitit.csv](testidata/B_kassa_kuitit.csv) (kuitit) ja [B_kassa_asiakasrekisteri.csv](testidata/B_kassa_asiakasrekisteri.csv) (asiakasrekisteri)
2. Valitse sovelluksen vasemmasta sivupalkista **Lataa oma data**.
3. Lataa **tilaustiedosto** kenttään **1. Tilausdata**.
4. Lataa **asiakastiedosto** kenttään **2. Asiakasdata**.
5. Tarkista kohdasta **Tilausdatan sarakkeet**, että sovellus valitsi oikeat sarakkeet (asiakastunniste, päivämäärä, summa). Yleensä ne ovat valmiiksi oikein.
6. Vieritä alas tuloksiin.

### Lisäksi voit kokeilla

- **Konversio-oletukset:** avaa sivupalkista *Lisäasetukset* ja liikuta säätimiä – Potentiaali-sarake päivittyy heti.
- **Segmenttien lataus:** paina sivun lopusta *Lataa asiakkaiden segmentit (CSV)*.

https://github.com/user-attachments/assets/11a158c7-68ef-4c2e-848b-87186640b8da

---

## Tietosuoja

Ladattua dataa käsitellään vain istunnon ajan, eikä sitä tallenneta. Kaikki tämän sivun esimerkki- ja testidata on kuvitteellista. Omaa dataa kokeiltaessa nimet ja muut suorat tunnisteet kannattaa poistaa ennen latausta – asiakasnumero riittää.

## Näin tulokset lasketaan

- **Laatupisteet:** työkalu aloittaa 100 pisteestä ja vähentää pisteitä jokaisesta löydetystä ongelmasta. Mitä enemmän virheitä datassa on, sitä enemmän pisteitä vähennetään. Tärkeistä ongelmista, kuten puuttuvista markkinointiluvista, vähennetään enemmän pisteitä kuin pienistä. Lisäksi jokainen eri ongelmatyyppi vähentää kaksi pistettä.
  - 90–100 pistettä: *hyvä*
  - 75–89 pistettä: *kohtalainen*
  - alle 75 pistettä: *heikko*
- **Asiakasryhmät (RFM):** jokainen asiakas pisteytetään kolmella tavalla asteikolla 1–5:
  - **R:** milloin asiakas on viimeksi ostanut
  - **F:** kuinka usein asiakas ostaa
  - **M:** kuinka paljon asiakas ostaa yhteensä

   Pisteet annetaan vertaamalla asiakasta muihin saman datan asiakkaisiin. Asiakkaan ryhmä määräytyy R- ja F-pisteiden perusteella. Laskennassa "tänään" tarkoittaa datan viimeisintä tilauspäivää, joten työkalu toimii myös vanhemmalla datalla.
- **Lisämyyntiarvio:** arvio kertoo, kuinka paljon lisämyyntiä yksi kampanja voisi tuoda. Se lasketaan näin:

  *asiakkaiden määrä × markkinointiluvan antaneiden osuus × oletettu ostoprosentti × keskiostos*

  Ostoprosentti on oletus, koska todelliset luvut selviävät vasta yrityksen omista kampanjoista. Siksi sitä voi muuttaa sivupalkin lisäasetuksista.

## Testattu datalla

**Itse tehty testidata (kuvitteellinen):**
- Esimerkkidata, joka on samassa muodossa kuin Custobarista ladattu tiedosto
- Testidata A, joka jäljittelee Shopifyn ja Klaviyon tiedostoja
- Testidata B, joka jäljittelee suomalaisen kassajärjestelmän tiedostoja

**Julkinen, oikea data:**
- [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce): brasilialaisen verkkokaupan data, noin 100 000 tilausta
- [UCI Online Retail II](https://archive.ics.uci.edu/dataset/502/online+retail+ii): brittiläisen verkkokaupan data, yli miljoona riviä (lisenssi CC BY 4.0)

## Tekniikka

Python, pandas, Streamlit ja Altair. Sovellus pyörii Streamlit Community Cloudissa.

| Tiedosto | Sisältö |
|---|---|
| `app.py` | Käyttöliittymä |
| `analysis.py` | Datan valmistelu, laatutarkistukset, RFM ja suositukset |
| `data/` | Esimerkkidata (Custobar-muoto) |
| `testidata/` | Testitiedostot A ja B |
| `tools/generate_custobar_data.py` | Esimerkkidatan luonti |
