# Simulazioni SUMO
Progetto per il tirocinio di laurea triennale

## Istruzioni

Cambiare mappa:
1. aggiungere i file della mappa nella sua cartella in sumo_xml_files
2. cambiare gli argomenti di traci.start() in runner > startProgram()
3. cambiare gli induction loop dalle variabili INDUCTION_LOOP_START e INDUCTION_LOOP_END in runner
4. cambiare le variabili FIRST_ROUTE e LAST_ROUTE in vehicle_generator
5. generare le routes per i veicoli per quella mappa passando -r a vehicle_generator

Cambiare distribuzione veicoli:
1. eseguire vehicle_generator passando come parametro il nome del file della popolazione
2. cambiare la variabile VEHICLE_DISTRIBUTION in vehicle_generator

Cambiare funzionamento semafori:
1. cambiare la variabile SMART_TRAFFIC_LIGHT in runner
2. cambiare le variabili FIRST_ENHANCEMENT e SECOND_ENHANCEMENT in TrafficLight