# Spreek

Spreek is een hulpprogramma voor Piper. Het geeft een GUI waar je een stem kunt selecteren en de voortgang van de omzetting van tekstbestanden naar mp3's kunt volgen.

Het is getest op Linux (Debian 13, Gnome).

Het is gemaakt met Python en Tkinter. Je hebt, naast Piper, ook ffmpeg nodig voor de omzetting van .wav bestanden naar mp3's.

Het programa leest tekstbestanden uit de directory 'invoer' en zet die via Piper om naar .wav bestanden, die dan met ffmpeg omgezet worden naar mp3's. vervolgens worden de .wav bedtanden weer verwijderd om schijfruimte te sparen.

## Stemmen
De stemmen (.onnx met bijbehorende .json bestanden) worden verwacht in (sub)directories in de directory 'voices'.
[stemmen voor Piper](https://github.com/t-meinhardt/piper-master/blob/master/VOICES.md)

## Uitvoer
Voor de uitvoer maakt het programma een directory aan waarvan de naam begint met 'uitvoer', gevolgd door de datum en de tijd vaade start van het programma.

## Locatie scripts
Het shell script 'start_server.sh' gaat er vanuit dat de locatie voor dit script deze is: '~/Projecten/Piper'.

## Piper documentatie
[Piper documentatie](https://tderflinger.github.io/piper-docs/guides/usage/)

