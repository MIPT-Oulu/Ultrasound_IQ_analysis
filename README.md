<!-- ENGLISH -->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/">
    <img src="IMG/logo.png" alt="Logo" width="800" height="209">    </a>

  <h2 align="center">Automated ultrasound reverberation air image analysis</h2>

  <p align="center">
    Automated analysis software and web browser-based results viewer for ultrasound reverberation air images
    <br />
    <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation"><strong> Documentation for analysis program (currently only in Finnish)  »</strong></a>  
  <br />
  <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app/documentation"><strong>Documentation for web-based visualization program (currently only in Finnish)»</strong></a>  
    <br />
    <br />
    <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/issues">Report a bug</a>  
    
  </p>
</p>




<details open="open">
  <summary><h2 style="display: inline-block">Contents</h2></summary>
  <ol>
    <li>
      <a href="#About-Project">About Project</a>
    </li>
    <li>
      <a href="#Getting-started">Getting started</a>
    </li>
    <li><a href="#Usage">Usage</a></li>
    <li><a href="#License">License</a></li>
    <li><a href="#Acknowledgements">Acknowledgements</a></li>
    <li><a href="#Contants">Contacts</a></li>
  </ol>
</details>


## About Project

The goal was to make automated analysis software similar to [Horssen et al. 2017](https://doi.org/10.1177/1742271X17733145) that would allow the user to perform automatic image quality analysis based on ultrasound reverberation images for ultrasonic air images.

The software is divided into two parts:
1. [Automatic analysis of ultrasonic air images](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis)
2. [Web-browser for result viewing](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app)

*Please note: Although the results viewer is browser-based, the software has only been tested in a local-environment in a browser/web server.*


## Getting started

The software is implemented in Python (v3.8) and the required python library modules are listed in the file `py38.yml`.

**Software download and creation of a new virtual environment**
1. Clone repository:
   ```sh
   git clone https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis.git
   ```
2. Go to root directory, where `py38.yml` is located:
   ```sh
   cd ..\Ultrasound_IQ_analysis\
   ```
3. Install libraries in your own virtual environment using conda:
```
    conda env create --file py38.yml
    conda activate py38
```

*.../Ultrasound_IQ_analysis/QA_analysis/data/* directory contains two different ultrasound air image examples that can be used to test the operation of the software. 

This software does not support retrieving images directly from the hospital's PACS system. The [Pynetdiccom] (https://pydicom.github.io/pynetdicom/stable/index.html) library can be used to create a DICOM network protocol for an analysis machine.

Retrieval of DICOM images from the PACS system can be done, for example, with the open [k-PACS software] (https://image-systems.biz/products/free-dicom-pacs-tools/k-pacs/).

The user must specify the directory location (in k-PACS software * .. \ imagebox *) where the DICOM files from the quality images arrive and where the watchdog listener path is set.
The analysis program listens to the files received in the directory, and in the case of an ultrasound image dicom file, the software performs an automatic quality analysis.


## Usage
The use of the software can be divided into two parts: 1. analysis program and 2. results review program. 

### 1. Operation and use of the automatic ultrasound air image analysis program
#### Operating principle in brief 
Running the /QA_analysis/main.py file will start the automatic analysis software (see the next section *Usage* for more detailed instructions first). It is based on the [watchdog](https://pypi.org/project/watchdog/) listener, which listens to the directory path to which the quality DICOM imagesare sent after PACS query. If a new file appears in the directory path, the analysis of the image is started. Before analysis, check that: 1. the file is of the DICOM type (there is an **\*.dcm extension**) and 2. the image is an ultrasound air image (**The patientID is in the correct format** as defined in the `Settings.yaml` file). The image is then analyzed with the same parameters as Horssen et al. 2017 has been  described and stored in the result directory based on the following folder hierarchy:

 ```
+-- path_save
|   +-- Instituutio_laitevalmistaja_laitteennimi
|        +-- Transducer_1
|             1
|             2 ... etc.
|        +-- Transducer_2
|        +-- Transducer_3 ... etc.
|   +--   Instituutio2_laitevalmistaja2_laitteennimi2
|        +-- Transducer_1
|             1
|             2 ... etc.
|        +-- Transducer_2 ... etc.
 ```
In other words, each ultrasound transducer of each ultrasound device has its own folder in which the measurements of a different time point are stored with sequential numbering.
The name attributes are automatically retrieved from the image DICOM header data. If the header information is missing, it will be replaced with a generic identifier. However, it is important that each ultrasound device can be directly identified by DICOM header attributes so that the arrangement hierarchy can be implemented automatically. The arrangement hierarchy is utilized in the results viewer.

`Instituutio_laitevalmistaja_laitteennimi`=  Institutional Department Name Attribute  + _ + Manufacturer's Model Name Attiribute+ _ + Station Name Attribute  
`Transducer_1` = TransducerType Attribute + _ + Transducer Frequency Attribute  
File e.g. `1` contains python dictionary in which the analysis results has been stored.

Note: It is very typical that dicom header attribute data is partially missing if, for example, if ultrasound images are transferred to an analysis computer via  proxy server without RIS.

`LUT.xls` is a manual look-up table used when the transduver name is not found in the metadata. The name is combined with the Physical deltaX and Physical deltaY parameters (assuming they are found in the metadata if the ultrasound transducer name is missing). More information (currenly only in finnish) [documentation](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation).

#### Usage
**Before starting the program:**  
Go to the *Ultrasound_IQ_analysis/QA_analysis* directory and open the `Settings.yaml` file.
The user must specify the following information: 
* *data_path:* the directory location where the DICOM files will be sent to.
**Note: The Python filename uses a linux notation, i.e. a slash (/) NOT a backslash. The name must also end with a slash, ie ../XX/ZZ/**
* *save_path:* tiedosto jonne analyysitulokset tallennetaan.   **HOX: Python tiedostonimi käyttää linux notaatiota eli vinoviivaa (/) EI kenoviivaa.**
* *threshold_val:* (percentage threshold value, default = 10%), which performs as a threshold for analysis values between previous measurement and current measurements relative difference. I.e. if the relative error is larger than threshold value the value is written in a separate log file (*log_file.txt*) as additional information for deviating transducers which can be viewed in the web-browser.
* *id_us_analysis:*  e.g. *112233ULTRA* Patient ID identificator, which has to be set same for each air image.
* *path_LUT_table:* Directory path for `LUT.xls` table.

**Running the analyssi program from the command line  (windows anaconda prompt, linux terminal tms.):**
1. Activate the python virtual environment: 
    ```
    conda activate py38
    ```
2. Go to the directory where the software (main.py) is located: 
    ```
    cd ...\QA_analysis
    ```
3. Start the program:
    ```
    python main.py
    ```
4. To test the operation of the program Cut + Paste sample files [Ultrasound_IQ_analysis/QA_analysis/data](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/data) to the `path_data` directory location (Note! 
If the DICOM images are already in the directory when the program is started, the analysis will no automatically start as the listener is just activated. You need to move the files out of the directory and move back so that the watchdog listener "catches" the files and the analysis is started.
  
### 2. Usage of the results web-browser viewer

#### Operating principle in brief
The purpose of the results review program is to monitor the results of the air image analysis. The viewer was done using [Flask](https://flask.palletsprojects.com/en/2.0.x/) microframework and runs in a web browser. 
<img src="IMG/visualization_1.png" alt="Logo" width="800" height="496">  

**Figure 1.** An illustration of the operation of a web browser-based analysis results viewer.

The program is very simple: by selecting *Log* from the top navigation bar (Figure 1 green) it opens log data from the analyzes; To view the results, select *Devices* from the navigation bar at the top (Figure 1 blue), which opens the device list. Selecting the device opens a list of ultrasound transducers and selecting the transducer  opens a list of measurements and trend monitoring.
<img src="IMG/visualization_2.png" alt="Logo" width="500" height="517">  

**Figure 2.** 
An illustration of the operation of a web browser-based analysis results viewer. It has been implemented with [Plotly javascript](https://plotly.com/javascript/) library.  


#### Usage
**Before starting the program:**
Go to the *Ultrasound_IQ_analysis/Visualization_app/* directory and open the `Settings.yaml` file.
The user must specify the following information:
* *path_data:* The file location where the analysis results are located.
* *path_log:* The location where the log file is located(default: `.../Ultrasound_IQ_analysis/QA_analysis/log.txt`).
*  *n_samples:* the number of samples (default = 4), which determines how many of the previous quality measurements are moving averaged and moving standard deviated for the trend monitoring. If there exists  fewer measurements than defined, the program will take as many measurements as the statistics have been measured.

Running a program from the command line (windows anaconda prompt, linux terminal):
1. Activate the python virtual environment: 
    ```
    conda activate py38
    ```
2. Go to the directory where the application[`.../Visualization_app/app.py`](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app) is located: 
    ```
    cd ...\Visualization_app
    ```
3. Run the program:
    ```
    python app.py
    ```
4. Open a browser and copy the local http address into the browser. (Note: the program is still under development and therefore has not been set to run through Gunicorn or a similar python web server.)

_Please note: More detailed documentation (only in Finnish) on the operation of the program can be found
from [`.../QA_analysis/documentation`](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation) and  [`.../Visualization_app/documentation` osioista._](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app/documentation)


## License
This project is MIT licensed. See See the `LICENSE` section for more information.

## Acknowledgements
We would like to thank  Tampere University Hospital for the ultrasound air images as the test material.

## Contacts
The project has been implemented at the University Hospital of Oulu and the Research Unit of Medical, Imaging Physics and Technology at the University of Oulu

The project involves:
Satu Inkinen - satu.inkinen [@] oulu.fi  
Vili Tuppurainen - vili.tuppurainen [@] ppshp.fi
Tuomo Starck - tuomo.starck [@] ppshp.fi  
Matti Hanni  - matti.hanni [@] ppshp.fi  
Miika Nieminen - miika.nieminen [@] ppshp.fi  


Project link: [https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis)

<!-- FINNISH -->

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/"> <!-- mikäli Gihubiin niin päivitä!-->
    <img src="IMG/logo.png" alt="Logo" width="800" height="209">  <!-- mikäli Gihubiin niin päivitä!-->
  </a>

  <h2 align="center">Automaattinen ultraääni-ilmakuvien analyysi</h2>

  <p align="center">
    Ultraääni-ilmakuville automaattinen analyysiohjelmisto ja web-selainpohjainen tulosten tarkasteluohjelma
    <br />
    <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation"><strong>Dokumentaatio analyysiohjelma »</strong></a>  <!-- mikäli Gihubiin niin päivitä!-->
  <br />
  <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app/documentation"><strong>Dokumentaatio visualisointiohjelma »</strong></a>  <!-- mikäli Gihubiin niin päivitä!-->
    <br />
    <br />
    <a href="https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/issues">Raportoi Bugi</a>  <!-- mikäli Gihubiin niin päivitä!-->
    
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Sisällysluettelo</h2></summary>
  <ol>
    <li>
      <a href="#Tietoa-projektista">Tietoa projektista</a>
    </li>
    <li>
      <a href="#Alkuasetukset">Alkuasetukset</a>
    </li>
    <li><a href="#Käyttö">Käyttö</a></li>
    <li><a href="#Lisenssi">Lisenssi</a></li>
    <li><a href="#Acknowledgements">Acknowledgements</a></li>
    <li><a href="#Yhteystiedot">Yhteystiedot</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## Tietoa projektista

Tavoitteena oli tehdä  [Horssen et al. 2017](https://doi.org/10.1177/1742271X17733145) tutkimuksen mukainen automaattinen analyysiohjelmisto, jonka avulla käyttäjä voi suorittaa ultraääni-ilmakuville automaattisen kuvanlaatuanalyysin reverberaatiokuviin perustuen.

Projektin analyysi jakautuu kahteen osaan: 
1. [Ultraääni-ilmakuvien automaattiseen analyysiin](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis)
2. [Web-selainpohjaiseen tulosten tarkasteluohjelmaan](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app)

*Huom: Vaikka tulosten tarkasteluohjelma on selainpohjainen, ohjelmistoa ei kuitenkaan ole testattu kuin paikallisesti selaimessa eikä web-serverikäytössä.*


<!-- GETTING STARTED -->
## Alkuasetukset

Ohjelmisto on toteutettu Pythonilla (v3.8) ja tiedostosta `py38.yml` löytyy listattuna  on vaadittavat python kirjastomoduulit. 

**Ohjelmiston lataus ja uuden virtuaaliympäristön luonti**
1. Kloonaa repository:
   ```sh
   git clone https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis.git
   ```
2. Mene root hakemistoon jossa `py38.yml` sijaitsee:
   ```sh
   cd ..\Ultrasound_IQ_analysis\
   ```
3. Asenna kirjastot omaan virtuaaliympäristöön conda:a käyttäen:
```
    conda env create --file py38.yml
    conda activate py38
```

*.../Ultrasound_IQ_analysis/QA_analysis/data/* hakemistosta löytyy kaksi erilaista ultraääni-ilmakuva esimerkkikuvaa, joilla ohjelmiston toimintaa voi testata. 

Tämä ohjelmisto ei tue kuvien hakemista sairaalan PACS-järjestelmästä suoraan. [Pynetdiccom](https://pydicom.github.io/pynetdicom/stable/index.html) kirjaston avulla voi tehdä DICOM -verkkoprotokollan analyysikoneelle.

Kuvien hakeminen PACS-järjestelmästä voi toteuttaa esimerkiksi avoimella [k-PACS ohjelmistolla](https://image-systems.biz/products/free-dicom-pacs-tools/k-pacs/).
Käyttäjän pitää määrittää hakemistosijainti (k-PACS ohjelmistossa *..\imagebox*), jonne DICOM tiedostot laatukuvista saapuvat ja johon watchdog kuuntelijan polku asetetaan.
Analyysiohjelma kuuntelee hakemistoon saapuneita tiedostoja ja mikäli kyseessä on ultraäänikuva dicom-tietosto, suorittaa ohjelmisto automaattisen laatuanalyysin. 

<!-- USAGE EXAMPLES -->

## Käyttö
Ohjelmiston käyttö voidaan jakaa kahteen osaan 1. analyysiohjelmaan ja  2. tulosten tarkasteluohjelmaan.  

### 1. Ilmakuvien automaattisen analyysiohjelman toiminta ja käyttö
#### Toimintaperiaate lyhyesti
/QA_analysis/main.py tiedostoa ajamalla käynnistetään automaattinen analyysiohjelmisto (ks seuraava osio *käyttö* tarkempi ohjeistus ensin). Se pohjautuu [watchdog](https://pypi.org/project/watchdog/) kuuntelijaan, joka kuuntelee hakemistopolkua, johon laatukuvat tulevat. Mikäli hakemistopolkuun ilmestyy uusi tiedosto aloitetaan kuvalle analyysi. Ennen analyysia tarkistetaan että: 1. tiedosto on DICOM tyyppiä (on **\*.dcm pääte**) ja 2. kuva on ultraääni-ilmakuva (**PatientID on oikeaa muotoa**, joka määritellään `Settings.yaml` tiedostossa). Tämän jälkeen kuvasta analysoidaan samat parametrit mitä Horssen et al. 2017 työssä on kuvattu ja ne tallenetaan tuloshakemistoon pohjautuen seuraavanlaiseen kansiohierarkkiaan:  

 ```
+-- path_save
|   +-- Instituutio_laitevalmistaja_laitteennimi
|        +-- Transducer_1
|             1
|             2 ... etc.
|        +-- Transducer_2
|        +-- Transducer_3 ... etc.
|   +--   Instituutio2_laitevalmistaja2_laitteennimi2
|        +-- Transducer_1
|             1
|             2 ... etc.
|        +-- Transducer_2 ... etc.
 ```
Eli siis jokaisen laitteen anturille tulee oma kansionsa johon eri aikapisteen mittaukset tallennetaan juoksevalla numeroinnilla.
Nimi attribuutit haetaan automaattisesti kuvan dicom tiedoista. Mikäli tieto puuttuu niin se korvataan jollakin geneerisella tunnisteella. Kuitenkin on tärkeää että jokaisen ultraäänilaitteen voi suoraan tunnistaan dicom attribuuteista, jotta järjestelyhierarkkia voidaan toteuttaa automaattisesti. Järjestelyhierarkkiaa käytetään hyödyksi tulosten katseluohjelmassa.

`Instituutio_laitevalmistaja_laitteennimi`=  Institutional Department Name Attribute  + _ + Manufacturer's Model Name Attiribute+ _ + Station Name Attribute  
`Transducer_1` = TransducerType Attribute + _ + Transducer Frequency Attribute  
Tiedostonumero esim. `1` sisältää python dictionaryn, johon analyysitulokset ovat tallennettu. 

Huom: On hyvin tyypillistä että dicom tietoja jää uupumaan jos esimerkiksi UÄ-kuvat siirretään analyysikoneelle edustapalvelimen kautta ilman lähetettä. 
`LUT.xls` on manuaalinen look-up-taulukko, jota käytetään silloin jos anturin nimeä ei löydy metatiedoista. Nimi yhdistetään Physical deltaX ja Physical deltaY parametrien
avulla (oletus että ne löytyvät metatiedoista mikäli anturin nimi puuttuu). Lisätietoja [dokumentaatiosta](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation).

#### Käyttö
**Ennen ohjelman käyttöönottoa:**  
Mene hakemistoon *Ultrasound_IQ_analysis/QA_analysis* ja avaa `Settings.yaml` tiedosto.  
Käyttäjän pitää määritellä seuraavat tiedot:  
* *data_path:*  tiedostosijanti, johon dicom tiedostot tulevat. **HOX: Python tiedostonimi käyttää linux notaatiota eli vinoviivaa (/) EI kenoviivaa. Nimen loppussa pitää myös olla vinoviiva eli  ../XX/ZZ/**  
* *save_path:* tiedosto jonne analyysitulokset tallennetaan.   **HOX: Python tiedostonimi käyttää linux notaatiota eli vinoviivaa (/) EI kenoviivaa.**
* *threshold_val:* (prosenttiluku 10%), joka on kynnystysarvo mittaustuloksen ja nykyisen mittautuloksen välisen suhteellisen eron välille. Mikäli virhe on suurempi kuin asetettu luku kirjautuu *log_file.txt* tiedostoon lisätietoja poikkeamasta, joka voi tarkastella myös tarkasteluohjelmassa.  
* *id_us_analysis:*  Esim. *112233ULTRA* Patient ID tunniste joka pitää laatukuvaa otettaessa asettaa oikein.
* *path_LUT_table:* Hakemistopolku `LUT.xls` taulukkoon.

**Ohjelman ajaminen komentoriviltä (windows anaconda prompt, linux terminal tms.):**
1. Aktivoi python virtuaaliympäristö: 
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
4. Ohjelman toimintaa testataksesi Cut+paste esimerkkitiedostot [Ultrasound_IQ_analysis/QA_analysis/data] (https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/data) `path_data` sijaintiin (Hox! Jos tiedostot ovat jo kansiossa, kun ohjelma käynnistyy ei analyysi starttaa. Tiedostot pitää siirtää hakemistosta pois ja siirtää takaisin hakemistoon jolloin analyysi käynnistyy).
  
### 2. Tulosten tarkasteluohjelman käyttö

#### Toimintaperiaate lyhyesti
Tulosten tarkasteluohjelman tarkoituksena on monitoroida ilmakuvien laatua. Se on tehty [Flask:lla](https://flask.palletsprojects.com/en/2.0.x/) ja toimii web-selaimessa. 
<img src="IMG/visualization_1.png" alt="Logo" width="800" height="496">  

**Kuva 1.** Havainnekuva web-selainpohjaisesta analyysitulosten tarkasteluohjelman toiminnasta.  

Ohjelman käyttö on tehty hyvin yksinkertaiseksi, siten että valitaan yläreunan naviogintipalkista *Log* (kuva 1 vihreä), josta aukeaa lokitiedot analyyseistä. Tulosten tarkasteluun yläreunasta valitaan naviogintipalkista *Devices* (kuva 1 sininen), joka avaa laitelistauksen (ks kansiohierarkkia). Valitsemalla laitteen avautuu listaus antureista ja anturia painamalla avautuu listaus anturille tehdyistä mittauksista ja trendiseurannasta.

<img src="IMG/visualization_2.png" alt="Logo" width="500" height="517">  

**Kuva 2.** Havainnekuva web-selainpohjaisesta analyysitulosten tarkasteluohjelman toiminnasta. Se on toteutettu [Plotly javascript](https://plotly.com/javascript/) kirjastolla.  

#### Käyttö
**Ennen ohjelman käyttöönottoa:**
Mene hakemistoon *Ultrasound_IQ_analysis/Visualization_app/* ja avaa `Settings.yaml` tiedosto.  
Käyttäjän pitää määritellä seuraavat tiedot:  
* *path_data:* Tiedostosijanti jossa analyysitulokset sijaitsevat.
* *path_log:* Sijainti jossa loki-tiedosto sijaitsee (oletus: `.../Ultrasound_IQ_analysis/QA_analysis/log.txt`).
*  *n_samples:* näytemäärä (4), joka määrittelee kuinka monesta edelliststä laatumittauksesta määritetään keskiarvo ja hajonta-arviot trendiseurantaan. Mikäli mittauksia on vähemmän kuin määritelty niin ohjelma ottaa niin monta mittausta statistiikan laskentaa on tehty.

Ohjelman ajaminen komentoriviltä (windows anaconda prompt, linux terminal):
1. aktivoi python virtuaaliympäristö: 
    ```
    conda activate py38
    ```
2. Mene hakemistoon, jossa sovellus [`.../Visualization_app/app.py`](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app) sijaitsee: 
    ```
    cd ...\Visualization_app
    ```
3. Käynnistä ohjelma:
    ```
    python app.py
    ```
4. Avaa selain ja kopioi lokaali http osoite selaimeen.  (Huom. ohjelmaa on vielä kehitysvaiheessa ja siksi se ei toimi Gunicorn tai vastaavan python verkkopalvelimen kautta.)


_Huom: Tarkempi kuvallinen suomenkielinen dokumentaatio ohjelmien toiminnasta löytyy [`.../QA_analysis/documentation`](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/QA_analysis/documentation) ja  [`.../Visualization_app/documentation` osioista._](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis/tree/main/Visualization_app/documentation)

<!-- Lisenssi -->
## Lisenssi
Tämä projekti on MIT lisensoitu. Ks. `LICENSE` osiosta lisätietoja. 

## Acknowledgements
Kiitokset Tampereen yliopistolliselle sairaalalle ultraääni-ilmakuva testiaineistosta.

<!-- Yhteystiedot -->
## Yhteystiedot

Projekti on toteutettu Oulun yliopistollisessa sairaalassa  ja Oulun yliopistossa lääketieteellisen, kuvantamisen  fysiikan ja  tekniikan tutkimusyksikössä.

Projektissa ovat mukana:  
Satu Inkinen - satu.inkinen [@] oulu.fi
Vili Tuppurainen - vili.tuppurainen [@] ppshp.fi
Tuomo Starck - tuomo.starck [@] ppshp.fi  
Matti Hanni  - matti.hanni [@] ppshp.fi  
Miika Nieminen - miika.nieminen [@] ppshp.fi  

Projektin linkki: [https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis](https://github.com/MIPT-Oulu/Ultrasound_IQ_analysis)
