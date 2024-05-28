import traci

J = 100

class TrafficLight:
    def __init__(self, tlID, enhancements, k):
        self.__tlID = tlID
        self.__enhancements = enhancements  # lista dei miglioramenti dell'algoritmo
        self.__K = k    # costante K nella formula del calcolo del costo del flusso
    
    @property
    def tlID(self):
        return self.__tlID

    @property
    def enhancements(self):
        return self.__enhancements

    @property
    def K(self):
        return self.__K
    
    @property
    def movingFlow(self):
        if traci.trafficlight.getPhase(self.tlID) in [3,4,5]:   # flusso orizzontale
            return 'HORIZONTAL'
        elif traci.trafficlight.getPhase(self.tlID) in [0,1,2]: # flusso verticale
            return 'VERTICAL'

    # switch del semaforo per cambiare il flusso che si muove
    def switchTrafficLight(self):
        traci.trafficlight.setPhase(self.tlID, traci.trafficlight.getPhase(self.tlID)+1)

    def getHorizontalEdges(self):
        horizontalEdges = []
        for edge in traci.junction.getIncomingEdges(self.tlID):
            if traci.edge.getAngle(edge) in [90.0, 270.0]:
                horizontalEdges.append(edge)

        return horizontalEdges

    def getVerticalEdges(self):
        verticalEdges = []
        for edge in traci.junction.getIncomingEdges(self.tlID):
            if traci.edge.getAngle(edge) in [0.0, 180.0]:
                verticalEdges.append(edge)

        return verticalEdges
    
    # calcolo dei costi dei flussi
    def getFlowCosts(self):
        costH = costV = 0
        
        for edge in self.getHorizontalEdges():
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                if 1 not in self.enhancements:
                    costH += J + 1 * (traci.vehicle.getSpeed(vehicle) ** 2)
                else:
                    costH += J + (self.K if self.movingFlow == 'HORIZONTAL' else 1) * (traci.vehicle.getSpeed(vehicle) ** 2)

        for edge in self.getVerticalEdges():
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                if 1 not in self.enhancements:
                    costV += J + 1 * (traci.vehicle.getSpeed(vehicle) ** 2)
                else:
                    costV += J + (self.K if self.movingFlow == 'VERTICAL' else 1) * (traci.vehicle.getSpeed(vehicle) ** 2)
        
        return costH, costV
    
    def tryToSkipRed(self):
        meanSpeedH = meanSpeedV = 0
        vehicleNumberH = vehicleNumberV = 0

        for edge in self.getHorizontalEdges():
            meanSpeedH += traci.edge.getLastStepMeanSpeed(edge)
            vehicleNumberH += traci.edge.getLastStepVehicleNumber(edge)
        meanSpeedH /= len(self.getHorizontalEdges())

        for edge in self.getVerticalEdges():
            meanSpeedV += traci.edge.getLastStepMeanSpeed(edge)
            vehicleNumberV += traci.edge.getLastStepVehicleNumber(edge)
        meanSpeedV /= len(self.getVerticalEdges())

        # se i veicoli sono fermi o non ci sono vai alla fase verde
        if (self.movingFlow == 'HORIZONTAL' and (meanSpeedH < 1.0 or vehicleNumberH == 0)) or (self.movingFlow == 'VERTICAL' and (meanSpeedV < 1.0 or vehicleNumberV == 0)):
            traci.trafficlight.setPhase(self.tlID, (traci.trafficlight.getPhase(self.tlID)+2)%6)
    
    # azioni eseguite a ogni step della simulazione
    def performStep(self):
        if 2 in self.enhancements:
            # se siamo alla fine della fase giallo prova a saltare la fase di solo rosso se è sicuro farlo
            if traci.trafficlight.getPhase(self.tlID) in [1,4] and 2 <= traci.trafficlight.getSpentDuration(self.tlID) < 3:
                self.tryToSkipRed()

        # massimo 180s di verde per un flusso
        if traci.trafficlight.getSpentDuration(self.tlID) >= 180.0:
            self.switchTrafficLight()
            return
        
        # minimo 10s di verde per un flusso e controllo di non essere in una fase con giallo o solo rosso
        if traci.trafficlight.getSpentDuration(self.tlID) > 10 and traci.trafficlight.getPhase(self.tlID) not in [1,2,4,5]:
            costH, costV = self.getFlowCosts()
            if (self.movingFlow == 'HORIZONTAL' and costH < costV) or (self.movingFlow == 'VERTICAL' and costV < costH):
                self.switchTrafficLight()
