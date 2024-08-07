import tkinter as tk
from tkinter import scrolledtext
from tkinter import ttk
import random
import threading
import time
from PIL import Image, ImageTk
import queue as q
import alertTypes as alertTypes

image_tk = None
root_window:tk.Tk = None
queue_dash = alertTypes.message_queue_dash

def check_queue():
    try:
        new_alarm = queue_dash.get_nowait()

        if new_alarm["type"] == "distance":
            AlarmDashboard.update_distance_alarms(new_alarm["counter"])
            print(new_alarm["counter"])
        else:
            AlarmDashboard.update_general_alarms(new_alarm["text"], new_alarm["priority"])

        queue_dash.task_done()
    except q.Empty:
        pass

    root_window.after(2000, check_queue)


class AlarmDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Alarm Dashboard")

        # Setting dei parametri di base
        global root_window 
        root_window = root

        window_width = 800
        window_height = 375
        root.geometry(f"{window_width}x{window_height}")
        root.configure(background="white")
        root.resizable(False, False)
        

        # Primo aggiornamento dashboard con indicazione di area libera
        AlarmDashboard.update_distance_alarms(0)
        check_queue()
        
                      
        
    
    def update_distance_alarms(alarm_counter):
        global image_tk
        global root_window

        # Eliminazione di tutti i widget precedenti senza distruggere l'intera finestra
        if image_tk is not None:
            for widget in root_window.winfo_children():
                widget.destroy()


        if alarm_counter == 0:
            image_path = './icons/green_icon.png'    
            
            image_pil = Image.open(image_path)
            image = image_pil.resize((308,308))
            image_tk  = ImageTk.PhotoImage(image)
            image_label = tk.Label(root_window, image=image_tk, background="white")
            image_label.grid(row=0, column=0, padx=60, pady=30)

            text = "AREA\nLIBERA"
            text_label = tk.Label(root_window, text=text, font=("Roboto", 40, 'bold'), justify='center', foreground='#05A002', background='white')
            text_label.grid(row=0, column=1, padx=60, pady=30)
        else:
            image_path = './icons/red_icon.png'
            
            image_pil = Image.open(image_path)
            image = image_pil.resize((308,308))
            image_tk  = ImageTk.PhotoImage(image)
            image_label = tk.Label(root_window, image=image_tk, background="white")
            image_label.grid(row=0, column=0, padx=30, pady=30)

            text = f"PERICOLO!\nOperatori\nnelle vicinanze"
            text_label = tk.Label(root_window, text=text, font=("Roboto", 40, 'bold'), justify='center', foreground='#FF1C1C', background='white')
            text_label.grid(row=0, column=1, padx=30, pady=30)

        root_window.update()

    
    def update_general_alarms(alarm_text, priority):
        global image_tk
        global root_window

        if image_tk is not None:
            for widget in root_window.winfo_children():
                widget.destroy()
        
        if priority == "communication":

            image_path= "./icons/info_icon.png"
            image_pil = Image.open(image_path)
            image = image_pil.resize((150,150))
            image_tk  = ImageTk.PhotoImage(image)
            image_label = tk.Label(root_window, image=image_tk, background="white")
            image_label.grid(row=0, column=1, padx=10, pady=50)
            
            text =  "COMUNICAZIONE\nGENERALE"
            text_label = tk.Label(root_window, text=text, font=("Roboto", 40, 'bold'), justify='center', foreground='#003399', background='white')
            text_label.grid(row=0, column=2, padx=10, pady=50)

            image_label_2 = tk.Label(root_window, image=image_tk, background="white")
            image_label_2.grid(row=0, column=3, padx=10, pady=50)

            text_label = tk.Label(root_window, text=alarm_text, font=("Roboto", 35, 'bold'), justify='center', foreground='#0E294B', background='white')
            text_label.grid(row=1, columnspan=3, pady=40, padx=80, sticky='nsew')

        else:
            image_path= "./icons/general_alarm_icon.png"
            image_pil = Image.open(image_path)
            image = image_pil.resize((150,150))
            image_tk  = ImageTk.PhotoImage(image)
            image_label = tk.Label(root_window, image=image_tk, background="white")
            image_label.grid(row=0, column=1, padx=40, pady=50)
            
            text =  "ALLARME\nGENERALE"
            text_label = tk.Label(root_window, text=text, font=("Roboto", 40, 'bold'), justify='center', foreground='#FF1C1C', background='white')
            text_label.grid(row=0, column=2, padx=40, pady=50)

            image_label_2 = tk.Label(root_window, image=image_tk, background="white")
            image_label_2.grid(row=0, column=3, padx=40, pady=50)

            text_label = tk.Label(root_window, text=alarm_text, font=("Roboto", 35, 'bold'), justify='center', foreground='#B50404', background='white')
            text_label.grid(row=1, column= 1, columnspan=3, pady=40, padx=80, sticky='ew')
        
        root_window.update()
        

    





    