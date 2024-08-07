'''from cleaningpath import CleaningPath
from disposal import *
from disposalhelper import *
from alarmhelper import *'''
from colorama import init, Fore, Back, Style

import startupPhase
from terminalclearer import TerminalClearer
import dashboard as dash
import threading

from machinery import *

# MENU Functions
def showMainMenu():
    print("Seleziona azione")
    print("1. Simula macchinario (tramite ID)")
    print("0. Aggiorna lista macchinari") # (corrisponde a riavviare il tutto in modo che se un macchinario viene aggiunto mentre il nodo è in esecuzione, questo viene caricato in memoria)
    print("X. Esci")
    return input("> ")
def showMachineryMenuFor(machinery):
    machinery.toString()
    print("Seleziona azione")
    print("1. Startup macchinario") 
    print("X. Torna indietro")
    return input("> ")



# MAIN
# Ogni Macchinario presente viene caricato in memoria
# L'intento di questo script è quello di simulare il nodo raspberry presente su ogni macchinario. Nella realtà questo sarebbe
# svolto da una board specializzata
# I passi principali del main sono questi:
# 1. Caricare tutti i macchinari presenti nel db
# 2. Mostrare menu principale
def main():
    TerminalClearer.clear()

    while True:
        machineriesList = Machinery.getMachineriesList()

        while True:
            Machinery.printMachineryList(machineriesList)
            choice = showMainMenu()

            if choice == "1":
                TerminalClearer.clear()
                Machinery.printMachineryList(machineriesList)
                machineryID = input("Inserisci ID del macchinario da simulare: ")
                currentMachinery = Machinery.getMachineryBy(machineryID, machineriesList)

                TerminalClearer.clear()
                while currentMachinery != "not valid":    # se currentMachinery è "not valid" significa che ha inserito un id di machinery non valido

                    choice = showMachineryMenuFor(currentMachinery)
                    if choice == "1":
                        TerminalClearer.clear()
                       
                       # Esecuzione della simulazione del macchinario
                        simulation_status = startupPhase.simulation(currentMachinery)
                        if not simulation_status:
                            break
                        
                    elif choice == "x":
                        TerminalClearer.clear()
                        break
                    else:
                        TerminalClearer.clear()
                        print(Fore.RED + Style.BRIGHT + "Scelta non valida." + Style.RESET_ALL)

                if currentMachinery == "not valid":
                    TerminalClearer.clear()
                    print(Fore.RED + Style.BRIGHT + "Machinery ID non esistente." + Style.RESET_ALL)

            elif choice == "0":
                TerminalClearer.clear()
                break
            elif choice == "x":
                return
            else:
                TerminalClearer.clear()
                print(Fore.RED + Style.BRIGHT + "Scelta non valida." + Style.RESET_ALL)


if __name__ == '__main__':
    main()

