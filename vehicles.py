from abc import ABC
from random import randint
import random
import numpy as np
import traci

from profiles import DriverProfile


class VehicleList(list):
    def getVehicle(self, vehicleID):
        for v in self:
            if v.vehicleID == vehicleID:
                return v


class VehicleClass(ABC):
    def __init__(self, id, r, l, w, ics, hst, a, nga, ba, fba, A, B, C, dp, d, sl, ec):
        # parametri statici
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
        self.__emissionClass = ec
        # parametri misurati durante la simulazione
        self.__totalWaitingTime = 0
        self.__totalTravelTime = 0
        self.__totalDistance = 0
        self.__meanSpeed = 0
        self.__totalCO2Emissions = 0
        self.__totalCOEmissions = 0
        self.__totalHCEmissions = 0
        self.__totalPMxEmissions = 0
        self.__totalNOxEmissions = 0
        self.__totalFuelConsumption = 0
        self.__totalNoiseEmission = 0
    
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

    @property
    def emissionClass(self):
        return self.__emissionClass

    @property
    def totalWaitingTime(self):
        return self.__totalWaitingTime
    
    @totalWaitingTime.setter
    def totalWaitingTime(self, value):
        self.__totalWaitingTime = value
    
    @property
    def totalTravelTime(self):
        return self.__totalTravelTime
    
    @totalTravelTime.setter
    def totalTravelTime(self, value):
        self.__totalTravelTime = value
    
    @property
    def totalDistance(self):
        return self.__totalDistance
    
    @totalDistance.setter
    def totalDistance(self, value):
        self.__totalDistance = value
    
    @property
    def meanSpeed(self):
        return self.__meanSpeed
    
    @meanSpeed.setter
    def meanSpeed(self, value):
        self.__meanSpeed = value
    
    @property
    def totalCO2Emissions(self):
        return self.__totalCO2Emissions
    
    @totalCO2Emissions.setter
    def totalCO2Emissions(self, value):
        self.__totalCO2Emissions = value
    
    @property
    def totalCOEmissions(self):
        return self.__totalCOEmissions
    
    @totalCOEmissions.setter
    def totalCOEmissions(self, value):
        self.__totalCOEmissions = value
    
    @property
    def totalHCEmissions(self):
        return self.__totalHCEmissions
    
    @totalHCEmissions.setter
    def totalHCEmissions(self, value):
        self.__totalHCEmissions = value
    
    @property
    def totalPMxEmissions(self):
        return self.__totalPMxEmissions
    
    @totalPMxEmissions.setter
    def totalPMxEmissions(self, value):
        self.__totalPMxEmissions = value
    
    @property
    def totalNOxEmissions(self):
        return self.__totalNOxEmissions
    
    @totalNOxEmissions.setter
    def totalNOxEmissions(self, value):
        self.__totalNOxEmissions = value
    
    @property
    def totalFuelConsumption(self):
        return self.__totalFuelConsumption
    
    @totalFuelConsumption.setter
    def totalFuelConsumption(self, value):
        self.__totalFuelConsumption = value
    
    @property
    def totalNoiseEmission(self):
        return self.__totalNoiseEmission
    
    @totalNoiseEmission.setter
    def totalNoiseEmission(self, value):
        self.__totalNoiseEmission = value

    @staticmethod
    def VSP(velocity, acceleration, slope): # W/Kg
        return velocity*(1.1*acceleration + 9.81*slope + 0.132) + 0.000302*(velocity**3)

    def FC(self, vsp): # g/h
        return ( ( self.A*(vsp**2) + self.B*vsp + self.C ) * self.carWeight ) / 1000

    def doMeasures(self, currentStep, final=False):
        if not final:
            self.meanSpeed = self.meanSpeed + (traci.vehicle.getSpeed(self.vehicleID) - self.meanSpeed) / currentStep # m/s
            if not (self.hasStartStop and traci.vehicle.getSpeed(self.vehicleID) < 0.3):
                self.totalCO2Emissions += (traci.vehicle.getCO2Emission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalCOEmissions += (traci.vehicle.getCOEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalHCEmissions += (traci.vehicle.getHCEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalPMxEmissions += (traci.vehicle.getPMxEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalNOxEmissions += (traci.vehicle.getNOxEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalFuelConsumption += (traci.vehicle.getFuelConsumption(self.vehicleID) * traci.simulation.getDeltaT()) / 1000000 # Kg nell'ultimo step
                self.totalNoiseEmission += traci.vehicle.getNoiseEmission(self.vehicleID) # dBA nell'ultimo step
        else:
            self.totalWaitingTime = traci.vehicle.getAccumulatedWaitingTime(self.vehicleID) # s
            self.totalDistance = traci.vehicle.getDistance(self.vehicleID) # m
            self.totalTravelTime = traci.simulation.getTime() - traci.vehicle.getDeparture(self.vehicleID) # s

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
        if cls.__name__ == "MediumVan" and carWeight > 3500: carWeight = 3500
        if cls.__name__ == "BigVan" and carWeight < 3501: carWeight = 3501

        # velocità iniziale
        initialCarSpeed = (50.00 / 3.6) * driverProfile.speedLimitComplianceFactor
        if cls.__name__ == "Bus" and initialCarSpeed > 13.89: initialCarSpeed = 13.89 

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

        # classe di emissioni
        match cls.__name__:
            case "SmallPetrolCar":
                euro = ["HBEFA4/PC_petrol_PreEuro_3WCat_1987-90", "HBEFA4/PC_petrol_Euro-1", "HBEFA4/PC_petrol_Euro-2", "HBEFA4/PC_petrol_Euro-3", "HBEFA4/PC_petrol_Euro-4", "HBEFA4/PC_petrol_Euro-5", "HBEFA4/PC_petrol_Euro-6ab"]
                emissionClass = random.choices(euro, weights=(15.63, 3.52, 10.09, 9.87, 22.33, 11.77, 26.69))[0]
            case "SmallDieselCar":
                euro = ["HBEFA4/PC_diesel_1986-1988", "HBEFA4/PC_diesel_Euro-1", "HBEFA4/PC_diesel_Euro-2", "HBEFA4/PC_diesel_Euro-3", "HBEFA4/PC_diesel_Euro-4_(DPF)", "HBEFA4/PC_diesel_Euro-5", "HBEFA4/PC_diesel_Euro-6ab"]
                emissionClass = random.choices(euro, weights=(3.34,	0.95, 3.89,	11.57, 25.10, 22.51, 32.63))[0]
            case "BigPetrolCar":
                euro = ["HBEFA4/PC_petrol_PreEuro_3WCat_1987-90", "HBEFA4/PC_petrol_Euro-1", "HBEFA4/PC_petrol_Euro-2", "HBEFA4/PC_petrol_Euro-3", "HBEFA4/PC_petrol_Euro-4", "HBEFA4/PC_petrol_Euro-5", "HBEFA4/PC_petrol_Euro-6ab"]
                emissionClass = random.choices(euro, weights=(15.63, 3.52, 10.09, 9.87, 22.33, 11.77, 26.69))[0]
            case "BigDieselCar":
                euro = ["HBEFA4/PC_diesel_1986-1988", "HBEFA4/PC_diesel_Euro-1", "HBEFA4/PC_diesel_Euro-2", "HBEFA4/PC_diesel_Euro-3", "HBEFA4/PC_diesel_Euro-4_(DPF)", "HBEFA4/PC_diesel_Euro-5", "HBEFA4/PC_diesel_Euro-6ab"]
                emissionClass = random.choices(euro, weights=(3.34,	0.95, 3.89,	11.57, 25.10, 22.51, 32.63))[0]
            case "MediumVan":
                euro = ["HBEFA4/LCV_diesel_N1-II_convlt_1986", "HBEFA4/LCV_diesel_N1-II_Euro-1", "HBEFA4/LCV_diesel_N1-II_Euro-2", "HBEFA4/LCV_diesel_N1-II_Euro-3", "HBEFA4/LCV_diesel_N1-II_Euro-4", "HBEFA4/LCV_diesel_N1-II_Euro-5", "HBEFA4/LCV_diesel_N1-II_Euro-6ab"]
                emissionClass = random.choices(euro, weights=(10.94, 5.60, 10.97, 17.05, 17.57,	11.82, 26.04))[0]
            case "BigVan":
                if carWeight <= 7500: euro = ["HBEFA4/RT_le7.5t_80ties", "HBEFA4/RT_le7.5t_Euro-I", "HBEFA4/RT_le7.5t_Euro-II", "HBEFA4/RT_le7.5t_Euro-III", "HBEFA4/RT_le7.5t_Euro-IV_SCR", "HBEFA4/RT_le7.5t_Euro-V_SCR", "HBEFA4/RT_le7.5t_Euro-VI_A-C"]
                else: euro = ["HBEFA4/RT_gt7_5-12t_80ties", "HBEFA4/RT_gt7_5-12t_Euro-I", "HBEFA4/RT_gt7_5-12t_Euro-II", "HBEFA4/RT_gt7_5-12t_Euro-III", "HBEFA4/RT_gt7_5-12t_Euro-IV_SCR", "HBEFA4/RT_gt7_5-12t_Euro-V_SCR", "HBEFA4/RT_gt7_5-12t_Euro-VI_A-C"]
                emissionClass = random.choices(euro, weights=(36.98, 5.84, 12.31, 16.32, 3.73, 9.58, 14.97))[0]
            case "Bus":
                euro = ["HBEFA4/UBus_Std_gt15-18t_80ties", "HBEFA4/UBus_Std_gt15-18t_Euro-I", "HBEFA4/UBus_Std_gt15-18t_Euro-II_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-III_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-IV_SCR_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-V_SCR_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-VI_A-C"]
                emissionClass = random.choices(euro, weights=(6.48,	0.88, 9.02,	19.38, 5.78, 22.82,	35.54))[0]

        return cls(vehicleID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAcceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass)

class SmallPetrolCar(VehicleClass):
    A = 0.2403
    B = 227
    C = 595
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    vClass = "passenger"
    color = "#FFFF00"
    shape = "passenger/sedan"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, SmallPetrolCar.A, SmallPetrolCar.B, SmallPetrolCar.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): # Kg/h
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * SmallPetrolCar.ConversionFactor


class SmallDieselCar(VehicleClass):
    A = 1.0601
    B = 168
    C = 379
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1
    weightMult = 1
    vClass = "passenger"
    color = "#00BFFF"
    shape = "passenger/sedan"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, SmallDieselCar.A, SmallDieselCar.B, SmallDieselCar.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * SmallDieselCar.ConversionFactor
    

class BigPetrolCar(VehicleClass):
    A = 0.2471
    B = 210
    C = 609
    ConversionFactor = 3.171 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    vClass = "passenger"
    color = "#FF4500"
    shape = "passenger/hatchback"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, BigPetrolCar.A, BigPetrolCar.B, BigPetrolCar.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): # Kg/h
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigPetrolCar.ConversionFactor

    
class BigDieselCar(VehicleClass):
    A = 0.6787
    B = 174
    C = 384
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.3
    vClass = "passenger"
    color = "#8A2BE2"
    shape = "passenger/hatchback"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, BigDieselCar.A, BigDieselCar.B, BigDieselCar.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigDieselCar.ConversionFactor
    

class MediumVan(VehicleClass):
    A = 1.3313
    B = 166
    C = 357
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.1
    weightMult = 1.9
    vClass = "delivery"
    color = "#DC143C"
    shape = "delivery"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * MediumVan.ConversionFactor
    

class BigVan(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 1.5
    weightMult = 4.7
    vClass = "delivery"
    color = "#FFFFFF"
    shape = "delivery"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * BigVan.ConversionFactor
    

class Bus(VehicleClass):
    A = 1.4156
    B = 166
    C = 378
    ConversionFactor = 3.163 # Kg of CO2 each Kg of fuel
    lengthMult = 3
    weightMult = 11
    vClass = "bus"
    color = "#7CFC00"
    shape = "bus"

    def __init__(self, vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, depart, startLane, emissionClass):
        super().__init__(vehID, routeID, carLength, carWeight, initialCarSpeed, hasStartStop, carAccceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, MediumVan.A, MediumVan.B, MediumVan.C, driverProfile, depart, startLane, emissionClass)

    def getCO2emission(self, velocity, acceleration, slope): 
        return (self.FC(VehicleClass.VSP(velocity, acceleration, slope)) /1000) * Bus.ConversionFactor