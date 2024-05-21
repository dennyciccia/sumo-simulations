# Simulazioni SUMO
Progetto per il tirocinio di laurea triennale.

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