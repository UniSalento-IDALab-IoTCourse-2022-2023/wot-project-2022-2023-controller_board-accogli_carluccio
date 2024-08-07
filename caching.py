import time

# CLASSE PER LA GESTIONE DI UNA SEMPLICE CACHE PER RILEVARE MESSAGGI DUPLICATI
class MessageCache:
    def __init__(self, expiration_time=60):
        self.cache = {}
        self.expiration_time = expiration_time
    
    # Cache composta da coppie (timestamp->id messaggio; tempo inserimento in cache)
    def add(self, message_id):
        self.cache[message_id] = time.time()

    # Se il messaggio è presente in cache ed è valido ritorna True, altrimenti elimina quel messaggio dalla cache perchè è passato troppo tempo
    def exists(self, message_id):
        if message_id in self.cache:
            if time.time() - self.cache[message_id] <= self.expiration_time:
                return True
            else:
                del self.cache[message_id]
                return False

    # Funzione di pulizia della cache per evitare la sua crescita indefinita
    def clean_up(self):
        current_time = time.time()
        keys_to_delete = [key for key, timestamp in self.cache.items() if current_time - timestamp > self.expiration_time]
        for key in keys_to_delete:
            del self.cache[key]