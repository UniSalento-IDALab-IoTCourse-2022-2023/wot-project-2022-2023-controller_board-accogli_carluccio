import requests
import json
from tabulate import tabulate
from colorama import init, Fore, Back, Style

from connectionhelper import ConnectionHelper


class IdentificationPlate:
    def __init__(self, year, manufacturer_name, serial_number, model):
        self.year = year
        self.manufacturer_name = manufacturer_name
        self.serial_number = serial_number
        self.model = model
        pass

# CLASSES
class Machinery:
    def __init__(self, id, name, type, state, plate, spec, isRemote):
        self.id = id
        self.name = name
        self.type = type
        self.state = state
        self.plate = plate
        self.spec = spec
        self.isRemote = isRemote


    @staticmethod
    def getMachineriesList():

        # get lista Bins ALLOCATI mediante SmartBinMS
        url = f'{ConnectionHelper.baseURL}/api/machineries/'
        token_jwt = ConnectionHelper.token_jwt()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token_jwt}'
        }

        # Effettua la richiesta GET
        response = requests.get(url, headers=headers)
        #response = requests.get(url)

        # Verifica lo stato della risposta
        if response.status_code != 200:
            print(Fore.RED + Style.BRIGHT + f"Richiesta lista macchinari non riuscita. Codice di stato: {response.status_code}" + Style.RESET_ALL)
            return

        # Contenuto della risposta
        content = json.loads(response.text)

        machineriesList = []

        for machinery_json in content:
            machinery = Machinery(machinery_json["id"],
                           machinery_json["name"],
                           machinery_json["typeName"],
                           machinery_json["state"],
                           machinery_json["plate"],
                           machinery_json["spec"],
                           machinery_json["isRemote"])
            machinery.plate = IdentificationPlate(machinery.plate["yearOfManufacture"],
                                                  machinery.plate["manufacturerName"],
                                                  machinery.plate["serialNumber"],
                                                  machinery.plate["model"])
            machineriesList.append(machinery)

        return machineriesList

    @staticmethod
    def printMachineryList(machineriesList):

        if not machineriesList: return

        headers = ["ID", "Nome", "Tipologia", "Modalità guida", "Stato"]
        tabulateData = []
        for machinery in machineriesList:
            control_mode = "On-board"
            if machinery.isRemote:
                control_mode = "Remote"

            if machinery.state == "INACTIVE" or machinery.state == "TO_CONFIGURE":
                tabulateData.append((machinery.id, machinery.name, machinery.type, control_mode, Fore.RED + Style.BRIGHT + machinery.state + Style.RESET_ALL))
            else:
                tabulateData.append((machinery.id, machinery.name, machinery.type, control_mode, Fore.GREEN + Style.BRIGHT + machinery.state + Style.RESET_ALL))

        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        print("\n" + table + "\n")

    @staticmethod
    def getMachineryBy(machineryID, machineriesList):
        for machinery in machineriesList:
            if machinery.id == machineryID:
                return machinery
        return "not valid"

    def toString(self):
        headers = ["ID", "Nome", "Tipologia", "Modalità guida", "Stato"]

        control_mode = "On-board"
        if self.isRemote:
            control_mode = "Remote"

        if self.state != "ACTIVE":
            tabulateData = [(self.id, self.name, self.type, control_mode, Fore.RED + Style.BRIGHT + self.state + Style.RESET_ALL)]
        else:
            tabulateData = [(self.id, self.name, self.type, control_mode, self.state)]


        # Utilizza tabulate per formattare e stampare la tabella
        table = tabulate(tabulateData, headers, tablefmt="plain")
        print("\n" + table + "\n")