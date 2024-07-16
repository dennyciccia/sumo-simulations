import traci

J = 100
K = 1
Ke = 5


class Flow:
    # un flusso è realtivo a una sola fase di verde
    # l'ID del flusso è l'indice della fase del semaforo a cui è realtivo
    # un flusso è composto da degli edge che si muovono

    def __init__(self, id, edges):
        self.__ID = id          # ID del flusso
        self.__edges = edges    # edge che si muovono in questo flusso
        self.__cost = 0         # costo del flusso calcolato
        self.__gone = False     # indica se il flusso è già andato in questo ciclo

    @property
    def ID(self):
        return self.__ID

    @property
    def edges(self):
        return self.__edges

    @property
    def cost(self):
        return self.__cost

    @cost.setter
    def cost(self, value):
        self.__cost = value

    @property
    def gone(self):
        return self.__gone

    @gone.setter
    def gone(self, value):
        self.__gone = value

    def containsExactlyAllEdges(self, edges):
        if len(edges) != len(self.edges):
            return False
        for i in range(len(edges)):
            if sorted(edges)[i] != sorted(self.edges)[i]:
                return False
        return True


class TrafficLightV2:
    def __init__(self, tlID, enhancements):
        self.__tlID = tlID                  # ID del semaforo
        self.__enhancements = enhancements  # lista dei miglioramenti dell'algoritmo

        # ottenimento del programma del semaforo
        self.__program = traci.trafficlight.getAllProgramLogics(self.__tlID)[1]

        # identificazione delle fasi
        self.__preMainPhases = []   # fasi subito prima del verde
        self.__mainPhases = []      # fasi in cui c'è il verde
        self.__preRedPhases = []    # fasi di giallo prima del rosso
        self.__allRedPhases = []    # fasi in cui c'è solo rosso

        for i, phase in enumerate(self.__program.phases):
            if phase.duration >= 50:
                self.__mainPhases.append(i)
                self.__preMainPhases.append((i-1) % len(self.__program.phases))
            if phase.state == len(phase.state) * 'r':
                self.__allRedPhases.append(i)
                self.__preRedPhases.append(i-1)

        # determinazione dei flussi
        self.__flows = []
        for phaseIndex in self.__mainPhases:
            movingEdges = []
            phaseString = self.__program.phases[phaseIndex].state.lower()

            # qua scorri tutti i controlled links (sono nella forma [(in, out, via)])
            # poi metti nei movingEdges quelli che nella phaseString hanno la 'g' in corrispondenza
            for j, link in enumerate(traci.trafficlight.getControlledLinks(self.__tlID)):
                if len(link) != 0:
                    edge = link[0][0][:-2]
                    if phaseString[j] == 'g' and edge not in movingEdges:
                        movingEdges.append(edge)

            self.__flows.append(Flow(phaseIndex, movingEdges))

        # quando inizia la simulazione il primo flow è già gone
        self.__flows[0].gone = True

        # indicazione di quale sarà la prossima fase in cui andare
        self.__nextPhase = -1

    @property
    def tlID(self):
        return self.__tlID

    @property
    def enhancements(self):
        return self.__enhancements

    @property
    def preMainPhases(self):
        return self.__preMainPhases

    @property
    def mainPhases(self):
        return self.__mainPhases

    @property
    def preRedPhases(self):
        return self.__preRedPhases

    @property
    def allRedPhases(self):
        return self.__allRedPhases

    @property
    def flows(self):
        return self.__flows

    @property
    def nextPhase(self):
        return self.__nextPhase

    @nextPhase.setter
    def nextPhase(self, value):
        self.__nextPhase = value

    def movingFlow(self):
        movingEdges = []
        phaseString = traci.trafficlight.getRedYellowGreenState(self.tlID).lower()

        # controlla che l'edge abbia il verde nella fase corrente,
        # se si aggiungilo agli edge in movimento
        for i, link in enumerate(traci.trafficlight.getControlledLinks(self.tlID)):
            if len(link) != 0:
                edge = link[0][0][:-2]
                if (phaseString[i] in ['g', 'y']) and edge not in movingEdges:
                    movingEdges.append(edge)

        # il moving flow è quello che ha tutti i movingEdges
        for flow in self.flows:
            if flow.containsExactlyAllEdges(movingEdges):
                return flow
        return None

    def switchTrafficLight(self):
        # switch del semaforo per cambiare il flusso che si muove
        notGoneFlows = [ f for f in self.flows if not f.gone ]
        maxCost = -1
        if len(notGoneFlows) != 0:
            maxCost = max([ f.cost for f in notGoneFlows ]) if 3 in self.enhancements else -1

        # se i flow sono tutti andati almeno una volta allora ricomincia il ciclo
        if len(notGoneFlows) == 0 or maxCost == 0:
            for f in self.flows: f.gone = False
            sortedFlows = sorted(self.flows, key=lambda x:x.cost, reverse=True)
        else:
            sortedFlows = sorted(notGoneFlows, key=lambda x:x.cost, reverse=True)

        # fai andare il flow con il costo più alto
        sortedFlows[0].gone = True
        self.nextPhase = sortedFlows[0].ID
        traci.trafficlight.setPhase(self.tlID, traci.trafficlight.getPhase(self.tlID)+1)

    def calcFlowCosts(self):
        # calcolo dei costi dei flussi
        for flow in self.flows:
            flow.cost = 0
            for edge in flow.edges:
                for vehicle in traci.edge.getLastStepVehicleIDs(edge):
                    flow.cost += J + (Ke if self.movingFlow() == flow else K) * (traci.vehicle.getSpeed(vehicle) ** 2)

    def tryToSkipRed(self):
        # prova a saltare la fase di solo rosso se è sicuro farlo
        # nella mappa di bologna questo non viene mai eseguito
        vehicleNumber = [ 0 for _ in range(len(self.flows)) ]
        meanSpeed = [ 0 for _ in range(len(self.flows)) ]

        # calcola velocità media e numero di veicoli su ogni edge di ogni flusso e controlla se si può saltare la fase di rosso
        skip = True
        for i, flow in enumerate(self.flows):
            for edge in flow.edges:
                vehicleNumber[i] += traci.edge.getLastStepVehicleNumber(edge)
                meanSpeed[i] += 0 if vehicleNumber[i] == 0 else traci.edge.getLastStepMeanSpeed(edge)
            meanSpeed[i] /= len(flow.edges)

            # per il flusso in movimento (quello che ha il giallo) guarda se c'è qualcuno sulla strada che non è già fermo
            if flow == self.movingFlow() and vehicleNumber[i] != 0 and meanSpeed[i] >= 1.0:
                skip = False

        # se i veicoli sugli edge degli altri flussi sono fermi o non ci sono vai alla fase verde successiva
        if skip:
            traci.trafficlight.setPhase(self.tlID, self.nextPhase)

    # azioni eseguite a ogni step della simulazione
    def performStep(self):
        # massimo 180s di verde per un flusso
        if traci.trafficlight.getSpentDuration(self.tlID) >= 180.0:
            self.switchTrafficLight()
            return

        # se siamo alla fine della fase attuale
        if traci.trafficlight.getSpentDuration(self.tlID) == traci.trafficlight.getPhaseDuration(self.tlID) - 1:
            # se siamo in una fase prima del rosso prova a saltare la fase di rosso
            if traci.trafficlight.getPhase(self.tlID) in self.preRedPhases:
                self.tryToSkipRed()
            # se siamo in una fase prima del verde passa alla prossima fase indicata
            elif traci.trafficlight.getPhase(self.tlID) in self.preMainPhases:
                traci.trafficlight.setPhase(self.tlID, self.nextPhase)
            return

        # minimo 10s di verde per un flusso
        if traci.trafficlight.getSpentDuration(self.tlID) > 10:
            # controllo di essere in una fase di verde
            if traci.trafficlight.getPhase(self.tlID) in self.mainPhases:
                self.calcFlowCosts()
                if self.movingFlow().cost < max([ f.cost for f in self.flows ]):
                    self.switchTrafficLight()
                return


# si può fare che nell'init si definiscono tutte le proprietà del semaforo
# IDEA (ma quale idea, non vedi che lei non ci sta):
# si può organizzare un semaforo in modo che in un ciclo tutti i flussi devono andare prima che un flusso vada di nuovo.
# si può fare che quando un il costo di un flusso fermo supera il costo del flusso in movimento allora passa a quello.
# se è già passato nel ciclo allora passano tutti gli altri in ordine di costo,
# poi quando ricomincia il ciclo presumibilmente quel flusso avrà ancora il costo alto quindi passerà per primo nel nuovo ciclo.

# Cose che si possono migliorare:
# - quando l'algoritmo deve decidere il prossimo flusso che deve andare, può anche far saltare un ciclo a un flusso se ha un costo prossimo a zero
# - se non ci sono veicoli che stanno passando in una strada allora si possono anche saltare le fasi in cui c'è il verde per libreare l'incrocio