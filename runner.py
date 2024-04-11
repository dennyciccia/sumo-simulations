import argparse
import os
import sys
from TrafficLight import TrafficLight
import traci

from vehicle_generator import *
from vehicles import *


def startProgram():
    traci.start(["sumo-gui", "-c", "sumo_xml_files/config.sumocfg", "--step-length", "0.1", "--waiting-time-memory", "500", "--start"])


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


if __name__ == '__main__':
    # parsing argomenti
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--load-file', dest="filename", required=True)
    arguments = parser.parse_args()

    # inizializzazione e avvio SUMO
    with open(arguments.filename, 'rb') as fd:
        vehicleList = pickle.load(fd)
    generateVehicleTypes(vehicleList)
    startProgram()
    addVehiclesToSimulation(vehicleList)

    smartTrafficLight = TrafficLight(tlID=traci.trafficlight.getIDList()[0])

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
        for indLoopID in ["ILE0dx","ILE0sx","IL-E2dx","IL-E2sx","IL-E1dx","IL-E1sx"]:
            vehicles = traci.inductionloop.getLastStepVehicleIDs(indLoopID)
            for elem in vehicles:
                if elem not in enteredVehicles:
                    enteredVehicles.append(elem)

        smartTrafficLight.performStep()

        # misure
        for vehicleID in enteredVehicles[:]:
            # emissioni
            v = traci.vehicle.getSpeed(vehicleID)
            a = traci.vehicle.getAcceleration(vehicleID)
            s = traci.vehicle.getSlope(vehicleID) # sempre 0.0
            #emission = vehicleList.getVehicle(vehicleID).getCO2emission(v, a, s)/36000 # Kg/100ms
            emission = (traci.vehicle.getCO2Emission(vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg/100ms
            totalEmissions += emission if emission >= 0 else 0
        
            # distanza totale percorsa e tempo totale di attesa
            for indLoopID in ["IL-E0dx","IL-E0sx","ILE2dx","ILE2sx","ILE1dx","ILE1sx"]:
                if vehicleID in traci.inductionloop.getLastStepVehicleIDs(indLoopID):
                    totalDistance += traci.vehicle.getDistance(vehicleID)
                    totalWaitingTime += traci.vehicle.getAccumulatedWaitingTime(vehicleID)
                    if vehicleID in enteredVehicles:
                        enteredVehicles.remove(vehicleID)
            
        # velocità media (degli edge nell'attuale step)
        meanSpeedAtStep = 0
        for edgeID in traci.edge.getIDList():
            meanSpeedAtStep += traci.edge.getLastStepMeanSpeed(edgeID)
        meanSpeedAtStep /= traci.edge.getIDCount()
        # velocità media fino ad ora
        meanSpeed = (meanSpeed * (step-1) + meanSpeedAtStep) / step
    
    # risultati misure
    print(f"Distanza totale percorsa: {totalDistance / 1000} Km")
    print(f"Velocità media: {(meanSpeed) * 3.6} Km/h")
    print(f"Tempo totale di attesa: {totalWaitingTime} s")
    print(f"Emissioni totali di CO2: {totalEmissions} Kg")
    print(f"Emissione media di CO2: {(totalEmissions * 1000) / (totalDistance / 1000)} g/Km")
    """
    with open("log.csv", 'a') as fd:
        print(f"{totalDistance / 1000},{meanSpeed * 3.6},{totalWaitingTime},{totalEmissions},{(totalEmissions * 1000) / (totalDistance / 1000)}", file=fd)
    """
    traci.close()
    sys.stdout.flush()
    