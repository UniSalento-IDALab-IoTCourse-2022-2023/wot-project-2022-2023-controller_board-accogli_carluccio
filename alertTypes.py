import hardwareDevices as hwD
from colorama import Fore, Style
from terminalclearer import TerminalClearer
import struct
import queue

'''
    Classe usata per definire le varie tipologie di allarmi supportate e i relativi comportamenti del sistema
'''
##############################################################################################
# Dizionari usati per il mapping di campi in interi per la codifica nella notifica BLE
priority_mapping = {
    "communication": 0,
    "warning": 1,
    "danger": 2
}

type_mapping = {
    "distance": 0,
    "general": 1,
}
##############################################################################################
num_entry_distance_alarm = 0


##############################################################################################
# Gestione segnalazione hardware
def signal_danger():
    hwD.led_on_red()
    hwD.buzzer_on()

def shut_off_signal_danger():
    hwD.led_on_green()
    hwD.buzzer_off()
##############################################################################################

message_queue_dash = queue.Queue()


''' Funzione per creare la caratteristica di base codificata: 
    0x 
    1 byte per indicare la tipologia di allarme come specificato nel type_mapping
    + 1 byte per indicare la priorità di allarme come specificato nel priority_mapping

'''
def create_encoded_alarm(alert):
    priority_alert = priority_mapping.get(alert.priority.lower(), 1)
    type_alert = type_mapping.get(alert.type.lower(), 0)
    return struct.pack('<BB', type_alert, priority_alert)


###############################################################################################################
# ALLARME DI DISTANZA 
class DistanceAlert:
    def __init__(self, timestamp, type, technologyID, priority, workerID, machineryID, isEntryAlarm):
        self.timestamp = timestamp
        self.type = type
        self.technologyID = technologyID
        self.priority = priority
        self.workerID = workerID
        self.machineryID = machineryID
        self.isEntryAlarm = isEntryAlarm

    def local_process_distance_alert(alert):
        if alert.isEntryAlarm:
            global num_entry_distance_alarm
            num_entry_distance_alarm += 1
            TerminalClearer.clear()
            print(Fore.RED + Style.BRIGHT + f'PERICOLO! Operatori nelle vicinanze' + Style.RESET_ALL)
            signal_danger()

            message_distance = {"type": "distance", "counter": num_entry_distance_alarm}
            message_queue_dash.put(message_distance)

        else:
            # Controllo aggiuntivo per sicurezza
            if num_entry_distance_alarm == 0:
                print("Errore. Exit alarm senza un entry alarm")
                return 
            
            num_entry_distance_alarm -= 1

            if num_entry_distance_alarm == 0:
                TerminalClearer.clear()
                print(Fore.GREEN + Style.BRIGHT + f'AREA LIBERA. Riprendere operazioni' + Style.RESET_ALL)
                shut_off_signal_danger()

                message_distance = {"type": "distance", "counter": 0}
                message_queue_dash.put(message_distance)
     
    ''' Funzione per la gestione dell'inoltro notifiche BLE
        1. Creazione caratteristica di base codificata
        2. Creazione del messaggio di comunicazione tra thread
        3. Invio del messaggio su una coda di messaggi su cui è in ascolto la thread BLE
    '''
    def process_BLE_notification(alert, message_queue:queue.Queue):
        encoded_alarm = create_encoded_alarm(alert)
        message = {"type": "distance", "info": encoded_alarm}
        message_queue.put(message)
        print(message)
###############################################################################################################





###############################################################################################################
# ALLARME GENERALE
class GeneralAlert:
    def __init__(self, timestamp, type, technologyID, priority, description):
        self.timestamp = timestamp
        self.type = type
        self.technologyID = technologyID
        self.priority = priority
        self.description = description

    def local_process_general_alert(alert):
        print(Fore.MAGENTA + Style.BRIGHT + f'ALLARME GENERALE: {alert.description}' + Style.RESET_ALL)

        message_general = {"type": "general", "text": alert.description, "priority":alert.priority.lower()}
        message_queue_dash.put(message_general)
    
    def process_BLE_notification(alert, message_queue:queue.Queue):
        encoded_alarm = create_encoded_alarm(alert)

        message = {"type": alert.type,"info": encoded_alarm, "general": alert.description.encode()}
        message_queue.put(message)
###############################################################################################################




# UTILITY FUNCTIONS
def reset_stat():
        global num_entry_distance_alarm
        num_entry_distance_alarm = 0
