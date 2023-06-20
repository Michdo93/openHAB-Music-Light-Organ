import io
import librosa
import requests
import soundfile as sf
import numpy as np
import time
import threading
from openhab import CRUD

class LampAnalyzer(threading.Thread):
    def __init__(self, lamp_switch_item, lamp_color_item, sonos_playuri_item, crud):
        super().__init__()
        self.lamp_switch_item = lamp_switch_item
        self.lamp_color_item = lamp_color_item
        self.sonos_playuri_item = sonos_playuri_item
        self.crud = crud
        self._stop_event = threading.Event()

        self.crud.sendCommand(lamp_switch_item, "ON")

        self.music_light_organ = MusicLightOrgan(self.crud)

    def run(self):
        while not self.stopped():
            audio_data = self.get_audio_data()
            audio_np, sample_rate = self.process_audio_data(audio_data)
            self.analyze_audio(audio_np, sample_rate)
            time.sleep(0.001)

        self.close()

    def get_audio_data(self):
        sonos_uri = self.crud.getState(self.sonos_playuri_item)
        #print(sonos_uri)

        response = requests.get(sonos_uri, stream=True)

        if response.status_code == 200:
            audio_stream = response.iter_content(chunk_size=1024)

            audio_data = b""
            for chunk in audio_stream:
                audio_data += chunk

                if len(audio_data) >= 44100 * 2:
                    break

        else:
            print("Error retrieving the Sonos audio stream.")
            audio_data = b""

        return audio_data

    def process_audio_data(self, audio_data):
        audio_np, sample_rate = sf.read(io.BytesIO(audio_data))
        if len(audio_np.shape) > 1:
            audio_np = audio_np[:, 0]

        return audio_np, sample_rate

    def analyze_audio(self, audio_data, sample_rate):
        self.music_light_organ.analyze_audio(audio_data, sample_rate, self.lamp_color_item)

    def close(self):
        self.crud.sendCommand(self.lamp_switch_item, "OFF")
        print(f"Thread for lamp {self.lamp_color_item} closed.")

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class MusicLightOrgan:
    def __init__(self, crud):
        self.crud = crud
        self.hue_colors = [
            "0, 100, 100",  # red
            "120, 100, 100",  # green
            "240, 100, 100",  # blue
            "60, 100, 100",  # yellow
            "300, 100, 100",  # turqouise
            "120, 100, 100"   # cyan
        ]

    def analyze_audio(self, audio_data, sample_rate, lamp_color_item):
        rms = librosa.feature.rms(y=audio_data)[0]

        threshold = 0.1

        rms_mean = np.mean(rms)

        if rms_mean > threshold:
            color = self.hue_colors[np.random.randint(len(self.hue_colors))]
            #print(f"Lampe {lamp_color_item}: {color}")
            self.crud.sendCommand(lamp_color_item, color)
        else:
            #print(f"Lampe {lamp_color_item}: 0, 0, 100")
            self.crud.sendCommand(lamp_color_item, "0, 0, 100")

if __name__ == '__main__':
    crud = CRUD("http://<ip>:8080", "<username>", "<password>")
    sonos_playuri_item = "iKonferenz_Sonos_Playbar_URIspielen"
    lamps_switch_items = ["iKueche_Hue_Lampe1_Schalter", "iKueche_Hue_Lampe2_Schalter", "iKueche_Hue_Lampe3_Schalter", "iKueche_Hue_Lampe4_Schalter", "iBad_Hue_Lampe1_Schalter", "iBad_Hue_Lampe2_Schalter", "iBad_Hue_Lampe3_Schalter", "iBad_Hue_Lampe4_Schalter", "iBad_Hue_Lampe5_Schalter", "iBad_Hue_Lampe6_Schalter", "iIoT_Hue_Lampe1_Schalter", "iIoT_Hue_Lampe2_Schalter", "iIoT_Hue_Lampe3_Schalter", "iIoT_Hue_Lampe4_Schalter", "iIoT_Hue_Lampe5_Schalter", "iIoT_Hue_Lampe6_Schalter", "iMultimedia_Hue_Lampe1_Schalter", "iMultimedia_Hue_Lampe2_Schalter", "iMultimedia_Hue_Lampe3_Schalter", "iMultimedia_Hue_Lampe4_Schalter", "iMultimedia_Hue_Lampe5_Schalter", "iMultimedia_Hue_Lampe6_Schalter"]
    lamps_color_items = ["iKueche_Hue_Lampe1_Farbe", "iKueche_Hue_Lampe2_Farbe", "iKueche_Hue_Lampe3_Farbe", "iKueche_Hue_Lampe4_Farbe", "iBad_Hue_Lampe1_Farbe", "iBad_Hue_Lampe2_Farbe", "iBad_Hue_Lampe3_Farbe", "iBad_Hue_Lampe4_Farbe", "iBad_Hue_Lampe5_Farbe", "iBad_Hue_Lampe6_Farbe", "iIoT_Hue_Lampe1_Farbe", "iIoT_Hue_Lampe2_Farbe", "iIoT_Hue_Lampe3_Farbe", "iIoT_Hue_Lampe4_Farbe", "iIoT_Hue_Lampe5_Farbe", "iIoT_Hue_Lampe6_Farbe", "iMultimedia_Hue_Lampe1_Farbe", "iMultimedia_Hue_Lampe2_Farbe", "iMultimedia_Hue_Lampe3_Farbe", "iMultimedia_Hue_Lampe4_Farbe", "iMultimedia_Hue_Lampe5_Farbe", "iMultimedia_Hue_Lampe6_Farbe"]

    if len(lamps_switch_items) != len(lamps_color_items):
        raise ValueError("You need as many switches as colour items.")

    threads = []
    try:
        for lamp_switch_item, lamp_color_item in zip(lamps_switch_items, lamps_color_items):
            thread = LampAnalyzer(lamp_switch_item, lamp_color_item, sonos_playuri_item, crud)
            thread.start()
            threads.append(thread)

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Programme is being terminated. Wait for the threads to finish...")

        for thread in threads:
            thread.stop()
            thread.join()

        print("Programme successfully completed.")
