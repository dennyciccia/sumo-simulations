import pickle
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
    def __init__(self, id, r, l, w, ics, hst, a, nga, ba, fba, dp, d=-1):
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
        self.__driverProfile = dp
        self.__depart = d

    """def __dict__(self):
        obj_dict = dict()

        obj_dict["vehicleID"] = self.vehicleID
        obj_dict["routeID"] = self.routeID
        obj_dict["carLength"] = self.carLength
        obj_dict["carWeight"] = self.carWeight
        obj_dict["initialCarSpeed"] = self.initialCarSpeed
        obj_dict["hasStartStop"] = self.hasStartStop
        obj_dict["carAcceleration"] = self.carAcceleration
        obj_dict["noGasAcceleration"] = self.noGasAcceleration
        obj_dict["brakingAcceleration"] = self.brakingAcceleration
        obj_dict["fullBrakingAcceleration"] = self.fullBrakingAcceleration
        obj_dict["depart"] = self.depart
        obj_dict["driverProfile"] = self.driverProfile.__dict__()

        return obj_dict"""

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
    def driverProfile(self):
        return self.__driverProfile
    
    @property
    def depart(self):
        return self.__depart
    
    @depart.setter
    def depart(self, value):
        self.__depart = value

    @staticmethod
    def VSP(velocity, acceleration, slope): # W/Kg
        return velocity*(1.1*acceleration + 9.81*slope + 0.132) + 0.000302*(velocity**3)

    def FC(self, vsp): # g/h
        return ( ( self.A*(vsp**2) + self.B*vsp + self.C ) * self.carWeight ) / 1000

    def getCO2emission(self, velocity, acceleration, slope): # Kg/h
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * self.ConversionFactor

    @classmethod
    def generateRandom(cls, vehicleID):
        # profilo dell'autista
        driverProfile = DriverProfile.generateRandom()

        # percorso
        routeID = "route" + str(randint(1,12))

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

        return cls(vehicleID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAcceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile)


class SmallPetrolCar(VehicleClass):
    A = 0.2403
    B = 227
    C = 595
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    color = "#FFFF00"
    shape = "passenger/sedan"


class SmallDieselCar(VehicleClass):
    A = 1.0601
    B = 168
    C = 379
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    color = "#00BFFF"
    shape = "passenger/sedan"


class BigPetrolCar(VehicleClass):
    A = 0.2471
    B = 210
    C = 609
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#FF4500"
    shape = "passenger/hatchback"

    
class BigDieselCar(VehicleClass):
    A = 0.6787
    B = 174
    C = 384
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#8A2BE2"
    shape = "passenger/hatchback"


class MediumVan(VehicleClass):
    A = 1.3313
    B = 166
    C = 357
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    color = "#DC143C"
    shape = "delivery"
    

class BigVan(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.50
    weightMult = 1.60
    color = "#FFFFFF"
    shape = "delivery"
    

class Bus(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 3
    weightMult = 11
    color = "#7CFC00"
    shape = "bus"


if __name__ == "__main__":
    """with open("temp.json","w") as fd:
        json.dump([v.__dict__() for v in vlist], fd)

    with open("temp", "r") as fd:
        vlist2 = json.load(fd)
        vlist2 = [Person(**person_data) for person_data in list_from_file]"""