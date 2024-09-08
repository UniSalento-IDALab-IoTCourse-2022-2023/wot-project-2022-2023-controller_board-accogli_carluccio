from connectionhelper import *
import paho.mqtt.client as mqtt
import json
import alertTypes
import queue
import caching as ch

message_queue = queue.Queue()
cache = ch.MessageCache()


def convert_message(msg:mqtt.MQTTMessage):
    try:
        json_msg = json.loads(msg.payload)

        if json_msg['type'].lower() == "distance" or json_msg['type'].lower() == "driver_away":
            distance_alert = alertTypes.DistanceAlert(json_msg['timestamp'], json_msg['type'].lower(), json_msg['technologyID'],
                                     json_msg['priority'], json_msg['workerID'], json_msg['machineryID'], json_msg['isEntryAlarm'])
            return distance_alert
        
        if json_msg['type'].lower() == "general":
            general_alert = alertTypes.GeneralAlert(json_msg['timestamp'], "general", json_msg['technologyID'],
                                     json_msg['priority'], json_msg['description'])
            return general_alert

    except json.JSONDecodeError as e:
        print("Errore durante la conversione del messaggio", e)


def on_message(client, userdata, msg):
    alert = convert_message(msg)

    # Meccanismo di gestione della duplicazione dei messaggi tramite cache
    if cache.exists(alert.timestamp):
        print("Duplicated message detected")
        return
    else:
        cache.add(alert.timestamp)
        
    cache.clean_up()

    # Processing tramite BLE e locale dell'alert ricevuto 
    if alert.type == "distance":
        alertTypes.DistanceAlert.process_BLE_notification(alert, message_queue)
        alertTypes.DistanceAlert.local_process_distance_alert(alert)
    
    if alert.type == "general":
        alertTypes.GeneralAlert.process_BLE_notification(alert, message_queue)
        alertTypes.GeneralAlert.local_process_general_alert(alert)
    
    if alert.type == "driver_away":
        return

    
    
        
    

def subscribe_to_alarm_topic(machineryID) -> mqtt.Client:
    # 1
    client = ConnectionHelper.mqttConnection(machineryID)
    machinery_topic = 'zone/default/machinery/'+machineryID+"/alarms"
    client.subscribe(machinery_topic)
    general_topic = 'zone/default/machinery/all/alarms'
    client.subscribe(general_topic)
    client.on_message = on_message
    return client

