
import json
import threading
from datetime import datetime

from colorama import Fore, Style
from connectionhelper import ConnectionHelper
from typing import List

'''
    Classe per la gestione della configurazione del macchinario nella fase di startup
    1. Sottoscrizione al topic di configurazione
    2. Logica gestione messaggio di configurazione
'''

message_arrived = threading.Event()

class MachineryConfiguration:
    def __init__(self, date, machineryID, authMacAddresses):
        self.date = date,
        self.machineryID = machineryID,
        self.authMacAddresses = authMacAddresses


    last_message = None
    configuration_topic = 'zone/default/machinery/configuration'

    ''' Metodo che si occupa di individuare la configurazione del giorno per il macchinario scelto da simulare '''
    @staticmethod
    def searchConfiguration(machinery_id, message):

        content:List[MachineryConfiguration] = json.loads(message)
        today_date = datetime.now().date()

        for message in content:
            if message['machineryID'] == machinery_id and \
                    datetime.strptime(message['date'], '%Y-%m-%d').date() == today_date:
                configuration = MachineryConfiguration(message["date"],
                                                       message["machineryID"],
                                                       message["authMacAddresses"])
                return configuration



    def on_message(client, userdata, msg):
        # Chiamata alla funzione specifica per gestire il messaggio ricevuto
        MachineryConfiguration.last_message = msg.payload.decode('utf-8')
        message_arrived.set()
        #MachineryConfiguration.searchConfiguration(msg.payload.decode())

    '''
        1. Connessione al broker MQTT e subscribe al topic di configurazione
        2. Inizio ascolto 
        3. Attesa fino alla ricezione del messaggio di configurazione
        4. Termine ascolto e disconnessione
        5. Ricerca della configurazione per il macchinario da simulare

    '''
    @staticmethod
    def retrieveConfiguration(machineryID):
        # 1
        client = ConnectionHelper.mqttConnection(machineryID)
        client.subscribe(MachineryConfiguration.configuration_topic)
        client.on_message = MachineryConfiguration.on_message

        # 2
        client.loop_start()

        # 3
        print(Fore.YELLOW + Style.DIM + f'In attesa di configurazione...' + Style.RESET_ALL)
        message_arrived.wait()

        # 4
        client.loop_stop()
        client.disconnect()

        # 5: messaggio arrivato
        new_configuration = MachineryConfiguration.searchConfiguration(machineryID, MachineryConfiguration.last_message)
        return new_configuration







