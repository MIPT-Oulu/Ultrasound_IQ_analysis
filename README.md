

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/github_username/repo_name"> <!-- mikäli Gihubiin niin päivitä!-->
    <img src="images/logo.png" alt="Logo" width="80" height="80">  <!-- mikäli Gihubiin niin päivitä!-->
  </a>

  <h3 align="center">project_title</h3>

  <p align="center">
    project_description
    <br />
    <a href="https://github.com/github_username/repo_name"><strong>Dokumentaatio »</strong></a>  <!-- mikäli Gihubiin niin päivitä!-->
    <br />
    <br />
    <a href="https://github.com/github_username/repo_name">Katso Demo</a>  <!-- mikäli Gihubiin niin päivitä!-->
    ·
    <a href="https://github.com/github_username/repo_name/issues">Raportoi Bugi</a>  <!-- mikäli Gihubiin niin päivitä!-->
    
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Sisällysluettelo</h2></summary>
  <ol>
    <li>
      <a href="#tietoa-projektista">Tietoa projektista</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#ohjelmistovaatimukset">Ohjelmistovaatimukset</a></li>
        <li><a href="#asennus">Asennus</a></li>
      </ul>
    </li>
    <li><a href="#käyttö">Käyttö</a></li>
    <li><a href="#vaikuttaminen">Vaikuttaminen</a></li>
    <li><a href="#lisenssi">Lisenssi</a></li>
    <li><a href="#ota-yhteyttä">Ota yhteyttä</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## Tietoa projektista

[![Product Name Screen Shot][product-screenshot]](https://example.com)

Tämän projektin tavoitteena oli tehdä  XX et al tutkimuksen pohjautuen automaattinen analyysiohjelmisto, jonka avulla käyttäjä voi suorittaa ultraääni-ilmakuville automaattisen laatuanalyysin.
Projekti on toteutettu Pythonilla (v3.8) ja analyysi jakautuu kahteen osaan: 1. Ultraääni-ilmakuvien automaattinen analyysi ja 2. tulosten tarkasteluohjelma.

Huom: Tulosten tarkasteluohjelma on kirjoittu Flask frameworkilla ja se on selainpohjainen. Ohjelmistoa ei kuitenkaan ole testattu kuin paikallisesti selaimessa. 

<!-- 
Here's a blank template to get started:
**To avoid retyping too much info. Do a search and replace with your text editor for the following:**
`github_username`, `repo_name`, `twitter_handle`, `email`, `project_title`, `project_description`
-->



<!-- GETTING STARTED -->
## Getting Started

Tiedostosta 'Requirements.txt' löytyy listattuna  on vaadittavat python kirjastomoduulit. Kuvien hakeminen PACS järjestelmästä on toteutettu k-PACS ohjelmistolla.
Käyttäjän pitää määrittää hakemistosijainti (k-PACS ohjelmistossa ..\imagebox), jonne DICOM tiedostot laatukuvista saapuvat.
Analyysiohjelma kuuntelee hakemistoon saapuneita tiedostoja ja mikäli kyseessä in ultraääni dicom tietosto, suorittaa ohjelmisto automaattisen laatuanalyysin. 


1. Kloonaa repository:
   ```sh
   git clone https://github.com/github_username/repo_name.git
   ```
2. Asenna puuttuvat kirjastot omaan virtuaaliympäristöön esim conda:a käyttäen:
```
    conda create --name py38 python=3.8
    source activate py38
    conda install --file requirements.txt.
```


<!-- USAGE EXAMPLES -->

### Käyttö
Ohjelmiston käyttö voidaan jakaa kahteen osaan 1. analyysi ja tulosten tarkasteluohjelma käyttöön. 

## Ilmakuvien analyysiohjelman käyttö
Ennen käyttöönottoa:
Mene hakemistoon ../QA_analysis
'Settings.yaml' tiedostoon käyttäjän pitää määritellä 'data_path' (tiedostosijanti johon dicom tiedostot tulevat) ja 'save_path' (tiedosto jonne analyysitulokset tallennetaan). Lisäksi tiedostoon on asesttu 'threshold_val' (prosenttiluku 10%), joka on kynnystysarvo mittaustuloksen ja nykyisen mittautuloksen välisen suhteellisen eron välille. Mikäli virhe on suurempi kuin asetettu luku kirjautuu 'log_file.txt' tiedostoon lisätietoja poikkeamasta, joka voi tarkastella myös tarkasteluohjelmassa.  

Ohjelman ajaminen komentoriviltä (windows anaconda prompt, linux terminal):
1. aktivoi python virutaaliympäristö: 
    ```
    conda activate py38
    ```
2. Mene hakemistoon, jossa sovellus (main.py) sijaitsee: 
    ```
    cd ...\QA_analysis
    ```
3. Käynnistä ohjelma:
    ```
    python main.py
    ```

##  Tulosten tarkasteluohjelman käyttö
Ennen käyttöönottoa:
'Settings.yaml' tiedostoon käyttäjän pitää määritellä 'path_data' (tiedostosijanti jossa analyysitulokset sijaitsevat) ja 'path_log: ' (sijainti jossa log tiedosto sijaitsee). Lisäksi tiedostoon on asesttu 'n_samples: ' (näytemäärä 4), joka määrittelee kuinka monesta edelliststä laatumittauksesta määritetään keskiarvo ja hajonta arviot trendiseurantaan. 

Ohjelman ajaminen komentoriviltä (windows anaconda prompt, linux terminal):
1. aktivoi python virutaaliympäristö: 
    ```
    conda activate py38
    ```
2. Mene hakemistoon, jossa sovellus (app.py) sijaitsee: 
    ```
    cd ...\Visualization_app
    ```
3. Käynnistä ohjelma:
    ```
    python app.py
    ```
4. Avaa selain ja kopioi lokaali http osoite.  (Huom ohjelmaa on vielä kehitysvaiheessa ja siksi se ei toimi Gunicorn tai vastaavan python verkkopalvelin kautta.)


_Tarkempi suomenkielinen dokumentaatio ohjelmien toiminnasta löytyy ' ../QA_analysis/documentation' ja ' ../Visualization_app/documentation' osioista._


<!-- CONTRIBUTING -->
## Contributing

Tämä projekti pohjautuu avoimeen lähdekoodiin ja siihen saa vapaasti vaikuttaa. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


<!-- LICENSE -->
## License
Mikä lisenssi projektille tulee?
Distributed under the MIT License. See `LICENSE` for more information.


<!-- CONTACT -->
## Contact

Projekti on toteutettu Oulun yliopistollisessa sairaalassa  ja Oulun yliopistossa lääketieteellisen, kuvantamisen  fysiikan ja  tekniikan tutkkimusyksikössä
Projektissa mukana ovat tekemässä Satu Inkinen, Tuomo Starck, Matti Hanni ja Miika Nieminen. 
Satu Inkinen -satu.inkinen [@] oulu.fi
Tuomo Starck -  tuomo.starck [@] ouh.fi
Matti Hanni - [@twitter_handle](https://twitter.com/twitter_handle) - matti.hann [@] ouh.fi
Miika Nieminen - miika.nieminen [@] oulu.fi

Projektin linkki: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)
