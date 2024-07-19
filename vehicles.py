from abc import ABC
from random import randint
import random
import numpy as np
import traci
import yaml


class DriverProfile:
    def __init__(self, securityDistanceToObjectAhead, reactionTime, driverAggressivity, speedLimitComplianceFactor):
        self.__securityDistanceToObjectAhead = securityDistanceToObjectAhead
        self.__reactionTime = reactionTime
        self.__driverAggressivity = driverAggressivity
        self.__speedLimitComplianceFactor = speedLimitComplianceFactor

    """def __dict__(self):
        obj_dict = dict()
        obj_dict["securityDistanceToObjectAhead"] = self.securityDistanceToObjectAhead
        obj_dict["reactionTime"] = self.reactionTime
        obj_dict["driverAggressivity"] = self.driverAggressivity
        obj_dict["speedLimitComplianceFactor"] = self.speedLimitComplianceFactor
        return obj_dict"""

    @property
    def securityDistanceToObjectAhead(self):
        return self.__securityDistanceToObjectAhead

    @property
    def reactionTime(self):
        return self.__reactionTime

    @property
    def driverAggressivity(self):
        return self.__driverAggressivity

    @property
    def speedLimitComplianceFactor(self):
        return self.__speedLimitComplianceFactor

    @staticmethod
    def generateRandom():
        # distanza di sicurezza
        distance = float(abs(np.random.normal(loc=7, scale=2, size=1)[0]))

        # tempo di reazione
        reactionTime = float(abs(np.random.normal(loc=0.1, scale=0.05, size=1)[0]))

        # aggressività
        min, max = 0.0, 1.0
        while True:
            aggressivity = round(float(np.random.normal(loc=0.5, size=1)[0]), 2)
            if min <= aggressivity <= max:
                break

        # rispetto del limite di velocità
        limit = round(float(np.random.normal(loc=1, scale=0.2, size=1)[0]), 2)
        if limit < 0: limit = 0.1

        return DriverProfile(distance, reactionTime, aggressivity, limit)


class VehicleList(list):
    def getVehicle(self, vehicleID):
        for v in self:
            if v.vehicleID == vehicleID:
                return v

    def dump(self, filename):
        with open(filename, 'w') as fd:
            yaml.dump(self, fd)

    @staticmethod
    def load(filename):
        with open(filename, 'r') as fd:
            obj = yaml.unsafe_load(fd)
        return obj


class Vehicle(ABC):
    def __init__(self, id, length, weight, initialSpeed, startstop, acceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, fuel, emission, depart=-1):
        # parametri statici
        self.__vehicleID = id
        self.__numericalID = int(id.replace("vehicle",""))
        self.__routeID = -1
        self.__length = length
        self.__weight = weight
        self.__initialSpeed = initialSpeed
        self.__hasStartStop = startstop
        self.__acceleration = acceleration
        self.__noGasAcceleration = noGasAcceleration
        self.__brakingAcceleration = brakingAcceleration
        self.__fullBrakingAcceleration = fullBrakingAcceleration
        self.__driverProfile = driverProfile
        self.__fuelType = fuel
        self.__emissionClass = emission
        self.__depart = depart
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
        self.__totalElectricityConsumption = 0
        self.__totalNoiseEmission = 0

    @property
    def vehicleID(self):
        return self.__vehicleID

    @property
    def numericalID(self):
        return self.__numericalID
    
    @property
    def routeID(self):
        return self.__routeID

    @routeID.setter
    def routeID(self, value):
        self.__routeID = value

    @property
    def length(self): # m
        return self.__length
    
    @property
    def weight(self): # Kg
        return self.__weight
    
    @property
    def initialSpeed(self):
        return self.__initialSpeed
    
    @property
    def hasStartStop(self):
        return self.__hasStartStop
    
    @property
    def acceleration(self):
        return self.__acceleration
    
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
    def fuelType(self):
        return self.__fuelType

    @property
    def emissionClass(self):
        return self.__emissionClass

    @property
    def depart(self):
        return self.__depart

    @depart.setter
    def depart(self, value):
        self.__depart = value

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

    @property
    def totalElectricityConsumption(self):
        return self.__totalElectricityConsumption

    @totalElectricityConsumption.setter
    def totalElectricityConsumption(self, value):
        self.__totalElectricityConsumption = value

    @totalFuelConsumption.setter
    def totalFuelConsumption(self, value):
        self.__totalFuelConsumption = value

    @property
    def totalNoiseEmission(self):
        return self.__totalNoiseEmission

    @totalNoiseEmission.setter
    def totalNoiseEmission(self, value):
        self.__totalNoiseEmission = value

    def doMeasures(self):
        if not (self.hasStartStop and traci.vehicle.getSpeed(self.vehicleID) < 0.3):
            self.totalCO2Emissions += (traci.vehicle.getCO2Emission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalCOEmissions += (traci.vehicle.getCOEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalHCEmissions += (traci.vehicle.getHCEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalPMxEmissions += (traci.vehicle.getPMxEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalNOxEmissions += (traci.vehicle.getNOxEmission(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalFuelConsumption += (traci.vehicle.getFuelConsumption(self.vehicleID) * traci.simulation.getDeltaT()) / 1000  # g nell'ultimo step
            self.totalNoiseEmission += traci.vehicle.getNoiseEmission(self.vehicleID)  # dBA nell'ultimo step
        self.totalElectricityConsumption += (traci.vehicle.getElectricityConsumption(self.vehicleID) * traci.simulation.getDeltaT())  # Wh nell'ultimo step
        self.totalWaitingTime = traci.vehicle.getAccumulatedWaitingTime(self.vehicleID)  # s
        self.totalDistance = traci.vehicle.getDistance(self.vehicleID)  # m
        self.totalTravelTime = traci.simulation.getTime() - traci.vehicle.getDeparture(self.vehicleID)  # s
        self.meanSpeed = self.totalDistance / self.totalTravelTime  # m/s
        # self.meanSpeed = ((step - 1) * self.meanSpeed + traci.vehicle.getSpeed(self.vehicleID)) / step # m/s

    @classmethod
    def generateRandom(cls, vehicleID):
        # profilo dell'autista
        driverProfile = DriverProfile.generateRandom()

        # lunghezza
        length = float(np.random.normal(loc=4.6*cls.lengthMult, size=1)[0])
        if cls.__name__ == "PassengerCar" and length < 2.5: length = 2.5
        if cls.__name__ == "MotorCycle": length = 2.5

        # peso
        weight = float(np.random.normal(loc=1600*cls.weightMult, scale=200, size=1)[0])
        if cls.__name__ == "LightCommercialVehicle" and weight > 3500: weight = 3500
        if cls.__name__ == "HeavyGoodsVehicle" and weight < 3501: weight = 3501
        if weight < 0: weight = 550

        # velocità iniziale
        initialSpeed = 13.89 * driverProfile.speedLimitComplianceFactor
        if cls.__name__ == "Bus" and initialSpeed > 13.89: initialSpeed = 13.89

        # start&stop
        hasStartStop = True if randint(0,1) == 1 and cls.__name__ == "PassengerCar" else False

        # accelerazione
        acceleration = float(np.random.normal(loc=3, scale=2, size=1)[0])
        acceleration = 2.1 if acceleration < 2.1 else acceleration

        # decelerazione
        noGasAcceleration = float(np.random.normal(loc=0.5, size=1)[0])
        noGasAcceleration = 0.5 if noGasAcceleration < 0.5 else noGasAcceleration
        brakingAcceleration = float(abs(np.random.normal(loc=4.0, size=1)[0]))
        if brakingAcceleration < 2 : brakingAcceleration = 2
        fullBrakingAcceleration = float(np.random.normal(loc=10, size=1)[0])
        if fullBrakingAcceleration < 7: fullBrakingAcceleration = 7

        # tipo di carburante e classe di emissioni
        fuels = ["petrol", "lpg/petrol", "cng/petrol", "electric", "diesel", "phev/petrol", "phev/diesel", "cng"]
        match cls.__name__:
            case "PassengerCar":
                fuelType = random.choices(fuels, weights=(43.99, 7.21, 1.96, 0.39, 42.10, 3.44, 0.00, 0.00))[0]
                match fuelType:
                    case "petrol":
                        classes = ["HBEFA4/PC_petrol_PreEuro_3WCat_1987-90", "HBEFA4/PC_petrol_Euro-1", "HBEFA4/PC_petrol_Euro-2", "HBEFA4/PC_petrol_Euro-3", "HBEFA4/PC_petrol_Euro-4", "HBEFA4/PC_petrol_Euro-5", "HBEFA4/PC_petrol_Euro-6ab"]
                        emissionClass = random.choices(classes, weights=(15.63, 3.52, 10.09, 9.87, 22.33, 11.77, 26.69))[0]
                    case "lpg/petrol":
                        classes = ["HBEFA4/PC_LPG_petrol_Euro-2_(LPG)", "HBEFA4/PC_LPG_petrol_Euro-3_(LPG)", "HBEFA4/PC_LPG_petrol_Euro-4_(LPG)", "HBEFA4/PC_LPG_petrol_Euro-5_(LPG)", "HBEFA4/PC_LPG_petrol_Euro-6_(LPG)"]
                        emissionClass = random.choices(classes, weights=(3.83, 3.30, 29.53, 18.00, 36.86))[0]
                    case "cng/petrol":
                        classes = ["HBEFA4/PC_CNG_petrol_Euro-2_(CNG)", "HBEFA4/PC_CNG_petrol_Euro-3_(CNG)", "HBEFA4/PC_CNG_petrol_Euro-4_(CNG)", "HBEFA4/PC_CNG_petrol_Euro-5_(CNG)", "HBEFA4/PC_CNG_petrol_Euro-6_(CNG)"]
                        emissionClass = random.choices(classes, weights=(3.59, 4.09, 34.81, 28.89, 23.43))[0]
                    case "electric":
                        emissionClass = "HBEFA4/PC_BEV"
                    case "diesel":
                        classes = ["HBEFA4/PC_diesel_1986-1988", "HBEFA4/PC_diesel_Euro-1", "HBEFA4/PC_diesel_Euro-2", "HBEFA4/PC_diesel_Euro-3", "HBEFA4/PC_diesel_Euro-4", "HBEFA4/PC_diesel_Euro-5", "HBEFA4/PC_diesel_Euro-6ab"]
                        emissionClass = random.choices(classes, weights=(3.34, 0.95, 3.89, 11.57, 25.10, 22.51, 32.63))[0]
                    case "phev/petrol":
                        classes = ["HBEFA4/PC_PHEV_petrol_Euro-4_(El)", "HBEFA4/PC_PHEV_petrol_Euro-5_(El)", "HBEFA4/PC_PHEV_petrol_Euro-6d_(El)"]
                        emissionClass = random.choices(classes, weights=(0.35, 2.96, 96.69))[0]

            case "LightCommercialVehicle":
                fuelType = random.choices(fuels, weights=(4.90, 0.00, 1.77, 0.00, 90.50, 0.43, 0.37, 0.00))[0]
                match fuelType:
                    case "petrol":
                        if weight <= 1305:
                            classes = ["HBEFA4/LCV_petrol_M+N1-I_Conv_gt1981", "HBEFA4/LCV_petrol_M+N1-I_Euro-1", "HBEFA4/LCV_petrol_M+N1-I_Euro-2", "HBEFA4/LCV_petrol_M+N1-I_Euro-3", "HBEFA4/LCV_petrol_M+N1-I_Euro-4", "HBEFA4/LCV_petrol_M+N1-I_Euro-5", "HBEFA4/LCV_petrol_M+N1-I_Euro-6ab"]
                        elif 1305 < weight <= 1760:
                            classes = ["HBEFA4/LCV_petrol_N1-II_Conv_gt1981", "HBEFA4/LCV_petrol_N1-II_Euro-1", "HBEFA4/LCV_petrol_N1-II_Euro-2", "HBEFA4/LCV_petrol_N1-II_Euro-3", "HBEFA4/LCV_petrol_N1-II_Euro-4", "HBEFA4/LCV_petrol_N1-II_Euro-5", "HBEFA4/LCV_petrol_N1-II_Euro-6ab"]
                        elif weight > 1760:
                            classes = ["HBEFA4/LCV_petrol_N1-III_Conv_gt1981", "HBEFA4/LCV_petrol_N1-III_Euro-1", "HBEFA4/LCV_petrol_N1-III_Euro-2", "HBEFA4/LCV_petrol_N1-III_Euro-3", "HBEFA4/LCV_petrol_N1-III_Euro-4", "HBEFA4/LCV_petrol_N1-III_Euro-5", "HBEFA4/LCV_petrol_N1-III_Euro-6ab"]
                        emissionClass = random.choices(classes, weights=(24.68, 9.64, 14.23, 11.98, 12.53, 5.84, 20.67))[0]
                    case "cng/petrol":
                        if weight <= 1305:
                            classes = ["HBEFA4/LCV_CNG_petrol_M+N1-I_Euro-2_(CNG)", "HBEFA4/LCV_CNG_petrol_M+N1-I_Euro-3_(CNG)", "HBEFA4/LCV_CNG_petrol_M+N1-I_Euro-4_(CNG)", "HBEFA4/LCV_CNG_petrol_M+N1-I_Euro-5_(CNG)", "HBEFA4/LCV_CNG_petrol_M+N1-I_Euro-6_(CNG)"]
                        elif 1305 < weight <= 1760:
                            classes = ["HBEFA4/LCV_CNG_petrol_N1-II_Euro-2_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-II_Euro-3_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-II_Euro-4_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-II_Euro-5_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-II_Euro-6_(CNG)"]
                        elif weight > 1760:
                            classes = ["HBEFA4/LCV_CNG_petrol_N1-III_Euro-2_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-III_Euro-3_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-III_Euro-4_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-III_Euro-5_(CNG)", "HBEFA4/LCV_CNG_petrol_N1-III_Euro-6_(CNG)"]
                        emissionClass = random.choices(classes, weights=(1.42, 3.33, 23.79, 31.31, 37.29))[0]
                    case "diesel":
                        if weight <= 1305:
                            classes = ["HBEFA4/LCV_diesel_M+N1-I_convlt_1981", "HBEFA4/LCV_diesel_M+N1-I_Euro-1", "HBEFA4/LCV_diesel_M+N1-I_Euro-2", "HBEFA4/LCV_diesel_M+N1-I_Euro-3", "HBEFA4/LCV_diesel_M+N1-I_Euro-4", "HBEFA4/LCV_diesel_M+N1-I_Euro-5", "HBEFA4/LCV_diesel_M+N1-I_Euro-6ab"]
                        elif 1305 < weight <= 1760:
                            classes = ["HBEFA4/LCV_diesel_N1-II_convlt_1981", "HBEFA4/LCV_diesel_N1-II_Euro-1", "HBEFA4/LCV_diesel_N1-II_Euro-2", "HBEFA4/LCV_diesel_N1-II_Euro-3", "HBEFA4/LCV_diesel_N1-II_Euro-4", "HBEFA4/LCV_diesel_N1-II_Euro-5", "HBEFA4/LCV_diesel_N1-II_Euro-6ab"]
                        elif weight > 1760:
                            classes = ["HBEFA4/LCV_diesel_N1-III_convlt_1986", "HBEFA4/LCV_diesel_N1-III_Euro-1", "HBEFA4/LCV_diesel_N1-III_Euro-2", "HBEFA4/LCV_diesel_N1-III_Euro-3", "HBEFA4/LCV_diesel_N1-III_Euro-4", "HBEFA4/LCV_diesel_N1-III_Euro-5", "HBEFA4/LCV_diesel_N1-III_Euro-6ab"]
                        emissionClass = random.choices(classes, weights=(10.94, 5.60, 10.97, 17.05, 17.57, 11.82, 26.04))[0]
                    case "phev/petrol":
                        if weight <= 1305:
                            classes = ["HBEFA4/LCV_PHEV_petrol_M+N1-I_Euro-5_(El)", "HBEFA4/LCV_PHEV_petrol_M+N1-I_Euro-6_(El)"]
                        elif 1305 < weight <= 1760:
                            classes = ["HBEFA4/LCV_PHEV_petrol_N1-II_Euro-5_(El)", "HBEFA4/LCV_PHEV_petrol_N1-II_Euro-6_(El)"]
                        elif weight > 1760:
                            classes = ["HBEFA4/LCV_PHEV_petrol_N1-III_Euro-5_(El)", "HBEFA4/LCV_PHEV_petrol_N1-III_Euro-6_(El)"]
                        emissionClass = random.choices(classes, weights=(0.13, 99.85))[0]
                    case "phev/diesel":
                        if weight <= 1305:
                            classes = ["HBEFA4/LCV_PHEV_diesel_M+N1-I_Euro-5_(El)", "HBEFA4/LCV_PHEV_diesel_M+N1-I_Euro-6_(El)"]
                        elif 1305 < weight <= 1760:
                            classes = ["HBEFA4/LCV_PHEV_diesel_N1-II_Euro-5_(El)", "HBEFA4/LCV_PHEV_diesel_N1-II_Euro-6_(El)"]
                        elif weight > 1760:
                            classes = ["HBEFA4/LCV_PHEV_diesel_N1-III_Euro-5_(El)", "HBEFA4/LCV_PHEV_diesel_N1-III_Euro-6_(El)"]
                        emissionClass = random.choices(classes, weights=(0.01, 99.78))[0]

            case "HeavyGoodsVehicle":
                fuelType = random.choices(fuels, weights=(0.00, 0.09, 0.00, 1.89, 97.11, 0.00, 0.00, 0.39))[0]
                match fuelType:
                    # in questo caso è GNL
                    case "lpg/petrol":
                        if weight <= 7500:
                            classes = ["HBEFA4/HGV_LNG_le7_5t_Euro-IV", "HBEFA4/HGV_LNG_le7_5t_Euro-V", "HBEFA4/HGV_LNG_le7_5t_Euro-VI"]
                        elif 7500 < weight <= 12000:
                            classes = ["HBEFA4/HGV_LNG_gt7_5-12t_Euro-IV", "HBEFA4/HGV_LNG_gt7_5-12t_Euro-V", "HBEFA4/HGV_LNG_gt7_5-12t_Euro-VI"]
                        elif weight > 12000:
                            classes = ["HBEFA4/HGV_LNG_gt12t_Euro-IV", "HBEFA4/HGV_LNG_gt12t_Euro-V", "HBEFA4/HGV_LNG_gt12t_Euro-VI"]
                        emissionClass = random.choices(classes, weights=(7.36, 4.69, 5.01))[0]
                    case "electric":
                        if weight <= 7500:
                            emissionClass = "HBEFA4/RigidTruck_BEV_le7.5t"
                        elif 7500 < weight <= 12000:
                            emissionClass = "HBEFA4/RigidTruck_BEV_gt7.5-12t"
                        elif weight > 12000:
                            emissionClass = "HBEFA4/RigidTruck_BEV_gt12t"
                    case "diesel":
                        if weight <= 7500:
                            classes = ["HBEFA4/RT_le7.5t_80ties", "HBEFA4/RT_le7.5t_Euro-I", "HBEFA4/RT_le7.5t_Euro-II", "HBEFA4/RT_le7.5t_Euro-III", "HBEFA4/RT_le7.5t_Euro-IV_SCR", "HBEFA4/RT_le7.5t_Euro-V_SCR", "HBEFA4/RT_le7.5t_Euro-VI_A-C"]
                        elif 7500 < weight <= 12000:
                            classes = ["HBEFA4/RT_gt7_5-12t_80ties", "HBEFA4/RT_gt7_5-12t_Euro-I", "HBEFA4/RT_gt7_5-12t_Euro-II", "HBEFA4/RT_gt7_5-12t_Euro-III", "HBEFA4/RT_gt7_5-12t_Euro-IV_SCR", "HBEFA4/RT_gt7_5-12t_Euro-V_SCR", "HBEFA4/RT_gt7_5-12t_Euro-VI_A-C"]
                        elif weight > 12000:
                            classes = ["HBEFA4/RT_gt12-14t_80ties", "HBEFA4/RT_gt12-14t_Euro-I", "HBEFA4/RT_gt12-14t_Euro-II", "HBEFA4/RT_gt12-14t_Euro-III", "HBEFA4/RT_gt12-14t_Euro-IV_SCR", "HBEFA4/RT_gt12-14t_Euro-V_SCR", "HBEFA4/RT_gt12-14t_Euro-VI_A-C"]
                        emissionClass = random.choices(classes, weights=(36.98, 5.84, 12.31, 16.32, 3.73, 9.58, 14.97))[0]
                    case "cng":
                        if weight <= 7500:
                            classes = ["HBEFA4/HGV_CNG_le7_5t_Euro-IV", "HBEFA4/HGV_CNG_le7_5t_Euro-V", "HBEFA4/HGV_CNG_le7_5t_Euro-VI"]
                        elif 7500 < weight <= 12000:
                            classes = ["HBEFA4/HGV_CNG_gt7_5-12t_Euro-IV", "HBEFA4/HGV_CNG_gt7_5-12t_Euro-V", "HBEFA4/HGV_CNG_gt7_5-12t_Euro-VI"]
                        elif weight > 12000:
                            classes = ["HBEFA4/HGV_CNG_gt12t_Euro-IV", "HBEFA4/HGV_CNG_gt12t_Euro-V", "HBEFA4/HGV_CNG_gt12t_Euro-VI"]
                        emissionClass = random.choices(classes, weights=(0.11, 18.30, 76.89))[0]

            case "Truck":
                fuelType = random.choices(fuels, weights=(0.00, 0.02, 0.00, 0.01, 97.79, 0.00, 0.00, 1.81))[0]
                match fuelType:
                    # in questo caso è GNL
                    case "lpg/petrol":
                        classes = ["HBEFA4/TT_AT_LNG_Euro-IV", "HBEFA4/TT_AT_LNG_Euro-V", "TT_AT_LNG_Euro-VI_(CI)"]
                        emissionClass = random.choices(classes, weights=(5.00, 35.00, 17.50))[0]
                    case "electric":
                        emissionClass = "HBEFA4/TT_AT_BEV"
                    case "diesel":
                        classes = ["HBEFA4/TT_AT_gt34-40t_80ties", "HBEFA4/TT_AT_gt34-40t_Euro-I", "HBEFA4/TT_AT_gt34-40t_Euro-II", "HBEFA4/TT_AT_gt34-40t_Euro-III", "HBEFA4/TT_AT_gt34-40t_Euro-IV_SCR", "HBEFA4/TT_AT_gt34-40t_Euro-V_SCR", "HBEFA4/TT_AT_gt34-40t_Euro-VI_A-C"]
                        emissionClass = random.choices(classes, weights=(36.98, 5.84, 12.31, 16.32, 3.73, 9.58, 14.97))[0]
                    case "cng":
                        classes = ["HBEFA4/TT_AT_CNG_Euro-IV", "HBEFA4/TT_AT_CNG_Euro-V", "TT_AT_CNG_Euro-VI"]
                        emissionClass = random.choices(classes, weights=(0.00, 0.98, 98.97))[0]

            case "MotorCycle":
                # Petrol è <=250cc, diesel è >250cc, electric è elettrico
                fuelType = random.choices(fuels, weights=(51.09, 0.00, 0.00, 0.39, 48.50, 0.00, 0.00, 0.00))[0]
                match fuelType:
                    case "petrol":
                        classes = ["HBEFA4/MC_4S_le250cc_preEuro", "HBEFA4/MC_4S_le250cc_Euro-1", "HBEFA4/MC_4S_le250cc_Euro-2", "HBEFA4/MC_4S_le250cc_Euro-3", "HBEFA4/MC_4S_le250cc_Euro-4", "HBEFA4/MC_4S_le250cc_Euro-5"]
                        emissionClass = random.choices(classes, weights=(29.65, 16.02, 11.56, 28.56, 8.60, 5.47))[0]
                    case "diesel":
                        classes = ["HBEFA4/MC_4S_gt250cc_preEuro", "HBEFA4/MC_4S_gt250cc_Euro-1", "HBEFA4/MC_4S_gt250cc_Euro-2", "HBEFA4/MC_4S_gt250cc_Euro-3", "HBEFA4/MC_4S_gt250cc_Euro-4", "HBEFA4/MC_4S_gt250cc_Euro-5"]
                        emissionClass = random.choices(classes, weights=(21.58, 10.24, 12.17, 31.88, 15.12, 8.98))[0]
                    case "electric":
                        emissionClass = "HBEFA4/MC_BEV"

            case "Bus":
                busType = random.choices(["citybus", "coach"], weights=(51.95, 46.52))[0]
                match busType:
                    case "citybus":
                        fuelType = random.choices(fuels, weights=(0.00, 0.00, 1.86, 4.89, 78.43, 0.00, 4.33, 10.48))[0]
                        match fuelType:
                            # in questo caso è GNL
                            case "cng/petrol":
                                classes = ["HBEFA4/UBus_Std_gt15-18t_LNG_Euro-IV", "HBEFA4/UBus_Std_gt15-18t_LNG_Euro-V", "HBEFA4/UBus_Std_gt15-18t_LNG_Euro-VI"]
                                emissionClass = random.choices(classes, weights=(5.78, 22.82, 35.54))[0]
                            case "electric":
                                emissionClass = "HBEFA4/UBus_Electric_Std_gt15-18t"
                                cls.shape = "bus/trolley"
                            case "diesel":
                                classes = ["HBEFA4/UBus_Std_gt15-18t_80ties", "HBEFA4/UBus_Std_gt15-18t_Euro-I", "HBEFA4/UBus_Std_gt15-18t_Euro-II_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-III_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-IV_EGR_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-V_SCR_(DPF)", "HBEFA4/UBus_Std_gt15-18t_Euro-VI_A-C"]
                                emissionClass = random.choices(classes, weights=(6.48, 0.88, 9.02, 19.38, 5.78, 22.82, 35.54))[0]
                            case "phev/diesel":
                                classes = ["HBEFA4/UBus_Std_gt15-18t_HEV_Euro-IV", "HBEFA4/UBus_Std_gt15-18t_HEV_Euro-V", "HBEFA4/UBus_Std_gt15-18t_HEV_Euro-VI_D-E"]
                                emissionClass = random.choices(classes, weights=(5.78, 22.82, 35.54))[0]
                            case "cng":
                                classes = ["HBEFA4/UBus_Std_gt15-18t_CNG_Euro-II", "HBEFA4/UBus_Std_gt15-18t_CNG_Euro-III", "HBEFA4/UBus_Std_gt15-18t_CNG_Euro-IV", "HBEFA4/UBus_Std_gt15-18t_CNG_Euro-V", "HBEFA4/UBus_Std_gt15-18t_CNG_Euro-VI"]
                                emissionClass = random.choices(classes, weights=(9.02, 19.38, 5.78, 22.82, 35.54))[0]
                    case "coach":
                        fuelType = "diesel"
                        classes = ["HBEFA4/Coach_Std_le18t_80ties", "HBEFA4/Coach_Std_le18t_Euro-I", "HBEFA4/Coach_Std_le18t_Euro-II", "HBEFA4/Coach_Std_le18t_Euro-III", "HBEFA4/Coach_Std_le18t_Euro-IV_SCR", "HBEFA4/Coach_Std_le18t_Euro-V_SCR", "HBEFA4/Coach_Std_le18t_Euro-VI_A-C"]
                        emissionClass = random.choices(classes, weights=(16.45, 4.56, 14.16, 17.94, 8.90, 13.50, 24.30))[0]

        return cls(vehicleID, length, weight, initialSpeed, hasStartStop, acceleration, noGasAcceleration, brakingAcceleration, fullBrakingAcceleration, driverProfile, fuelType, emissionClass)


class PassengerCar(Vehicle):
    lengthMult = 1
    weightMult = 1
    vClass = "passenger"
    color = "#3498DB"
    shape = "passenger/sedan"


class LightCommercialVehicle(Vehicle):
    lengthMult = 1.3
    weightMult = 1.9
    vClass = "delivery"
    color = "#FFFFFF"
    shape = "delivery"
    

class HeavyGoodsVehicle(Vehicle):
    lengthMult = 1.6
    weightMult = 6.2
    vClass = "delivery"
    color = "#EB984E"
    shape = "delivery"


class Truck(Vehicle):
    lengthMult = 4.0
    weightMult = 23.0
    vClass = "truck"
    color = "#C0392B"
    shape = "truck"


class MotorCycle(Vehicle):
    lengthMult = 0.7
    weightMult = 0.34375
    vClass = "motorcycle"
    color = "#8E44AD"
    shape = "motorcycle"


class Bus(Vehicle):
    lengthMult = 3
    weightMult = 10
    vClass = "bus"
    color = "#28B463"
    shape = "bus"
