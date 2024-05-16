# Simulazioni SUMO
Progetto per il tirocinio di laurea triennale.

## Istruzioni

**Cambiare mappa:**
1. aggiungere i file della mappa nella sua cartella in 'sumo_xml_files/'
2. per generare le routes per la mappa usare ```python $env:SUMO_HOME/tools/randomTrips.py -n <file.net.xml> -e <numero-routes> -r <file.rou.xml>``` poi assegnare gli id con lo script 'sumo_xml_files/routes_editor.py'
3. generare le routes per i veicoli per quella mappa passando ```-r``` a 'vehicle_generator.py'

**Cambiare distribuzione veicoli:**
1. cambiare le costanti VPH, TOTAL_TIME, VEHICLE_DISTRIBUTION in 'vehicle_generator.py'
2. eseguire 'vehicle_generator.py' passando come parametro il nome del file della popolazione

**Generare popolazione veicoli:**
1. eseguire ```vehicle_generator.py -f "vehicle_population_filename"``` per generare la popolazione
2. eseguire ```vehicle_generator.py -f "vehicle_population_filename" -r FIRST LAST``` per assegnare le route ai veicoli in base alla mappa corrente

### Eseguire una simulazione:

Eseguire ```runner.py -p "path/to/vehicle_population_file" -n MAP_NAME -stl (ON | OFF) -e [1 | 2 | 1 2] [-s]```
   - ```-p``` indica il file contenente la popolazione di veicoli
   - ```-n``` indica il nome della mappa attuale
   - ```-stl``` indica lo stato del semaforo intelligente (ON/OFF)
   - ```-e``` indica quali enhancements usare per il semaforo intelligente (nessuno, 1, 2, 1 2)
   - ```-s``` salta il controllo delle routes (il controllo serve per evitare di dimenticarsi di generarle), non consigliato

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