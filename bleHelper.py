# Standard modules
import logging
import random
import time

# Bluezero modules
from bluezero import async_tools
from bluezero import adapter, device
from bluezero import peripheral
import dbus.service
from gi.repository import GLib
import threading
import asyncio as asyncio
import dbus


import alertProcessing as alertProc
import queue as q
from typing import List


# Custom service uuid
ALARM_BASEINFO_SRVC = '12341000-1234-1234-1234-123456789abc'

# Custom characteristics uuids
ALARM_BASEINFO_CHRC = '12341001-1234-1234-1234-123456789abc'
GENERAL_ADDON_CHRC = '12341002-1234-1234-1234-123456789abc'

# Bluetooth SIG adopted UUID for descriptors
ALARM_UDESC_DSCP = '2901'

# Coda messaggi usata per la comunicazione tra thread
queue = alertProc.message_queue

object_path = "/ukBaz/bluezero"


class BLE_connection_helper:
    def __init__(self, peripheral_device: peripheral.Peripheral, device_connected:device.Device, whitelist:List[str], event_sync:threading.Event):
        self.peripheral_device = peripheral_device
        self.device_connected = device_connected
        self.whitelist = whitelist
        self.event_sync = event_sync

ble_connection = None


# Valori delle caratteristiche aggiornati
characteristics_value = {
    "base_info": None,
    "general" : None
}

###############################################################################################################
# UTILITY FUNCTIONS


# Controllo dispositivi autorizzati in base agli indirizzi MAC nella whitelist
def is_whitelisted(device:device.Device):
    print(device.address)

    if device.address.casefold() in [a.casefold() for a in ble_connection.whitelist]:
        print("Auth")
        return True
    else:
        return False


def on_connect(ble_device:device.Device):
    if not ble_connection.device_connected:
        if is_whitelisted(ble_device):
            ble_connection.device_connected = ble_device
            print("Connesso a "+str(ble_device.address))
            ble_connection.event_sync.set()
        else:
            ble_device.disconnect()
            print("Dispositivo non autorizzato")
    else:
        ble_device.disconnect()


def on_disconnect(adapter_address, device_address):
    if device_address == None or not ble_connection.device_connected:
        return 
    
    if device_address != ble_connection.device_connected.address:
        return
    
    if ble_connection.event_sync.is_set():
        ble_connection.device_connected = None
        ble_connection.event_sync.clear()

    print("Disconnesso da "+device_address)
###############################################################################################################

###############################################################################################################
# Funzioni per la lettura delle caratteristiche   
def read_general_info():
    """
    Example read callback. Value returned needs to a list of bytes/integers
    in little endian format.
    """
    # Se un allarme non è ancora stato generato e si esegue la read da un central, viene restituito il byte 0
    if not characteristics_value.get('general'):
        return bytes([0])
    
    return characteristics_value.get('general')


def read_base_info():
    """
    Example read callback. Value returned needs to a list of bytes/integers
    in little endian format.
    """
    # Se un allarme non è ancora stato generato e si esegue la read da un central, viene restituito il byte 0
    if not characteristics_value.get('base_info'):
        return bytes([0])
    
    return characteristics_value.get('base_info')
###############################################################################################################




###############################################################################################################
# Gestione notifica allarmi
def check_alarms(characteristic):
    """
    Example of callback to send notifications

    :param characteristic:
    :return: boolean to indicate if timer should continue
    """

    # get messaggio dalla coda
    try:
        alarm = queue.get_nowait()
        print("EI SONO LA THREAD BLE: {}",alarm)

        # Nuovo allarme ricevuto. Scrittura della caratteristica di base
        # Causes characteristic to be updated and send notification
        global characteristics_value
        characteristics_value['base_info'] = alarm['info']

        characteristic.set_value(alarm['info'])

        if alarm['type'] == "general":
            general_characteristic = ble_connection.peripheral_device.characteristics[1]
            
            characteristics_value['general'] = alarm['general']

            general_characteristic.set_value(alarm['general'])

        # Segnalazione fine elaborazione messaggio
        queue.task_done()

    except q.Empty:
        pass

    # Return True to continue notifying. Return a False will stop notifications
    return characteristic.is_notifying



# Attivata quando il centrale BLE richiede di essere notificato per tale caratteristica
def notify_callback(notifying, characteristic):
    """
    Noitificaton callback example. In this case used to start a timer event
    which calls the update callback ever 1 second

    :param notifying: boolean for start or stop of notifications
    :param characteristic: The python object for this characteristic
    """
    print(notifying)

    if notifying:
        async_tools.add_timer_seconds(1, check_alarms, characteristic)
###############################################################################################################

def descriptor_base():
    title="Alarm info. Format: type-priority(2 bytes)"
    title_bytes = title.encode()
    value = []
    for byte in title_bytes:
        value.append(byte)
    return value

###############################################################################################################
# CREAZIONE PERIFERICO CON SERVIZI
def service_creation(adapter:adapter.Adapter, whitelist, operator_connected, machinery_serial_number) -> BLE_connection_helper:

    # Create peripheral
    machinery_alarms = peripheral.Peripheral(adapter.address,
                                        local_name=machinery_serial_number,
                                        appearance=128)
    # Add service
    machinery_alarms.add_service(srv_id=1, uuid=ALARM_BASEINFO_SRVC, primary=True)
    
    # Add characteristics
    machinery_alarms.add_characteristic(srv_id=1, chr_id=1, uuid=ALARM_BASEINFO_CHRC,
                                   value=[], notifying=False,
                                   flags=['read', 'notify'],
                                   read_callback=read_base_info,
                                   write_callback=None,
                                   notify_callback=notify_callback
                                   )
    machinery_alarms.add_characteristic(srv_id=1, chr_id=2, uuid=GENERAL_ADDON_CHRC,
                                   value=[], notifying=False,
                                   flags=['read'],
                                   read_callback=read_general_info,
                                   write_callback=None,
                                   notify_callback=None
                                   )

    # Add descriptor
    machinery_alarms.add_descriptor(srv_id=1, chr_id=1, dsc_id=1, uuid=ALARM_UDESC_DSCP,
                                   value=descriptor_base(), flags=['read'])


    
    # Publish peripheral and start event loop
    machinery_alarms.on_connect=on_connect
    machinery_alarms.on_disconnect=on_disconnect

    global ble_connection
    ble_connection = BLE_connection_helper(machinery_alarms, None, whitelist, operator_connected)
    return ble_connection
###############################################################################################################



###############################################################################################################
# CHIUSURA CONNESSIONE
def close_ble_connection():

    if ble_connection is not None:
        # Disconnessione dispositivo connesso se presente
        if ble_connection.device_connected is not None:
            ble_connection.device_connected.disconnect() 
            ble_connection.device_connected = None
        
        # Terminazione ascolto eventi BLE
        ble_connection.peripheral_device.mainloop.quit()

        # Eliminazione del servizio BLE registrato
        ble_connection.peripheral_device.ad_manager.unregister_advertisement(ble_connection.peripheral_device.advert)

        dbusConnection = ble_connection.peripheral_device.advert.connection
        dbusPath = ble_connection.peripheral_device.advert._object_path
        
        ble_connection.peripheral_device.advert.remove_from_connection(dbusConnection, dbusPath)

        ble_connection.peripheral_device.srv_mng.unregister_application(ble_connection.peripheral_device.app)

        dbusConnection2 = ble_connection.peripheral_device.app.connection
        dbusPath2 = ble_connection.peripheral_device.app._object_path
        ble_connection.peripheral_device.app.remove_from_connection(dbusConnection2, dbusPath2)
        '''#dbus.service.Object.remove_from_connection(ble_connection.peripheral_device.advert)
        #ble_connection.peripheral_device.advert.remove_from_connection()
        dbusConnection = ble_connection.peripheral_device.advert.connection
        #dbusConnection = ble_connection.peripheral_device.app.connection
        dbusPath = ble_connection.peripheral_device.advert._object_path
        #ble_connection.peripheral_device.app.remove_from_connection()
        print(ble_connection.peripheral_device.app.path)
        #dbus.SystemBus().get_object(, object_path)
                app = ble_connection.peripheral_device.app
        ble_connection.peripheral_device.srv_mng.unregister_application(app)
        
        dbus.service.Object.remove_from_connection(app)
        adv_path = '/ukBaz/bluezero/advertisement0001'
        
        srv_path ='/ukBaz/bluezero/service0001'
        
        print(ble_connection.peripheral_device.srv_mng.manager_obj.bus_name)
        proxy = dbus.SystemBus().get_object(ble_connection.peripheral_device.srv_mng.manager_obj.bus_name, object_path)

        #dbus.SystemBus().get_object(ble_connection.peripheral_device.srv_mng.manager_obj.bus_name, object_path).
        #dbusConnection2 = ble_connection.peripheral_device.advert.connection
        #ble_connection.peripheral_device.advert.remove_from_connection(dbusConnection2, adv_path)
        #dbus.SystemBus().release_name(ble_connection.peripheral_device.srv_mng.manager_obj.bus_name)'''
        

###############################################################################################################    

