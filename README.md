# Simulazioni SUMO
Progetto per il tirocinio di laurea triennale.

## Funzionalità moduli

### runner.py

Carica i veicoli dal file specificato con `-p` e crea il file 'sumo_xml_files/vehicletypes.rou.xml'. <br/>
Esegue la simulazione con i parametri specificati in `startProgram()` e aggiunge i veicoli alla simulazione. <br/>
Inizializza la lista di semafori smart settando il Program 1 se è stato passato il parametro `-stl ON`. <br/>
Avvia la simulazione e a ogni step:<br/>
    -Aggiorna il set dei veicoli presenti nella simulazione aggiungendo quelli entrati e rimuovendo quelli usciti.<br/>
    -Esegue le operazioni dei semafori.<br/>
    -Misura i valori dei veicoli.<br/>
Finita la simulazione scrive le misure in formato csv nella cartella 'logs'.

### vehicle_generator.py

Definisce la distribuzione dei veicoli con le percentuali per ogni tipo di veicolo.<br/>
Se non viene passato il parametro `-r` il modulo genera la popolazione in formato yaml nel file specificato con `-f` con il numero di veicoli specificato con `-n`.<br/>
Se viene passato il parametro `-r` vengono assegnate le routes alla popolazione di veicoli già esistente specificata con `-f`.

### TrafficLight.py

Definisce l'oggetto TrafficLight che implementa l'algoritmo per ridurre le emissioni.<br/>
L'oggetto viene usato tramite il metodo `performStep()` che esegue la logica dell'algoritmo e applica gli enhancements specificati.

### vehicles.py

Definisce l'oggetto vehicleList e i metodi per accedere a un elemento e caricare una lista da file o caricarla su un file.<br/>
Definisce la classe astratta Vehicle con tutte le proprietà di un veicolo e i metodi per misurare i parametri e per generare un veicoli casuale.<br/>
Definisce gli oggetti dei diversi tipi di veicoli con i rispettivi attributi di classe.<br/>

### DriverProfile.py

Definisce l'oggetto DriverProfile che modella il comportamento di un autista.

## Dati

Per questo progetto sono stati usati i dati ACI relativi al parco veicolare in Italia nel 2022. <br/>
Sono disponibili al link https://www.aci.it/laci/studi-e-ricerche/dati-e-statistiche/autoritratto/autoritratto-2022.html.

## Istruzioni

**Aggiungere mappa:**
1. aggiungere i file della mappa nella sua cartella in 'sumo_xml_files/'
2. generare le routes per la mappa seguendo le apposite istruzioni

**Cambiare distribuzione veicoli:**
1. cambiare le costanti VPH, TOTAL_TIME, VEHICLE_DISTRIBUTION in 'vehicle_generator.py'
2. eseguire 'vehicle_generator.py' passando come parametro il nome del file della popolazione

**Generare popolazione veicoli:**
1. eseguire ```vehicle_generator.py -f "vehicle_population_filename"``` per generare la popolazione
2. eseguire ```vehicle_generator.py -f "vehicle_population_filename" -r FIRST LAST``` per assegnare le route ai veicoli in base alla mappa corrente

**Generare routes per una certa mappa**
1. usare ```python $env:SUMO_HOME/tools/randomTrips.py -n <file.net.xml> -e <numero-routes> -r <file.rou.xml>``` per generare il file delle routes (.rou.xml)
2. rimuovere dal file generato tutti i tag che non sono <route/>
3. usare ```python sumo_xml_files/routes_editor.py -f <file.rou.xml>``` per assegnare gli ID alle routes

### Eseguire una simulazione:

Eseguire ```runner.py -p "path/to/vehicle_population_file" -n MAP_NAME -stl (ON | OFF) -e [1 | 2 | 1 2] [-s]```
   - ```-p``` indica il file contenente la popolazione di veicoli
   - ```-n``` indica il nome della mappa attuale
   - ```-stl``` indica lo stato del semaforo intelligente (ON/OFF)
   - ```-e``` indica quali enhancements usare per il semaforo intelligente (nessuno, 1, 2, 1 2)
   - ```-s``` salta il controllo delle routes (il controllo serve per evitare di dimenticarsi di assegnarle), non consigliato

**Prima di eseguire una simulazione:**
- impostare la mappa
- impostare la distribuzione (numero di veicoli che girano)
- generare la popolazione

### Regole per costruire una mappa

- I semafori devono avere 6 fasi, per ogni direzione una fase di verde, una fase di giallo che dura 3s e una fase di rosso. 
- La prima fase di un semaforo deve essere quella in cui si muove il flusso verticale. 
- I semafori devono avere l'ID uguale a quello dell'incrocio in cui si trovano.

## Requisiti

Il progetto è stato sviluppato su Windows 10 con SUMO 1.20.0.

I requisiti sono specificati nel file `requirements.txt`, per installarli eseguire il comando:

```
pip install -r requirements.txt
```