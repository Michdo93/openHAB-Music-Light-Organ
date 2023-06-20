# openHAB-Music-Light-Organ
A light organ for openHAB that accesses a playuri item of a Sonos speaker and adjusts colour lamps (e.g. from Philips Hue) accordingly.

# Preparation

You have to install following libraries via pip:

```
python3 -m pip install python-openhab-crud
python3 -m pip install librosa
python3 -m pip install requests
python3 -m pip install soundfile
python3 -m pip install numpy
```

# Installation

Then you have to download the python file and make it executable:

```
wget https://raw.githubusercontent.com/Michdo93/openHAB-Music-Light-Organ/main/music_light_organ.py
sudo chmod +x music_light_organ.py
```

# Customisations

You have to change following for accesing your openHAB instance via the REST API:

```
crud = CRUD("http://<ip>:8080", "<username>", "<password>")
```

Please replace `<ip>`, `<username>`, `<password>` with the ip address, username and password of your openHAB instance.

For retrieving the `playuri` stream you have to change following:

```
sonos_playuri_item = "iKonferenz_Sonos_Playbar_URIspielen"
```

Please replace `iKonferenz_Sonos_Playbar_URIspielen` with the name of your `playuri` item.

And at least you have to change following to control your lamps:

```
lamps_switch_items = ["iKueche_Hue_Lampe1_Schalter", "iKueche_Hue_Lampe2_Schalter", "iKueche_Hue_Lampe3_Schalter", "iKueche_Hue_Lampe4_Schalter", ...]
lamps_color_items = ["iKueche_Hue_Lampe1_Farbe", "iKueche_Hue_Lampe2_Farbe", "iKueche_Hue_Lampe3_Farbe", "iKueche_Hue_Lampe4_Farbe", ...]
```

Please note that you have to specify as many items for switching the colour lamps on/off as items for changing the colour values of a lamp. For the `Switch` items you have to edit `lamps_switch_items` and for the `Color` items you have to replace `lamps_color_items`. You also have to make sure that the assignment is correct and that both are given in the same order so that both items can be used correctly for a colour lamp.
