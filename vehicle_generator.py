import argparse
import pickle
from datetime import datetime
import random
import traci
from xml.dom import minidom 

from vehicles import *

VEHICLE_POPULATION_FILE_PATH = "data/vehicles_population" + str(datetime.now().timestamp()) + ".dat"
ROUTE_FILE_PATH = "sumo_xml_files/vehicletypes.rou.xml"
VPH = 500
VEHICLE_DISTRIBUTION = {'SmallPetrolCar': 0.210, 'SmallDieselCar': 0.373, 'BigPetrolCar': 0.034, 'BigDieselCar': 0.231, 'MediumVan': 0.139, 'BigVan': 0.009, 'Bus': 0.003}

# generazione degli oggetti dei veicoli
def generateRandomVehicles():
    vehicleList = VehicleList()
    vehicleCounter = 0

    # generazione di tutti i tipi di veicoli
    for vtype, perc in VEHICLE_DISTRIBUTION.items():
        for _ in range(round(VPH*perc)):
            vehicleList.append(eval(vtype).generateRandom("vehicle"+str(vehicleCounter)))
            vehicleCounter += 1

    # rimescolamento in modo che i tipi di veicoli partano in ordine sparso
    random.shuffle(vehicleList)

    # calcolo istanti di partenze ----- TODO:da sistemare
    departCounter = 0
    for v in vehicleList:
        v.depart = departCounter
        departCounter += round(3600 / VPH, 3)
    
    return vehicleList

#generazione dei tipi dei veicoli e scrittura sul file XML
def generateVehicleTypes(vehicleList):
    rootXML = minidom.Document()
    routes = rootXML.createElement('routes')
    rootXML.appendChild(routes)

    #creazione vTypes
    for v in vehicleList:
        vtype = rootXML.createElement('vType')
        vtype.setAttribute('id', 'vtype-'+v.vehicleID)
        vtype.setAttribute('length', str(v.carLength))
        vtype.setAttribute('mass', str(v.carWeight))
        vtype.setAttribute('accel', str(v.carAcceleration))
        vtype.setAttribute('decel', str(v.brakingAcceleration))
        vtype.setAttribute('emergencyDecel', str(v.fullBrakingAcceleration))
        vtype.setAttribute('minGap', str(v.driverProfile.securityDistanceToObjectAhead))
        vtype.setAttribute('color', str(v.color))
        vtype.setAttribute('guiShape', str(v.shape))
        routes.appendChild(vtype)

    #aggiunta dell'XML generato
    with open(ROUTE_FILE_PATH, 'w') as fd:
        fd.write(rootXML.toprettyxml(indent="    "))

#aggiunta veicoli alla simulazione
def addVehiclesToSimulation(vehicleList):
    for v in vehicleList:
        departLane = randint(0,1)
        traci.vehicle.add(vehID=v.vehicleID, routeID=v.routeID, typeID='vtype-'+v.vehicleID, depart=v.depart, departSpeed=v.initialCarSpeed, departLane=departLane)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--dest-file', default=VEHICLE_POPULATION_FILE_PATH, dest="filename", required=False)
    arguments = parser.parse_args()

    # generazione della popolazione
    vList = generateRandomVehicles()

    # scrittura su file
    with open(arguments.filename, 'wb') as fd:
        pickle.dump(vList, fd)
