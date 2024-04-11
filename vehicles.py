from abc import ABC
from random import randint
import numpy as np

from profiles import DriverProfile


class VehicleList(list):
    def getVehicle(self, vehicleID):
        for v in self:
            if v.vehicleID == vehicleID:
                return v


class VehicleClass(ABC):
    def __init__(self, id, r, l, w, ics, hst, a, nga, ba, fba, A, B, C, dp, d, sl):
        self.__vehicleID = id
        self.__routeID = r
        self.__carLength = l
        self.__carWeight = w
        self.__initialCarSpeed = ics
        self.__hasStartStop = hst
        self.__carAcceleration = a
        self.__noGasAcceleration = nga
        self.__brakingAcceleration = ba
        self.__fullBrakingAcceleration = fba
        self.__A = A
        self.__B = B
        self.__C = C
        self.__driverProfile = dp
        self.__depart = d
        self.__startLane = sl
    
    @property
    def vehicleID(self):
        return self.__vehicleID
    
    @property
    def routeID(self):
        return self.__routeID

    @property
    def carLength(self): # m
        return self.__carLength
    
    @property
    def carWeight(self): # Kg
        return self.__carWeight
    
    @property
    def initialCarSpeed(self):
        return self.__initialCarSpeed
    
    @property
    def hasStartStop(self):
        return self.__hasStartStop
    
    @property
    def carAcceleration(self):
        return self.__carAcceleration
    
    @property
    def noGasAcceleration(self):
        return self.__noGasAcceleration
    
    @property
    def brakingAcceleration(self):
        return self.__brakingAcceleration

    @property
    def fullBrakingAcceleration(self):
        return self.__fullBrakingAcceleration
    
    @property
    def A(self):
        return self.__A
    
    @property
    def B(self):
        return self.__B
    
    @property
    def C(self):
        return self.__C
    
    @property
    def driverProfile(self):
        return self.__driverProfile
    
    @property
    def depart(self):
        return self.__depart
    
    @depart.setter
    def depart(self, value):
        self.__depart = value

    @property
    def startLane(self):
        return self.__startLane

    @staticmethod
    def VSP(velocity, acceleration, slope): # W/Kg
        return velocity*(1.1*acceleration + 9.81*slope + 0.132) + 0.000302*(velocity**3)

    def FC(self, vsp): # g/h
        return ( ( self.A*(vsp**2) + self.B*vsp + self.C ) * self.carWeight ) / 1000

    @classmethod
    def generateRandom(cls, vehicleID, startLane, depart=-1):
        # profilo dell'autista
        driverProfile = DriverProfile.generateRandom()

        # percorso
        if startLane == 1:
            routeID = "route" + str(randint(1,2))
        if startLane == 2:
            routeID = "route2"
        if startLane == 3 or startLane == 4:
            routeID = "route3"
        if startLane == 5:
            routeID = "route4"
        if startLane == 6:
            routeID = "route5"

        # lunghezza
        carLength = np.random.normal(loc=4.6*cls.lengthMult, size=1)[0]

        # peso
        carWeight = np.random.normal(loc=1600*cls.weightMult, scale=200, size=1)[0]

        # velocità iniziale
        initialCarSpeed = (50.00 / 3.6) * driverProfile.speedLimitComplianceFactor

        # start&stop
        hasStartStop = True if randint(0,1) == 1 else False

        # accelerazione
        carAcceleration = np.random.normal(loc=3, scale=2, size=1)[0]
        carAcceleration = 2.1 if carAcceleration < 2.1 else carAcceleration

        # decelerazione
        noGasAcceleration = np.random.normal(loc=0.5, size=1)[0]
        noGasAcceleration = 0.5 if noGasAcceleration < 0.5 else noGasAcceleration
        brakingAcceleration = abs(np.random.normal(loc=3.0, size=1)[0])
        fullBrakingAcceleration = np.random.normal(loc=6, size=1)[0]

        return cls(vehicleID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAcceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane)


class SmallPetrolCar(VehicleClass):
    A = 0.2403
    B = 227
    C = 595
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    color = "#FFFF00"
    shape = "passenger/sedan"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, SmallPetrolCar.A, SmallPetrolCar.B, SmallPetrolCar.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): # Kg/h
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * SmallPetrolCar.ConversionFactor


class SmallDieselCar(VehicleClass):
    A = 1.0601
    B = 168
    C = 379
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    color = "#00BFFF"
    shape = "passenger/sedan"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, SmallDieselCar.A, SmallDieselCar.B, SmallDieselCar.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * SmallDieselCar.ConversionFactor
    

class BigPetrolCar(VehicleClass):
    A = 0.2471
    B = 210
    C = 609
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#FF4500"
    shape = "passenger/hatchback"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, BigPetrolCar.A, BigPetrolCar.B, BigPetrolCar.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): # Kg/h
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigPetrolCar.ConversionFactor

    
class BigDieselCar(VehicleClass):
    A = 0.6787
    B = 174
    C = 384
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#8A2BE2"
    shape = "passenger/hatchback"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, BigDieselCar.A, BigDieselCar.B, BigDieselCar.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigDieselCar.ConversionFactor
    

class MediumVan(VehicleClass):
    A = 1.3313
    B = 166
    C = 357
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#DC143C"
    shape = "delivery"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * MediumVan.ConversionFactor
    

class BigVan(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.50
    weightMult = 1.60
    color = "#FFFFFF"
    shape = "delivery"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigVan.ConversionFactor
    

class Bus(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 3
    weightMult = 11
    color = "#7CFC00"
    shape = "bus"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * Bus.ConversionFactor