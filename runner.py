import argparse
import os
import sys
from TrafficLight import TrafficLight
import traci
import yaml

from vehicle_generator import *
from vehicles import *


SMART_TRAFFIC_LIGHT_ON = False


def startProgram():
    traci.start(["sumo-gui", "-c", "sumo_xml_files/4way_crossing/4way_crossing.sumocfg", "--step-length", "0.1", "--waiting-time-memory", "500", "--start"])


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


# constanti
INDUCTION_LOOP_START = ["ILE1dx","ILE1sx","ILE2dx","ILE2sx","ILE3dx","ILE3sx","ILE4dx","ILE4sx"]
INDUCTION_LOOP_END = ["IL-E1dx","IL-E1sx","IL-E2dx","IL-E2sx","IL-E3dx","IL-E3sx","IL-E4dx","IL-E4sx"]


if __name__ == '__main__':
    # parsing argomenti
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--population-file', dest="population_file", required=True)
    parser.add_argument('-l', '--log-file', dest="log_file", required=True)
    arguments = parser.parse_args()

    # inizializzazione e avvio SUMO
    with open(arguments.population_file, 'r') as fd:
        vehicleList = yaml.unsafe_load(fd)
    generateVehicleTypes(vehicleList)
    startProgram()
    addVehiclesToSimulation(vehicleList)

    smartTrafficLight = list()
    for tl in traci.trafficlight.getIDList():
        smartTrafficLight.append(TrafficLight(tlID=tl))
        if SMART_TRAFFIC_LIGHT_ON:
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
        for indLoopID in INDUCTION_LOOP_START:
            vehicles = traci.inductionloop.getLastStepVehicleIDs(indLoopID)
            for elem in vehicles:
                if elem not in enteredVehicles:
                    enteredVehicles.append(elem)

        # step semafori
        if SMART_TRAFFIC_LIGHT_ON:
            for trafficLight in smartTrafficLight:
                trafficLight.performStep()

        # misure
        for vehicleID in enteredVehicles[:]:
            vehicleList.getVehicle(vehicleID).doMeasures(step)

            # emissioni (misure intermedie)
            v = traci.vehicle.getSpeed(vehicleID)
            a = traci.vehicle.getAcceleration(vehicleID)
            s = traci.vehicle.getSlope(vehicleID) # sempre 0.0
            #emission = vehicleList.getVehicle(vehicleID).getCO2emission(v, a, s)/36000 # Kg/100ms
            emission = (traci.vehicle.getCO2Emission(vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg/100ms
            totalEmissions += emission if emission >= 0 else 0
        
            # distanza totale percorsa e tempo totale di attesa
            for indLoopID in INDUCTION_LOOP_END:
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
    with open(arguments.log_file, 'a') as fd:
        for v in vehicleList:
            print(f"{v.vehicleID},{v.totalDistance / 1000},{v.totalTravelTime},{v.totalWaitingTime},{v.meanSpeed * 3.6},{v.totalCO2Emissions},{v.totalCOEmissions},{v.totalHCEmissions},{v.totalPMxEmissions},{v.totalNOxEmissions},{v.totalFuelConsumption},{v.totalNoiseEmission}", file=fd)

    traci.close()
    sys.stdout.flush()
    