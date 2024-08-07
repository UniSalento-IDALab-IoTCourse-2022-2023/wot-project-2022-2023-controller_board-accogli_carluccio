import jwt
import datetime
import paho.mqtt.client as mqtt
import base64
from colorama import Fore, Style



class ConnectionHelper:

    hostAddress = '192.168.1.230'
    #hostAddress = '172.20.10.2'

    brokerURL = hostAddress # 'localhost'
    brokerPort = 1883
    
    username = "guest"
    password = "guest"

    baseURL = f'http://{hostAddress}:8081' # 'http://localhost'
   

    @staticmethod
    def token_jwt():
       
        # Chiave segreta per firmare il token
        '''secret_key = 'seedseedseedseedseedseedseedseedseedseedseed'

        # Converti la chiave segreta in un oggetto bytes
        secret_key_bytes = secret_key.encode()

        # Codifica la chiave segreta in Base64
        secret_key_base64 = secret_key#base64.b64encode(secret_key_bytes).decode()
        print(f"Secretkey_b64={secret_key_base64}")

        # Creazione di un payload con alcune informazioni utente
        payload = {
            'role': 'CONTROL_BOARD',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2),  # Scadenza del token

            "aud": [
                "http://siteManagementService:8081"
            ],
            "sub": "CONTROL_BOARD",
            "iat": datetime.datetime.utcnow(),
            "iss": "control board machinery",
        }

        # Creazione del token
        token = jwt.encode(payload=payload, key=secret_key_base64, algorithm='HS256')
        

        print("Token JWT generato: " + token)'''
        token_jwt = 'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOlsiaHR0cDovL3NpdGVNYW5hZ2VtZW50U2VydmljZTo4MDgxIl0sInJvbGUiOiJDT05UUk9MX0JPQVJEIiwidXNlcklEIjoiIiwic3ViIjoiY29udHJvbCBib2FyZCIsImlhdCI6MTcyMTM5MTI4MCwiaXNzIjoiaHR0cDovL2xvZ2luU2VydmljZTo4MDgwIiwiZXhwIjoyNzIxNDI3MjgwfQ.J6KCLjqDZnAeh2ifXgvjzn6Ie5slGkgKnf5KFejOBfg'
        return token_jwt

    @staticmethod
    def mqttConnection(machineryID):

        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                print(Fore.GREEN + Style.BRIGHT + f"Connesso al broker MQTT" + Style.RESET_ALL)
            else:
                print(Fore.RED + Style.BRIGHT + f"Connessione al broker MQTT fallita con codice di ritorno {reason_code}" + Style.RESET_ALL)

        client_id = f'machineryNode_{machineryID}'
        client = mqtt.Client(protocol=mqtt.MQTTv5, client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(ConnectionHelper.username, ConnectionHelper.password)
        client.on_connect = on_connect
        client.connect(ConnectionHelper.brokerURL, ConnectionHelper.brokerPort)
        return client

    @staticmethod
    def close_mqtt_connecton(client_mqtt:mqtt.Client, topic):
        client_mqtt.loop_stop()
        client_mqtt.unsubscribe(topic)
        client_mqtt.disconnect
