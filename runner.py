import argparse
import os
import sys
import time
import traci
from TrafficLight import TrafficLight
from vehicle_generator import *
from vehicles import *


def startProgram(mapname):
    traci.start(["sumo-gui", "-c", "sumo_xml_files/" + mapname + "/" + mapname + ".sumocfg", "--step-length", "0.1", "--waiting-time-memory", "1000", "--start", "--quit-on-end"])


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


if __name__ == '__main__':
    # parsing argomenti
    parser = argparse.ArgumentParser(description="Modulo per eseguire le simulazioni")
    parser.add_argument('-p', '--population-file', dest="population_file", required=True, metavar="path/to/vehicle_population_file", help="File della popolazione dei veicoli")
    parser.add_argument('-n', '--map-name', dest="mapname", required=True, metavar="NAME", help="Nome dello scenario")
    parser.add_argument('-stl', '--smart-traffic-light', choices=["ON", "OFF"], dest="smart_traffic_light", required=True, metavar="ON | OFF", help="Accensione o meno del semaforo intelligente")
    parser.add_argument('-e', '--enhancements', choices=[1,2], nargs='*', type=int, dest="enhancements", required=False, metavar="[1] [2]", help="Numero del migliramento dell'alogritmo che si vuole usare (1, 2, 1 2)")
    parser.add_argument('-s', '--skip-route-check', action="store_true", dest="skip_route_check", required=False, help="Controllo delle routes")
    arguments = parser.parse_args()

    if arguments.enhancements is not None and len(arguments.enhancements) > 2:
        print("Massimo due argomenti per -e / --enhancements")
        exit()

    exec("from induction_loop_constants import INDUCTION_LOOP_START_" + arguments.mapname + ", INDUCTION_LOOP_END_" + arguments.mapname)

    # inizializzazione
    vehicleList = VehicleList.load(arguments.population_file)

    # controllo routes
    if not arguments.skip_route_check:
        route_set = set()
        for v in vehicleList:
            route_set.add(v.routeID)
        with open("sumo_xml_files/" + arguments.mapname + "/" + arguments.mapname + ".rou.xml", 'r') as fd:
            lines = len(fd.readlines())
        if lines-3 != len(route_set): print(f"\033[91m {'!!! Routes non corrette !!!'}\033[00m")

    # avvio SUMO
    startProgram(arguments.mapname)
    addVehiclesToSimulation(vehicleList)

    smartTrafficLight = list()
    for tl in traci.trafficlight.getIDList():
        smartTrafficLight.append(TrafficLight(tlID=tl, enhancements=(arguments.enhancements if arguments.enhancements is not None else [])))
        if arguments.smart_traffic_light == "ON":
            traci.trafficlight.setProgram(tl, "1")
        else:
            traci.trafficlight.setProgram(tl, "0")

    totalEmissions = 0 # Kg
    totalDistance = 0 # m
    enteredVehicles = list()
    step = 0
    meanSpeed = 0
    totalWaitingTime = 0

    # avvio simulazione
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        step += 1

        # veicoli entrati nella simulazione
        for indLoopID in eval("INDUCTION_LOOP_START_" + arguments.mapname):
            vehicles = traci.inductionloop.getLastStepVehicleIDs(indLoopID)
            for elem in vehicles:
                if elem not in enteredVehicles:
                    enteredVehicles.append(elem)

        # step semafori
        if arguments.smart_traffic_light == "ON":
            for trafficLight in smartTrafficLight:
                trafficLight.performStep()

        # misure
        for vehicleID in enteredVehicles[:]:
            vehicleList.getVehicle(vehicleID).doMeasures(step)

            # emissioni (misure intermedie)
            #v = traci.vehicle.getSpeed(vehicleID)
            #a = traci.vehicle.getAcceleration(vehicleID)
            #s = traci.vehicle.getSlope(vehicleID) # sempre 0.0
            #emission = vehicleList.getVehicle(vehicleID).getCO2emission(v, a, s)/36000 # Kg/100ms
            #totalEmissions += emission if emission >= 0 else 0
            emission = (traci.vehicle.getCO2Emission(vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg/100ms
            totalEmissions += emission

            # distanza totale percorsa e tempo totale di attesa
            for indLoopID in eval("INDUCTION_LOOP_END_" + arguments.mapname):
                if vehicleID in traci.inductionloop.getLastStepVehicleIDs(indLoopID):
                    vehicleList.getVehicle(vehicleID).doMeasures(step, final=True)

                    # (misure intermedie)
                    totalDistance += traci.vehicle.getDistance(vehicleID)
                    totalWaitingTime += traci.vehicle.getAccumulatedWaitingTime(vehicleID)

                    if vehicleID in enteredVehicles:
                        enteredVehicles.remove(vehicleID)
            
        # velocità media (degli edge nell'attuale step) (misure intermedie)
        meanSpeedAtStep = 0
        for edgeID in traci.edge.getIDList():
            meanSpeedAtStep += traci.edge.getLastStepMeanSpeed(edgeID)
        meanSpeedAtStep /= traci.edge.getIDCount()
        # velocità media fino a ora
        meanSpeed = (meanSpeed * (step-1) + meanSpeedAtStep) / step
    
    # risultati misure intermedie
    print(f"Distanza totale percorsa: {totalDistance / 1000} Km")
    print(f"Velocità media: {meanSpeed * 3.6} Km/h")
    print(f"Tempo totale di attesa: {totalWaitingTime} s")
    print(f"Emissioni totali di CO2: {totalEmissions} Kg")
    print(f"Emissione media di CO2: {(totalEmissions * 1000) / (totalDistance / 1000)} g/Km")

    # scrittura dati dei veicoli
    if not os.path.exists("logs/" + arguments.mapname):
        os.mkdir("logs/" + arguments.mapname)

    logfile = "logs/" + arguments.mapname + "/log_stl" + arguments.smart_traffic_light
    if arguments.enhancements is not None and len(arguments.enhancements) > 0:
        logfile += "_e"
        for e in arguments.enhancements: logfile += str(e)
    logfile += '_' + str(int(time.time())) + ".csv"

    with open(logfile, 'w') as fd:
        print("VehicleID;Distanza percorsa (m);Tempo di percorrenza (s);Tempo di attesa (s);Velocita media (m/s);Emissioni di CO2 (g);Emissioni di CO (g);Emissioni di HC (g);Emissioni di PMx (g);Emissioni di NOx (g);Consumo di carburante (g);Consumo elettrico (Wh);Emissione di rumore (dBA)", file=fd)
        for v in vehicleList:
            print(f"{v.vehicleID};{v.totalDistance};{v.totalTravelTime};{v.totalWaitingTime};{v.meanSpeed};{v.totalCO2Emissions};{v.totalCOEmissions};{v.totalHCEmissions};{v.totalPMxEmissions};{v.totalNOxEmissions};{v.totalFuelConsumption};{v.totalElectricityConsumption};{v.totalNoiseEmission}", file=fd)

    traci.close()
    sys.stdout.flush()
