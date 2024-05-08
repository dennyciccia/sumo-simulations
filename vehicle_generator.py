import argparse
from xml.dom import minidom 

from vehicles import *

VEHICLETYPES_FILE_PATH = "sumo_xml_files/vehicletypes.rou.xml"
VPH = 915
TOTAL_TIME = 3600 # secondi
N_VEHICLES = (VPH * TOTAL_TIME) / 3600
VEHICLE_DISTRIBUTION = {'PassengerCar': 0.75890, 'LightCommercialVehicle': 0.08343, 'HeavyGoodsVehicle': 0.01393, 'Truck': 0.00403, 'MotorCycle': 0.13781, 'Bus': 0.00189}

# generazione degli oggetti dei veicoli
def generateRandomVehicles():
    vehicleList = VehicleList()
    vehicleCounter = 0

    # generazione di tutti i tipi di veicoli
    for vtype, perc in VEHICLE_DISTRIBUTION.items():
        for _ in range(round(N_VEHICLES*perc)):
            vehicleList.append(eval(vtype).generateRandom("vehicle"+str(vehicleCounter)))
            vehicleCounter += 1

    # assegnamento istanti di partenze casuali
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

def generate_routes(filename, first_route, last_route):
    vehicleList = VehicleList.load(filename)

    for v in vehicleList:
        v.routeID = "route" + str(randint(first_route, last_route))

    vehicleList.dump(filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Modulo per generare i veicoli")
    parser.add_argument('-f', '--dest-file', dest="filename", required=True, metavar="path/to/vehicle_population_filename.yaml", help="File in cui vengono salvati i veicoli")
    parser.add_argument('-r', '--generate-routes', nargs=2, type=int, dest="routes", required=False, metavar=('N', 'M'), help="ID numerici della prima e dell'ultima route per la mappa attuale")
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