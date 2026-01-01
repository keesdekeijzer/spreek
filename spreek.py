#!/usr/bin/env python3

import wave
from piper import PiperVoice
from piper import SynthesisConfig
import re
import os
import subprocess
import datetime
import shutil

# sudo apt-get install python3-tk
import tkinter as tk  
from tkinter import ttk
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText

# versie: 2026-01-01 11:27


# (ffmpeg moet ook geinstalleerd zijn)
# In de directory waar dit script staat worden ook verwacht:
# 1. een directory 'invoer' waar de te spreken teksten in moeten staan
# 2. een directory 'voices' waar de stemmen in moeten staan
# de uitvoer-directory met de mp3's komt ook in de directory waar dit script staat

# waarden instellen
now = datetime.datetime.now()
nu = now.strftime("%Y-%m-%d-%H-%M")

#stem = "voice/nl_BE-nathalie-medium.onnx"
#stemnaam = 'nathalie'
dirnaam = 'invoer'
uitvoermap = 'uitvoer-' + nu # bestanden mogen niet al bestaan
# toevoeging = ' - nathalie'
os.mkdir(uitvoermap)

"""
num_symbols=config["num_symbols"],
num_speakers=config["num_speakers"],
sample_rate=config["audio"]["sample_rate"],
noise_scale=inference.get("noise_scale", 0.667),
length_scale=inference.get("length_scale", 1.0),
noise_w=inference.get("noise_w", 0.8),
"""

syn_config = SynthesisConfig(
    volume=1.0,          # Volume multiplier 0.5?
    length_scale=1.0,    # Speaking speed (higher = slower)
    noise_scale=0.7,     # Audio variation 0.667
    noise_w_scale=0.9,   # Speaking variation 0.8
    normalize_audio=True # Automatic volume normalization
)

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
    stemnaam = lijst[-2]
    showinfo(
        title='Result',
        message=f'Je hebt {stemnaam} gekozen als stem!'
    )


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

# stem keuze
stem_var = tk.StringVar()
combobox = ttk.Combobox(root, textvariable=stem_var)
combobox['values'] = (
'voices/nl/nathalie/nl_BE-nathalie-medium.onnx', 
'voices/nl/mls/nl_NL-mls-medium.onnx', 
'voices/de/mls/de_DE-mls-medium.onnx',
'voices/en/alba/en_GB-alba-medium.onnx',
'voices/en/aru/en_GB-aru-medium.onnx',
'voices/en/cori/en_GB-cori-high.onnx',
'voices/en/jenny/en_GB-jenny_dioco-medium.onnx',
'voices/en/semaine/en_GB-semaine-medium.onnx',
'voices/en/vctk/en_GB-vctk-medium.onnx')
combobox['state'] = 'readonly'
combobox.pack(padx=250, pady=10, expand=True,fill=tk.BOTH)
combobox.bind('<<ComboboxSelected>>', stem_gekozen)

# vrije ruimte
text_var = tk.StringVar()
text_var.set(vrij())

label1 = ttk.Label(root, text=text_var.get(), font=("Helvetica", 14), anchor=tk.CENTER)
label1.pack(padx=10, pady=10, expand=True,fill=tk.BOTH)

# nu bezig met bestand ...
label2 = ttk.Label(root, text='', font=("Helvetica", 14), anchor=tk.CENTER)
label2.pack(padx=10, pady=10, expand=True,fill=tk.BOTH)

# naam uitvoermap tonen
label3 = ttk.Label(root, text=uitvoermap,font=("Helvetica", 14), anchor=tk.CENTER)
label3.pack(padx=10, pady=10, expand=True,fill=tk.BOTH)

# startknop
button = ttk.Button(root, text='Start', command=start_knop)
button.pack()

# frame
frame = ttk.Frame(root)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
exit_button.pack(ipadx=5, ipady=5, expand=True)

# start GUI
root.mainloop()
