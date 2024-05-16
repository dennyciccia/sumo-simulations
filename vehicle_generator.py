import random
import traci
from xml.dom import minidom 

from vehicles import *

LANE_NUM = 6
VPH_LANE1 = 324
PERC_LANE1 = {'SmallPetrolCar': 0.210, 'SmallDieselCar': 0.373, 'BigPetrolCar': 0.034, 'BigDieselCar': 0.231, 'MediumVan': 0.139, 'BigVan': 0.009, 'Bus': 0.003}
VPH_LANE2 = 60
PERC_LANE2 = {'SmallPetrolCar': 0.050, 'SmallDieselCar': 0.483, 'BigPetrolCar': 0.000, 'BigDieselCar': 0.200, 'MediumVan': 0.117, 'BigVan': 0.150, 'Bus': 0.000}
VPH_LANE3 = 331
PERC_LANE3 = {'SmallPetrolCar': 0.251, 'SmallDieselCar': 0.363, 'BigPetrolCar': 0.033, 'BigDieselCar': 0.215, 'MediumVan': 0.127, 'BigVan': 0.006, 'Bus': 0.006}
VPH_LANE4 = 67
PERC_LANE4 = {'SmallPetrolCar': 0.119, 'SmallDieselCar': 0.403, 'BigPetrolCar': 0.000, 'BigDieselCar': 0.179, 'MediumVan': 0.119, 'BigVan': 0.179, 'Bus': 0.000}
VPH_LANE5 = 113
PERC_LANE5 = {'SmallPetrolCar': 0.186, 'SmallDieselCar': 0.478, 'BigPetrolCar': 0.000, 'BigDieselCar': 0.257, 'MediumVan': 0.080, 'BigVan': 0.000, 'Bus': 0.000}
VPH_LANE6 = 20
PERC_LANE6 = {'SmallPetrolCar': 0.000, 'SmallDieselCar': 0.800, 'BigPetrolCar': 0.000, 'BigDieselCar': 0.000, 'MediumVan': 0.200, 'BigVan': 0.000, 'Bus': 0.000}

# generazione degli oggetti dei veicoli
def generateRandomVehicles():
    vehicleLists = [VehicleList(), VehicleList(), VehicleList(), VehicleList(), VehicleList(), VehicleList()]
    vehicleCounter = 0

    # generazione di tutti i tipi di veicoli per ogni corsia 
    for lane in range(LANE_NUM):
        for vtype, perc in eval("PERC_LANE"+str(lane+1)).items():
            tmp = list()
            for _ in range(round(eval("VPH_LANE"+str(lane+1))*perc)):
                tmp.append(eval(vtype).generateRandom("vehicle"+str(vehicleCounter), startLane=lane+1))
                vehicleCounter += 1
            vehicleLists[lane].extend(tmp)
        # rimescolamento in modo che i tipi di veicoli partano in ordine sparso
        random.shuffle(vehicleLists[lane])
        # calcolo istanti di partenze
        departCounter = 0
        for v in vehicleLists[lane]:
            v.depart = departCounter
            departCounter += round(3600/eval("VPH_LANE"+str(lane+1)),3)
    
    #unione delle liste
    vehicleList = VehicleList()
    for i in range(LANE_NUM):
        vehicleList.extend(vehicleLists[i])
    
    return vehicleList

# generazione dei percorsi
def generateRoutes(rootXML, routes):    
    route = rootXML.createElement('route')
    route.setAttribute('id', 'route1')
    route.setAttribute('edges', 'E0 E1')
    routes.appendChild(route)

    route = rootXML.createElement('route')
    route.setAttribute('id', 'route2')
    route.setAttribute('edges', 'E0 E2')
    routes.appendChild(route)

    route = rootXML.createElement('route')
    route.setAttribute('id', 'route3')
    route.setAttribute('edges', '-E2 -E0')
    routes.appendChild(route)

    route = rootXML.createElement('route')
    route.setAttribute('id', 'route4')
    route.setAttribute('edges', '-E1 -E0')
    routes.appendChild(route)

    route = rootXML.createElement('route')
    route.setAttribute('id', 'route5')
    route.setAttribute('edges', '-E1 E2')
    routes.appendChild(route)

#generazione dei tipi dei veicoli e scrittura sul file XML
def generateVehicleTypes(vehicleList):
    rootXML = minidom.Document()
    routes = rootXML.createElement('routes')
    rootXML.appendChild(routes)
    generateRoutes(rootXML, routes)

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
        vtype.setAttribute('vClass', str(v.vClass))
        vtype.setAttribute('emissionClass', str(v.emissionClass))
        vtype.setAttribute('color', str(v.color))
        vtype.setAttribute('guiShape', str(v.shape))
        routes.appendChild(vtype)

    #aggiunta dell'XML generato
    with open("port_exp.rou.xml", 'w') as fd:
        fd.write(rootXML.toprettyxml(indent="    "))

#aggiunta veicoli alla simulazione
def addVehiclesToSimulation(vehicleList):
    for v in vehicleList:
        if v.startLane == 1 or v.startLane == 3 or v.startLane == 6:
            departLane = 0
        if v.startLane == 2 or v.startLane == 4 or v.startLane == 5:
            departLane = 1
        traci.vehicle.add(vehID=v.vehicleID, routeID=v.routeID, typeID='vtype-'+v.vehicleID, depart=v.depart, departSpeed=v.initialCarSpeed, departLane=departLane)
