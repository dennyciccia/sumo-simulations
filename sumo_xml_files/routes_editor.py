import argparse
import xml.etree.ElementTree as et

parser = argparse.ArgumentParser("Correttore per le routes")
parser.add_argument('-i', '--input', required=True, dest="input")
parser.add_argument('-o', '--output', required=True, dest="output")
arguments = parser.parse_args()

# Carica il file XML
tree = et.parse(arguments.input)
root = tree.getroot()

# Modifica gli attributi per ogni riga
for i, elem in enumerate(root):
    elem.set("id", "route" + str(i+1))

# Salva il file XML modificato
tree.write(arguments.output)