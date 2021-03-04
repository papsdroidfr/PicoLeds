# PicoLeds
Contrôle d'un anneau de 16 leds Neopixels RGB à l'aide d'un micro-contrôleur Raspberry [PICO](https://www.papsdroid.fr/post/hello-pico).
Ce prototype permet de commander les ambiances lumineuses à l'aide d'un bouton poussoir dans le but de fabriquer une petite lampe de chevet aux ambiances sympas.
![Prototype](_docs/IMG_20210304_190720_web.jpg)


## prototype

### matériel nécessaire
* 1 Raspberry PICO 
* 2 barettes de pin header 20 broches 2,54mm (unutie si le PICO est echeté avec les barettes soudées)
* 1 anneau de 16 leds Neopixel d'Adafruit, sur lequel il faut souder 3 pin headers sur +VCC, SIGNAL et GND.
* 1 petit bouton poussoir 6mm
* 1 condensateur polarisé 100nf
* 2 resistances 10k ohms.
* 1 breadbord et des câbles dupont mâles/mâle souples.

### fritzing
Le prototype sur breadboard est simple à réaliser. Il faut souder les pin header 20 broches sur le PICO (ou acheter un PICO avec les pin header déjà soudés). 
J'ai aussi soudé 3 pin sur le ring Neopixel des 16 leds sur le +VCC, SIGNAL et GND afin de pouvoir le positionner sur la breadboard. 
Le bouton poussoir est monté en pull-up avec le jeux de 2 résistances 10k ohms.
Aucun filtrage "RC" n'est nécessaire avec le bouton poussoir car les faux-rebonds electro-mécaniques générés lors des appuis seront filtrés de manière logicielle.
![fritzing](_docs/picoLeds_fritzing_web.png)

## script MicroPython
Avant d'installer le scipt micoPython qui gère l'anneau Neopixel il faut d'abord configurer le Raspberry PICO en suivant [ce guide](https://www.papsdroid.fr/post/hello-pico).
Le script **picoLeds.py** dans le dossier /microPython est conçu à partir de l'exemple fourni par Raspberry concernant le [SDK microPython](https://datasheets.raspberrypi.org/pico/raspberry-pi-pico-python-sdk.pdf) sur le contrôle Neopixel.
Le bouton poussoir poussoir quand à lui est associé à une fonction callback appelée par interruption losque le Pin relié au bouton se retrouve à la masse (montage pull-up).
Pour éviter les faux rebonds electro-mécaniques, la fonction callback commence par attendre un certain temps de stabilisation (50ms suffisent), 
puis elle contrôle que le bouton poussoir est toujours appuyé après ce laps de temps. 
Dans ce cas, on peut alors coder ce que doit exécuter cette fonction callback en étant sûr d'avoir évité tous les faux-rebonds.

Ce script commence par animer les leds avec un effet arc-en ciel, puis les éteint toutes.
Chaque appui sur le bouton poussoir va provoquer un effet de "fade out" dans une couleur qui change lors de chaque appui.


## Prochaine étape 
création d'un circuit-imprimé et intégration dans une petite lampe de chevet.





