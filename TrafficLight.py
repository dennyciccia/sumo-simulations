import traci

J = 100
K = 1

class TrafficLight:
    def __init__(self, tlID):
        self.__tlID = tlID
        self.__elapsedTimePhase = 0     # da quanto tempo è attiva la fase corrente (s)
    
    @property
    def tlID(self):
        return self.__tlID
    
    @property
    def movingFlow(self):
        if traci.trafficlight.getPhase(self.tlID) in [0,1,2]:   # flusso orizzontale
            return 'A'
        elif traci.trafficlight.getPhase(self.tlID) in [3,4,5]: # flusso verticale
            return 'B'

    @property
    def elapsedTimePhase(self):
        return self.__elapsedTimePhase
    
    @elapsedTimePhase.setter
    def elapsedTimePhase(self, value):
        self.__elapsedTimePhase = value

    # switch del semaforo per cambiare il flusso che si muove
    def changeMovingFlow(self):
        traci.trafficlight.setPhase(self.tlID, traci.trafficlight.getPhase(self.tlID)+1)
    
    # calcolo dei costi dei flussi
    def getFlowCosts(self):
        costA = costB = 0
        
        for edge in ["E0", "-E2"]:
            for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                costA += J + K * (traci.vehicle.getSpeed(vehicle)**2)
                #costA += J + (30 if self.movingFlow == 'A' else 1) * (traci.vehicle.getSpeed(vehicle)**2)
        
        edge = "-E1"
        for vehicle in traci.edge.getLastStepVehicleIDs(edge):
            costB += J + K * (traci.vehicle.getSpeed(vehicle)**2)
            #costB += J + (30 if self.movingFlow == 'B' else 1) * (traci.vehicle.getSpeed(vehicle)**2)
        
        return costA, costB
    
    def tryToSkipRed(self):
        meanSpeedE0 = traci.edge.getLastStepMeanSpeed("E0")
        vehicleNumberE0 = traci.edge.getLastStepVehicleNumber("E0")
        meanSpeedMinusE2 = traci.edge.getLastStepMeanSpeed("-E2")
        vehicleNumberMinusE2 = traci.edge.getLastStepVehicleNumber("-E2")
        meanSpeedMinusE1 = traci.edge.getLastStepMeanSpeed("-E1")
        vehicleNumberMinusE1 = traci.edge.getLastStepVehicleNumber("-E1")
        # se i veicoli sono fermi o non ci sono vai alla fase verde
        if (self.movingFlow == 'A' and (meanSpeedE0 < 1.0 or vehicleNumberE0 == 0) and (meanSpeedMinusE2 < 1.0 or vehicleNumberMinusE2 == 0)) or (self.movingFlow == 'B' and (meanSpeedMinusE1 < 1.0 or vehicleNumberMinusE1 == 0)):
            traci.trafficlight.setPhase(traci.trafficlight.getPhase(self.tlID)+1)
    
    # azioni eseguite ad ogni step della simulazione
    def performStep(self):
        # calcolo del tempo trascorso nella fase attuale
        self.elapsedTimePhase = round(traci.trafficlight.getPhaseDuration(self.tlID) - (traci.trafficlight.getNextSwitch(self.tlID) - traci.simulation.getTime()), 3)
        
        # se siamo alla fine della fase giallo prova a saltare la fase di solo rosso se è sicuro farlo
        #if traci.trafficlight.getPhase(self.tlID) in [1,4] and 2.8 < self.elapsedTimePhase < 3.0:
        #    self.tryToSkipRed()

        # massimo 180s di verde per un flusso
        if self.elapsedTimePhase >= 180.0:
            self.changeMovingFlow()
            return
        
        # minimo 10s di verde per un flusso e controllo di non essere in una fase con giallo o solo rosso
        if self.elapsedTimePhase > 10 and traci.trafficlight.getPhase(self.tlID) not in [1,2,4,5]:
            costA, costB = self.getFlowCosts()
            if (self.movingFlow == 'A' and costA < costB) or (self.movingFlow == 'B' and costB < costA):
                self.changeMovingFlow()