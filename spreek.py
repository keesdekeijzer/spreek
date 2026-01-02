#!/usr/bin/env python3

import wave
from piper import PiperVoice
from piper import SynthesisConfig
import re
import os
import subprocess
import datetime
import shutil
import operator

# sudo apt-get install python3-tk
import tkinter as tk  
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText

# versie: 2026-01-01 11:27

"""
# versie: 2026-01-02 13:35
De beschikbare stemmen ophalen door recursief de 'voices' directory te doorlopen
De pop-up verwijderd die je kreeg na het kiezen van een stem
Pack layout omgezet naar Grid layout
GUI geschikt gemaakt voor het instellen van SynthesisConfig
SynthesisConfig instellingen laten meenemen bij de uitvoering
"""

# (ffmpeg moet ook geinstalleerd zijn)
# In de directory waar dit script staat worden ook verwacht:
# 1. een directory 'invoer' waar de te spreken teksten in moeten staan
# 2. een directory 'voices' waar de stemmen in moeten staan
# de uitvoer-directory met de mp3's komt ook in de directory waar dit script staat
# de naam van de directory waarin de stem staat wordt toegevoegd aan het einde van de namen van de mp3-bestanden

# waarden instellen
now = datetime.datetime.now()
nu = now.strftime("%Y-%m-%d-%H-%M")

dirnaam = 'invoer'
uitvoermap = 'uitvoer-' + nu # bestanden mogen niet al bestaan
os.mkdir(uitvoermap)


def vrij(): # schijfruimte opvragen
    # opslag gebruik opvragen
    total, used, free = shutil.disk_usage("/home")
    f_free = "{:.2f} GiB".format(free // (2**30))
    perc = str(int(free / total * 100))
    beschikbaar = f'Opslag: {perc} % vrij ({f_free})'
    return beschikbaar

def verwijder_bestand(file_path):
    try:
        os.remove(file_path)
        voeg_tekst_toe(f"Bestand '{file_path}' verwijderd.")
    except FileNotFoundError:
        print(f"Bestand '{file_path}' niet gevonden.")
    except PermissionError:
        print(f"Geen toestemming om bestand '{file_path}' te verwijderen.")
    except Exception as e:
        print(f"Fout opgetreden bij het verwijderen van het bestand: {e}")

def bestandsnaam_opschonen(naam):
    naam = naam.replace('(','_')
    naam = naam.replace(')','_')
    naam = naam.replace(' ','_')
    return naam

def maak_mp3(uitvoer):
    uitvoer_mp3 = uitvoer[:-4] + ".mp3"
    command = f"(ffmpeg -i {uitvoer} -vn -ar 44100 -ac 2 -b:a 192k {uitvoer_mp3})"
    process_1 = subprocess.run(command, shell=True, capture_output=True, text=True)
    return uitvoer_mp3


def leesvoor(tekstbestand):
    # tekstbestand is een tuple
    # uitvoermap nodig
    # stem nodig
    # stemnaam nodig
    
    toevoeging = f' - {stemnaam}'
    
    uitvoer = f"{uitvoermap}/{tekstbestand[1]}{toevoeging}.wav"
    uitvoer = bestandsnaam_opschonen(uitvoer)
    tekst = ""
    with open(tekstbestand[0]) as bestand:
        for regel in bestand:
            tekst = tekst + regel
    voice = PiperVoice.load(stem)
    
    syn_config = SynthesisConfig(
    volume=float(volume.get()),       # Volume multiplier
    length_scale=float(vertraging.get()),  # Speaking speed (higher = slower)
    noise_scale=float(audio_variatie.get()),   # Audio variation 
    noise_w_scale=float(spreek_variatie.get()),   # Speaking variation
    normalize_audio=bool(normalisatie.get()) # Automatic volume normalization
)
    with wave.open(uitvoer, "wb") as wav_file:
        voice.synthesize_wav(tekst, 
        wav_file,
        syn_config=syn_config)

    voeg_tekst_toe(f'Klaar met: {uitvoer}')
    uitvoer_mp3 = maak_mp3(uitvoer)
    voeg_tekst_toe(f'Aangemaakt: {uitvoer_mp3}')
    verwijder_bestand(uitvoer)
    root.update() # GUI bijwerken

def start_knop():
    if 'stem' in globals():
        button.state(['disabled'])
        hoofdprogramma()
        eerste_keer = False
        text.see(tk.END)
    else:
        showinfo(
        title='Foutje!',
        message=f'Kies eerst een stem!'
        )

def voeg_tekst_toe(nieuwe_tekst):
    nieuwe_tekst = '\n' + nieuwe_tekst
    text['state'] = 'normal'
    text.insert(tk.END, nieuwe_tekst)
    text['state'] = 'disabled'
    text.see(tk.END)
    root.update() # GUI bijwerken

# hoofdprogramma
def hoofdprogramma():
    bestanden = haal_bestanden(dirnaam) # lijst met tuples
    text_var.set(vrij())
    voeg_tekst_toe('Gestart met het spreken van de teksten.')
    for nummer, item in enumerate(bestanden):
        # tellen start bj 0, daarom 1 erbij
        nummer_str = str(nummer + 1)
        aantal_bestanden = str(len(bestanden))
        bezig_met = f'Bezig met {nummer_str} van {aantal_bestanden} : {item[0]}'
        label2['text'] = bezig_met
        root.update()
        leesvoor(item)
        text_var.set(vrij())
        root.update()
    voeg_tekst_toe('\nKLAAR!')

def haal_bestanden(dirnaam):
    bestandenlijst = os.listdir(dirnaam)

    metpaden = map(lambda naam: os.path.join(dirnaam, naam), bestandenlijst)
    bestanden = []
    for item in metpaden:
        if os.path.isfile(item):
            naambestand = os.path.basename(item)[:-4]
            tekst_item = (item, naambestand) # tuple
            bestanden.append(tekst_item)
    bestanden.sort()
    return bestanden

def stem_gekozen(event):
    """ zet de gekozen stem """
    global stem
    global stemnaam
    stem = stem_var.get()
    lijst = stem.split('/')
    stemnaam = lijst[-2] # naam van de directory waar het .onnx in staat
    # 'stemnaam' wordt aan de naam van de mp3 toegevoegd

# stemmen ophalen als tuple
def haal_stemmen_op():
    # lees directory voices uit
    bestanden = []
    haal_stem_bestanden('voices', bestanden)
    bestanden.sort()
    return bestanden
    
def haal_stem_bestanden(dirnaam, bestanden): 
    # .onnx bestanden, recursieve functie
    bestandenlijst = os.listdir(dirnaam)

    metpaden = map(lambda naam: os.path.join(dirnaam, naam), bestandenlijst)
            
    for item in metpaden:
        if os.path.isfile(item):
            naambestand = os.path.basename(item)
            if naambestand.endswith('.onnx'):
                tekst_item = (item, naambestand) # tuple
                bestanden.append(tekst_item)
        else:
            haal_stem_bestanden(item, bestanden)


# einde functies


# GUI
root = tk.Tk()
root.title('Spreek - Tekst omzetten naar spraak')

# Venster centreren
window_width = 1000
window_height = 600

# scherm afmetingen
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# middelpunt
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)

# centreren
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

# icon
try:
    # Linux en macOS
    photo = tk.PhotoImage(file='./tts.png') #.png or .gif
    root.iconphoto(False, photo)
except tk.TclError:
    print("icon file not found.")


# grid 12x2
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=1)
root.rowconfigure(6, weight=1)
root.rowconfigure(7, weight=1)
root.rowconfigure(8, weight=1)
root.rowconfigure(9, weight=1)
root.rowconfigure(10, weight=5)
root.rowconfigure(11, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)


stembestanden = haal_stemmen_op()

# verwijder de tweede waarde van elke tuple en geef een lijst met alleen de eerste waarden van de tuples, zet de lijst om naar een tuple
stemmen_tuple = tuple(list(map(operator.itemgetter(0), stembestanden))) 

# stem keuze

label1titel = ttk.Label(root, text='Stem', font=("Helvetica", 10), anchor=tk.CENTER)
label1titel.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5)

stem_var = tk.StringVar()
combobox = ttk.Combobox(root, textvariable=stem_var)
combobox['values'] = stemmen_tuple
combobox['state'] = 'readonly'
combobox.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)
combobox.bind('<<ComboboxSelected>>', stem_gekozen)

# vrije ruimte
text_var = tk.StringVar()
text_var.set(vrij())

label2titel = ttk.Label(root, text='Vrije ruimte', font=("Helvetica", 10), anchor=tk.CENTER)
label2titel.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

label1 = ttk.Label(root, text=text_var.get(), font=("Helvetica", 14), anchor=tk.CENTER)
label1.grid(column=1, row=3, sticky=tk.EW, padx=5, pady=5)

# nu bezig met bestand ...

label3titel = ttk.Label(root, text='Bezig met:', font=("Helvetica", 10), anchor=tk.CENTER)
label3titel.grid(column=1, row=4, sticky=tk.EW, padx=5, pady=5)

label2 = ttk.Label(root, text='', font=("Helvetica", 14), anchor=tk.CENTER)
label2.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

# naam uitvoermap tonen

label4titel = ttk.Label(root, text='Uitvoer directory', font=("Helvetica", 10), anchor=tk.CENTER)
label4titel.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)

label3 = ttk.Label(root, text=uitvoermap,font=("Helvetica", 14), anchor=tk.CENTER)
label3.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)

# startknop

label5titel = ttk.Label(root, text='Start knop', font=("Helvetica", 10), anchor=tk.CENTER)
label5titel.grid(column=1, row=8, sticky=tk.EW, padx=5, pady=5)

button = ttk.Button(root, text='Start', command=start_knop)
button.grid(column=1, row=9, sticky=tk.EW, padx=5, pady=5)

# frame
frame = ttk.Frame(root)
frame.grid(column=0, row=10, sticky=tk.EW, padx=5, pady=5, columnspan=2)

# tekst uitvoer gedeelte
text = ScrolledText(frame, height=8)
text.pack(padx=10, pady=10, expand=True,fill=tk.BOTH)

text.config(
    font=("Consolas", 12), 
    fg="#F0F0F0", 
    bg="#282C34", 
    insertbackground="white"
)

text['state'] = 'normal'

# exit knop
exit_button = ttk.Button(root, text='Exit', command=lambda: root.quit())
exit_button.grid(column=1, row=11, sticky=tk.EW, padx=5, pady=5)

# stemvariabelen instellen

schaal = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0)

# label Volume
label10titel = ttk.Label(root, text='Volume', font=("Helvetica", 10), anchor=tk.CENTER)
label10titel.grid(column=0, row=0, sticky=tk.EW, padx=5, pady=5)

volume = tk.StringVar(value=1.0)
volume_spin_box = ttk.Spinbox(
    root,
    from_=0.0,
    to=2.0,
    values=schaal,
    textvariable=volume,
    wrap=True)

volume_spin_box.grid(column=0, row=1, sticky=tk.NS, padx=5, pady=5)

# label Vertraging
label12titel = ttk.Label(root, text='Vertraging', font=("Helvetica", 10), anchor=tk.CENTER)
label12titel.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)

vertraging = tk.StringVar(value=1.0)
vertraging_spin_box = ttk.Spinbox(
    root,
    from_=0.0,
    to=2.0,
    values=schaal,
    textvariable=vertraging,
    wrap=True)

vertraging_spin_box.grid(column=0, row=3, sticky=tk.NS, padx=5, pady=5)

# label Audio variatie
label14titel = ttk.Label(root, text='Audio variatie', font=("Helvetica", 10), anchor=tk.CENTER)
label14titel.grid(column=0, row=4, sticky=tk.EW, padx=5, pady=5)

audio_variatie = tk.StringVar(value=0.7)
audio_variatie_spin_box = ttk.Spinbox(
    root,
    from_=0.0,
    to=2.0,
    values=schaal,
    textvariable=audio_variatie,
    wrap=True)

audio_variatie_spin_box.grid(column=0, row=5, sticky=tk.NS, padx=5, pady=5)

# label Spreek variatie
label16titel = ttk.Label(root, text='Spreek variatie', font=("Helvetica", 10), anchor=tk.CENTER)
label16titel.grid(column=0, row=6, sticky=tk.EW, padx=5, pady=5)

spreek_variatie = tk.StringVar(value=0.9)
spreek_variatie_spin_box = ttk.Spinbox(
    root,
    from_=0.0,
    to=2.0,
    values=schaal,
    textvariable=spreek_variatie,
    wrap=True)

spreek_variatie_spin_box.grid(column=0, row=7, sticky=tk.NS, padx=5, pady=5)

# label Normalisatie
label18titel = ttk.Label(root, text='Normalisatie', font=("Helvetica", 10), anchor=tk.CENTER)
label18titel.grid(column=0, row=8, sticky=tk.EW, padx=5, pady=5)

normalisatie = tk.BooleanVar(value=True)

checkbox = ttk.Checkbutton(
    root,
    text='Normaliseren',
    variable=normalisatie
)

checkbox.grid(column=0, row=9, sticky=tk.NS, padx=5, pady=5)


# start GUI
root.mainloop()
