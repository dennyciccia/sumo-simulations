import traci

J = 100
K = 1

class TrafficLight:
    def __init__(self, tlID, enhancements):
        self.__tlID = tlID
        self.__enhancements = enhancements  # lista dei miglioramenti dell'algoritmo
        self.__elapsedTimePhase = 0     # da quanto tempo è attiva la fase corrente (s)
    
    @property
    def tlID(self):
        return self.__tlID

    @property
    def enhancements(self):
        return self.__enhancements
    
    @property
    def movingFlow(self):
        if traci.trafficlight.getPhase(self.tlID) in [3,4,5]:   # flusso orizzontale
            return 'HORIZONTAL'
        elif traci.trafficlight.getPhase(self.tlID) in [0,1,2]: # flusso verticale
            return 'VERTICAL'

    @property
    def elapsedTimePhase(self):
        return self.__elapsedTimePhase

    @elapsedTimePhase.setter
    def elapsedTimePhase(self, value):
        self.__elapsedTimePhase = value

    # switch del semaforo per cambiare il flusso che si muove
    def switchTrafficLight(self):
        traci.trafficlight.setPhase(self.tlID, traci.trafficlight.getPhase(self.tlID)+1)

    def getHorizontalEdges(self):
        return ["E1", "E3"]

    def getVerticalEdges(self):
        return ["E2", "E4"]
    
    # calcolo dei costi dei flussi
    def getFlowCosts(self):
        costH = costV = 0
        
        for edge in self.getHorizontalEdges():
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                if 1 not in self.enhancements:
                    costH += J + K * (traci.vehicle.getSpeed(vehicle) ** 2)
                else:
                    costH += J + (30 if self.movingFlow == 'HORIZONTAL' else 1) * (traci.vehicle.getSpeed(vehicle) ** 2)

        for edge in self.getVerticalEdges():
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                if 1 not in self.enhancements:
                    costV += J + K * (traci.vehicle.getSpeed(vehicle) ** 2)
                else:
                    costV += J + (30 if self.movingFlow == 'VERTICAL' else 1) * (traci.vehicle.getSpeed(vehicle) ** 2)
        
        return costH, costV
    
    def tryToSkipRed(self):
        meanSpeedH = (traci.edge.getLastStepMeanSpeed("E1") * traci.edge.getLastStepMeanSpeed("E3")) / 2
        vehicleNumberH = traci.edge.getLastStepVehicleNumber("E1") + traci.edge.getLastStepVehicleNumber("E3")
        meanSpeedV = (traci.edge.getLastStepMeanSpeed("E2") * traci.edge.getLastStepMeanSpeed("E4")) / 2
        vehicleNumberV = traci.edge.getLastStepVehicleNumber("E2") + traci.edge.getLastStepVehicleNumber("E4")
        # se i veicoli sono fermi o non ci sono vai alla fase verde
        if (self.movingFlow == 'HORIZONTAL' and (meanSpeedH < 1.0 or vehicleNumberH == 0)) or (self.movingFlow == 'VERTICAL' and (meanSpeedV < 1.0 or vehicleNumberV == 0)):
            traci.trafficlight.setPhase(self.tlID, (traci.trafficlight.getPhase(self.tlID)+2)%6)
    
    # azioni eseguite a ogni step della simulazione
    def performStep(self):
        # calcolo del tempo trascorso nella fase attuale
        self.elapsedTimePhase = round(traci.trafficlight.getPhaseDuration(self.tlID) - (traci.trafficlight.getNextSwitch(self.tlID) - traci.simulation.getTime()), 3)
        
        if 2 in self.enhancements:
            # se siamo alla fine della fase giallo prova a saltare la fase di solo rosso se è sicuro farlo
            if traci.trafficlight.getPhase(self.tlID) in [1,4] and 2.8 < self.elapsedTimePhase < 3.0:
                self.tryToSkipRed()

        # massimo 180s di verde per un flusso
        if self.elapsedTimePhase >= 180.0:
            self.switchTrafficLight()
            return
        
        # minimo 10s di verde per un flusso e controllo di non essere in una fase con giallo o solo rosso
        if self.elapsedTimePhase > 10 and traci.trafficlight.getPhase(self.tlID) not in [1,2,4,5]:
            costH, costV = self.getFlowCosts()
            if (self.movingFlow == 'HORIZONTAL' and costH < costV) or (self.movingFlow == 'VERTICAL' and costV < costH):
                self.switchTrafficLight()
