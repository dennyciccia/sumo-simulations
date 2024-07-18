import argparse
import os
import sys
import time
import random
import traci
from xml.dom import minidom
from TrafficLightV2 import TrafficLightV2
from vehicles import VehicleList


def startProgram(mapname):
    traci.start(["sumo-gui", "-c", "sumo_xml_files/" + mapname + "/" + mapname + ".sumocfg", "--waiting-time-memory", "3000", "--start", "--quit-on-end"])


def generateVehicleTypesXML(vehicleList):
    rootXML = minidom.Document()
    routes = rootXML.createElement('routes')
    rootXML.appendChild(routes)

    # creazione vTypes
    for v in vehicleList:
        vtype = rootXML.createElement('vType')
        vtype.setAttribute('id', 'vtype-'+v.vehicleID)
        vtype.setAttribute('length', str(v.length))
        vtype.setAttribute('mass', str(v.weight))
        vtype.setAttribute('accel', str(v.acceleration))
        vtype.setAttribute('decel', str(v.brakingAcceleration))
        vtype.setAttribute('emergencyDecel', str(v.fullBrakingAcceleration))
        vtype.setAttribute('minGap', str(v.driverProfile.securityDistanceToObjectAhead))
        vtype.setAttribute('vClass', str(v.vClass))
        vtype.setAttribute('emissionClass', str(v.emissionClass))
        vtype.setAttribute('color', str(v.color))
        vtype.setAttribute('guiShape', str(v.shape))
        routes.appendChild(vtype)

    # scrittura dell'XML generato
    with open("sumo_xml_files/vehicletypes.rou.xml", 'w') as fd:
        fd.write(rootXML.toprettyxml(indent="    "))


def addVehiclesToSimulation(vehicleList):
    for v in vehicleList:
        #departLane = random.randint(0, 1)
        departLane = 0
        traci.vehicle.add(vehID=v.vehicleID, routeID=v.routeID, typeID='vtype-'+v.vehicleID, depart=v.depart, departSpeed=v.initialSpeed, departLane=departLane)


def main():
    # parsing argomenti
    parser = argparse.ArgumentParser(description="Modulo per eseguire le simulazioni")
    parser.add_argument('-p', '--population-file', dest="population_file", required=True, metavar="path/to/vehicle_population_file", help="File della popolazione dei veicoli")
    parser.add_argument('-n', '--map-name', dest="mapname", required=True, metavar="NAME", help="Nome dello scenario")
    parser.add_argument('-stl', '--smart-traffic-light', choices=["ON", "OFF"], dest="smart_traffic_light", required=True, metavar="ON | OFF", help="Accensione o meno del semaforo intelligente")
    parser.add_argument('-e', '--enhancements', choices=[1,2,3], nargs='*', type=int, dest="enhancements", required=False, metavar="[1] [2] [3]", help="Numero del migliramento dell'alogritmo che si vuole usare (1, 2, 3)")
    parser.add_argument('-s', '--skip-route-check', action="store_true", dest="skip_route_check", required=False, help="Controllo delle routes")
    arguments = parser.parse_args()

    if arguments.enhancements is not None and len(arguments.enhancements) > 3:
        print("Massimo tre argomenti per -e / --enhancements")
        exit()

    # inizializzazione veicoli
    vehicleList = VehicleList.load(arguments.population_file)

    # controllo routes
    if not arguments.skip_route_check and "manhattan" not in arguments.mapname and "bologna" not in arguments.mapname:
        route_set = set()
        for v in vehicleList:
            route_set.add(v.routeID)
        with open("sumo_xml_files/" + arguments.mapname + "/" + arguments.mapname + ".rou.xml", 'r') as fd:
            lines = len(fd.readlines())
        if lines-3 != len(route_set): print(f"\033[91m {'!!! Routes non corrette !!!'}\033[00m")

    # generazione del file dei vehicletypes
    generateVehicleTypesXML(vehicleList)

    # avvio SUMO
    startProgram(arguments.mapname)
    addVehiclesToSimulation(vehicleList)

    # inizializzazione semafori
    smartTrafficLight = list()
    for tl in traci.trafficlight.getIDList():
        if arguments.smart_traffic_light == "ON" and len(traci.trafficlight.getAllProgramLogics(tl)) > 1:
            smartTrafficLight.append(TrafficLightV2(tlID=tl, enhancements=(arguments.enhancements if arguments.enhancements is not None else [])))
            traci.trafficlight.setProgram(tl, "1")
        else:
            traci.trafficlight.setProgram(tl, "0")

    activeVehicles = set()

    # avvio simulazione
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        #aggiornamento set
        activeVehicles.update(traci.simulation.getDepartedIDList())
        activeVehicles.difference_update(traci.simulation.getArrivedIDList())

        # step semafori
        if arguments.smart_traffic_light == "ON":
            for trafficLight in smartTrafficLight:
                trafficLight.performStep()

        # misure
        for vehicle in activeVehicles:
            vehicleList.getVehicle(vehicle).doMeasures()

    # scrittura dati dei veicoli
    if not os.path.exists("logs/" + arguments.mapname):
        os.mkdir("logs/" + arguments.mapname)

    logfile = "logs/" + arguments.mapname + "/log_stl" + arguments.smart_traffic_light
    if arguments.enhancements is not None and len(arguments.enhancements) > 0:
        logfile += "_e"
        for e in arguments.enhancements: logfile += str(e)
    logfile += '_vp' + arguments.population_file[23:-5] + '_' + str(int(time.time())) + ".csv"

    with open(logfile, 'w') as fd:
        print("VehicleID;Distanza percorsa (m);Tempo di percorrenza (s);Tempo di attesa (s);Velocita media (m/s);Emissioni di CO2 (g);Emissioni di CO (g);Emissioni di HC (g);Emissioni di PMx (g);Emissioni di NOx (g);Consumo di carburante (g);Consumo elettrico (Wh);Emissione di rumore (dBA)", file=fd)
        for v in vehicleList:
            print(f"{v.vehicleID};{v.totalDistance};{v.totalTravelTime};{v.totalWaitingTime};{v.meanSpeed};{v.totalCO2Emissions};{v.totalCOEmissions};{v.totalHCEmissions};{v.totalPMxEmissions};{v.totalNOxEmissions};{v.totalFuelConsumption};{v.totalElectricityConsumption};{v.totalNoiseEmission}", file=fd)

    traci.close()
    sys.stdout.flush()


if __name__ == "__main__":
    main()
