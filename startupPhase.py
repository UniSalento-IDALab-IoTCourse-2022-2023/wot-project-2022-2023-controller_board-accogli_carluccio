from machineryConfiguration import MachineryConfiguration
from colorama import Fore, Style
import bleHelper as ble
from connectionhelper import ConnectionHelper
from bluezero import peripheral,adapter
import threading
import alertProcessing as alertProc
import paho.mqtt.client as mqtt
import hardwareDevices as hwD
import time
from terminalclearer import TerminalClearer
import alertTypes 
import dashboard as dash

# Variabile per la sincronizzazione tra le thread alla connessione operatore
operator_connected = threading.Event()
ble_connection = None

# TEST Da cambiare con a variabile locale list_mac_addresses
WHITELIST = ["e0:dc:ff:f4:3c:1e", "f4:60:e2:c0:2d:9f"]


##############################################################################################################
# Inizio ascolto eventi BLE in loop
def ble_publish(alert_service: peripheral.Peripheral):
    alert_service.publish()

# Creazione servizio BLE, creazione thread per l'ascolto indipendente degli eventi BLE e start
def manage_bluetooth(machinery_serial_number) -> threading.Thread:
    global ble_connection
    ble_connection = ble.service_creation(list(adapter.Adapter.available())[0], WHITELIST, operator_connected, machinery_serial_number)
    ble_events_thread = threading.Thread(target=ble_publish, args=(ble_connection.peripheral_device,))
    ble_events_thread.start()
    return ble_events_thread
##############################################################################################################

##############################################################################################################
def signal_connection_successfull():
    hwD.led_on_green()
    hwD.buzzer_beep(1)
    hwD.write_to_display("CONNESSO")

def signal_waiting_for_connection():
    print(Fore.YELLOW + Style.BRIGHT + f'In attesa di connessione operatore' + Style.RESET_ALL)
    hwD.led_on_blue()
    hwD.write_to_display("In attesa\r\ndi operatore..")

def signal_connection_lost():
    print(Fore.RED + Style.BRIGHT + f'OPERATORE DISCONNESSO. In attesa di riconnessione...' + Style.RESET_ALL)
    hwD.led_on_yellow()
    hwD.write_to_display("DISCONNESSO\r\nIn attesa..")
##############################################################################################################


##############################################################################################################
def check_today_configuration(machinery_id):
    configuration = MachineryConfiguration.retrieveConfiguration(machinery_id) 

    # Se non è presente usciamo
    if not configuration:
        print(Fore.RED + Style.BRIGHT + f'Macchinario non configurato per la data odierna' + Style.RESET_ALL)
        hwD.write_to_display("Macchinario\n\rdisabilitato")
        return False
 
    return configuration
##############################################################################################################

stop_event = threading.Event()

###############################################################
def simulation_processing(client_mqtt):
    #TerminalClearer.clear()
    while True:
        client_mqtt.loop_start()
        while ble_connection.device_connected is not None:
            pass
        # Gestione disconnessione
        if stop_event.is_set():
            return
        else:
            client_mqtt.loop_stop()
            signal_connection_lost()
            operator_connected.wait()

            if operator_connected.is_set:
                signal_connection_successfull()
###############################################################




''' Definizione delle operazioni di simulazione
    1. Check se il macchinario è nello stato attivo
    2. Avvio operazioni per setup dei dispositivi hardware presenti sul macchinario
    3. Controllo se è presente una configurazione per il macchinario
    4. Recupero della lista di mac addresses dalla configurazione
    5. Creazione del servizio BLE e inizio ascolto eventi in una thread separata e comunicazione tramite hardware
    6. In attesa che un operatore si connetta. La gestione avviene tramite evento di threading
    7. Segnalazione hardware per l'avvenuta connessione BLE
    8. Sottoscrizione topic allarmi macchinario
    9. Gestione sessione MQTT. Si continua ad ascoltare i messaggi finchè l'operatore è connesso con lo smartphone
    10. Inizializzazione della dashboard per la visualizzazione degli allarmi (per ora supportati distance e general)
    11. In caso di interruzione della simulazione, si effettuano le chiusure delle connessioni attive e le operazioni di pulizia necessarie
'''
def simulation(machinery):
   
    # 1
    '''if machinery.state != "ACTIVE":
        print(Fore.RED + Style.BRIGHT + f'Macchinario non attivo' + Style.RESET_ALL)
        return False'''

    # 2
    hwD.setup()

    print(machinery.plate.serial_number)

    # 3
    '''configuration = check_today_configuration(machinery.id)
    if not configuration:
        return False
    
    # 4
    list_mac_addresses = configuration.authMacAddresses
    print(f'Indirizzi MAC consentiti: {list_mac_addresses}')'''
    
    # 5
    signal_waiting_for_connection()
    ble_thread = manage_bluetooth(machinery.plate.serial_number)

    # 6
    operator_connected.wait()

    # 7
    signal_connection_successfull()

    # 8
    machinery_topic = 'zone/default/machinery/'+machinery.id+"/alarms"
    client_mqtt = alertProc.subscribe_to_alarm_topic(machinery.id)
    print("Sottoscrizione al topic allarme riuscita")

    # 9
    try:
        simulation_thread = threading.Thread(target=simulation_processing, args=(client_mqtt,))
        simulation_thread.start()

        # 10
        root_window = dash.tk.Tk()
        app = dash.AlarmDashboard(root_window)
        root_window.mainloop()
        
    except KeyboardInterrupt:
        # 11
        print("Interruzione simulazione...")

        stop_event.set()

        ConnectionHelper.close_mqtt_connecton(client_mqtt, machinery_topic)
        ble.close_ble_connection()
        ble_thread.join()
        simulation_thread.join()

        root_window.withdraw()
        root_window.tk.quit()

        hwD.turn_off_all()
        alertTypes.reset_stat()
       
        return True
