import argparse
import yaml
from datetime import datetime
import random
import traci
from xml.dom import minidom 

from vehicles import *

VEHICLETYPES_FILE_PATH = "sumo_xml_files/vehicletypes.rou.xml"
VPH = 915
TOTAL_TIME = 3600 # secondi
N_VEHICLES = (VPH * TOTAL_TIME) / 3600
VEHICLE_DISTRIBUTION = {'PassengerCar': 75.890, 'LightCommercialVehicle': 8.343, 'HeavyGoodsVehicle': 1.393, 'Truck': 0.403, 'MotorCycle': 13.781, 'Bus': 0.189}

# generazione degli oggetti dei veicoli
def generateRandomVehicles():
    vehicleList = VehicleList()
    vehicleCounter = 0

    # generazione di tutti i tipi di veicoli
    for vtype, perc in VEHICLE_DISTRIBUTION.items():
        for _ in range(round(N_VEHICLES*perc)):
            vehicleList.append(eval(vtype).generateRandom("vehicle"+str(vehicleCounter)))
            vehicleCounter += 1

    # rimescolamento in modo che i tipi di veicoli partano in ordine sparso
    random.shuffle(vehicleList)

    # calcolo istanti di partenze
    for v in vehicleList:
        v.depart = randint(0, TOTAL_TIME)
    
    return vehicleList

# generazione dei tipi dei veicoli e scrittura sul file XML
def generateVehicleTypes(vehicleList):
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
    with open(VEHICLETYPES_FILE_PATH, 'w') as fd:
        fd.write(rootXML.toprettyxml(indent="    "))

# aggiunta veicoli alla simulazione
def addVehiclesToSimulation(vehicleList):
    for v in vehicleList:
        departLane = randint(0,1)
        traci.vehicle.add(vehID=v.vehicleID, routeID=v.routeID, typeID='vtype-'+v.vehicleID, depart=v.depart, departSpeed=v.initialSpeed, departLane=departLane)

def generate_routes(filename, first_route, last_route):
    vehicleList = VehicleList.load(filename)

    for v in vehicleList:
        v.routeID = randint(first_route, last_route)

    vehicleList.dump(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--dest-file', dest="filename", required=True)
    parser.add_argument('-r', '--generate-routes', nargs=2, type=int, dest="routes", metavar=("first route", "last route"), required=False)
    arguments = parser.parse_args()

    if arguments.routes is not None:
        # generazione delle route per la mappa attuale specificando first e last route
        first, last = arguments.routes
        generate_routes(arguments.filename, first, last)
    else:
        # generazione della popolazione
        vList = generateRandomVehicles()
        # generazione del file dei vehicletypes
        generateVehicleTypes(vList)
        # serializzazione
        vList.dump(arguments.filename)