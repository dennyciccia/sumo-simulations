import numpy as np

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
        d = abs(np.random.normal(loc=7, scale=2, size=1)[0])
        
        # tempo di reazione
        t = abs(np.random.normal(loc=0.1, scale=0.05, size=1)[0])
        
        # aggressività
        min, max = 0.0, 1.0
        while True:
            a = round(np.random.normal(loc=0.5, size=1)[0], 2)
            if min <= a <= max:
                break
        
        # rispetto del limite di velocità
        l = np.random.normal(loc=1, scale=0.2, size=1)[0]

        return DriverProfile(d, t, a, l)