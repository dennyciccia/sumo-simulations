import argparse
from vehicles import *

VPH = 1179
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
        # serializzazione
        vList.dump(arguments.filename)