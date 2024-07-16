# script che serve per estrarre i dati sul numero di veicoli circolanti a Bologna dal file del dataset

import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Modulo per ricavare i dati del numero di veicoli circolanti a Bologna")
parser.add_argument('-f', '--file-name', dest="filename", required=True, metavar="path/to/dataset_file.csv", help="File del dataset in CSV")
parser.add_argument('-H', '--hour', dest="hour", required=True, metavar="HH:00-HH:00", help='Fascia oraria da cui estrarre i dati')
arguments = parser.parse_args()

# Totale del numero medio di veicoli che passano in tutte le vie tra le 18 e le 19.
# Per ogni via la media dei veicoli che ci passano durante l'anno tra le 18 e le 19.
# Somma dei numeri medi.

df = pd.read_csv(arguments.filename, header=0, sep=';')
totale_veicoli_nella_via = dict()
totale_giorni_per_via = dict()
media_veicoli_nella_via = dict()

for _, row in df.iterrows():
    if row["Nome via"] not in totale_veicoli_nella_via and row["Nome via"] not in totale_giorni_per_via:
        totale_veicoli_nella_via[row["Nome via"]] = 0
        totale_giorni_per_via[row["Nome via"]] = 0

    totale_veicoli_nella_via[row["Nome via"]] += row[arguments.hour]
    totale_giorni_per_via[row["Nome via"]] += 1

for key, value in totale_veicoli_nella_via.items():
    media_veicoli_nella_via[key] = value / totale_giorni_per_via[key]

somma = 0
for value in media_veicoli_nella_via.values():
    somma += value

print(totale_veicoli_nella_via["VIA RAVENNA"])
print(totale_giorni_per_via["VIA RAVENNA"])
print(media_veicoli_nella_via["VIA RAVENNA"])
print(len(totale_veicoli_nella_via))
print("somma: ", somma)