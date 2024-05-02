# Simulazioni SUMO
Progetto per il tirocinio di laurea triennale

## Istruzioni

Cambiare mappa:
1. aggiungere i file della mappa nella sua cartella in sumo_xml_files
2. cambiare gli argomenti di traci.start() in runner > startProgram()
3. cambiare gli induction loop dalle variabili INDUCTION_LOOP_START e INDUCTION_LOOP_END in runner
4. generare le routes per i veicoli per quella mappa passando -r a vehicle_generator

Cambiare distribuzione veicoli:
1. cambiare le costanti VPH, TOTAL_TIME, VEHICLE_DISTRIBUTION in vehicle_generator
2. eseguire vehicle_generator passando come parametro il nome del file della popolazione

## Argomenti

