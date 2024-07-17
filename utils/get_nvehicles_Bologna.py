# Script che serve per estrarre i dati sul numero di veicoli circolanti a Bologna dal file del dataset
# Trova il totale del numero medio di veicoli che passano in tutte le vie tra le 18 e le 19.
# Calcola per ogni via la media dei veicoli che ci passano durante l'anno tra le 18 e le 19.
# Poi fa la somma dei numeri medi.

import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Modulo per ricavare i dati del numero di veicoli circolanti a Bologna")
parser.add_argument('-f', '--file-name', dest="filename", required=True, metavar="path/to/dataset_file.csv", help="File del dataset in CSV")
parser.add_argument('-H', '--hour', dest="hour", required=True, metavar="HH:00-HH:00", help='Fascia oraria da cui estrarre i dati')
arguments = parser.parse_args()

df = pd.read_csv(arguments.filename, header=0, sep=';')
totale_veicoli_nella_via = dict()
totale_giorni_per_via = dict()
media_veicoli_nella_via = dict()

# ogni riga è un giorno dell'anno
for _, row in df.iterrows():
    # se la via si vede per la prima volta inizializza a zero il valore del dizionario
    if row["Nome via"] not in totale_veicoli_nella_via and row["Nome via"] not in totale_giorni_per_via:
        totale_veicoli_nella_via[row["Nome via"]] = 0
        totale_giorni_per_via[row["Nome via"]] = 0

    # aggiungi i veicoli che passano in quella via in quel giorno dell'anno
    totale_veicoli_nella_via[row["Nome via"]] += row[arguments.hour]
    totale_giorni_per_via[row["Nome via"]] += 1

# media dei veicoli che passano nella via durante l'anno
for key, value in totale_veicoli_nella_via.items():
    media_veicoli_nella_via[key] = value / totale_giorni_per_via[key]

# somma del numero medio di veicoli che passano nelle vie durante l'anno
somma = 0
for value in media_veicoli_nella_via.values():
    somma += value

print("Totale veicoli: ", somma)