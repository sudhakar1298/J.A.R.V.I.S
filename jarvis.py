import pyaudio
import numpy as np
import subprocess
import time
import sys
import os
from collections import deque
import struct
import signal

try:
    import pvporcupine
except ImportError:
    print("Porcupine not installed!")
    print("Install it with: pip install pvporcupine")
    sys.exit(1)

PORCUPINE_ACCESS_KEY = "FvWMDPVZ48U3HQeBc9LjWP3jEZG7uqDFJL4qjwrtxWXoedhKCWactA=="


class UnifiedLauncher:

    def __init__(self, wake_word="jarvis", clap_threshold=1800, debug=False):
        self.wake_word = wake_word.lower()
        self.clap_threshold = clap_threshold
        self.debug = debug

        self.is_active = False
        self.activation_time = 0
        self.active_duration = 5
        self.running = True

        self.waiting_for_triple = False
        self.triple_wait_time = 0
        self.triple_wait_duration = 30

        self.clap_times = []
        self.last_clap_time = 0
        self.clap_interval = 0.7
        self.previous_amplitude = 0
        self.amplitude_history = deque(maxlen=10)

        builtin_keywords = pvporcupine.KEYWORDS
        if self.wake_word not in builtin_keywords:
            print(f"Wake word '{self.wake_word}' not available, using 'jarvis'")
            self.wake_word = "jarvis"

        try:
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=[self.wake_word]
            )
            print(f"Wake word '{self.wake_word}' loaded")
        except Exception as e:
            print(f"Error initializing Porcupine: {e}")
            sys.exit(1)

        self.sample_rate = self.porcupine.sample_rate
        self.frame_length = self.porcupine.frame_length

        self.pa = pyaudio.PyAudio()
        self.audio_stream = None

        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, sig, frame):
        print("Shutting down...")
        self.running = False

    def start_audio_stream(self):
        try:
            self.audio_stream = self.pa.open(
                rate=self.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.frame_length
            )
            print("Listening for wake word...")
        except Exception as e:
            print(f"Error opening audio stream: {e}")
            sys.exit(1)

    def detect_wake_word(self, pcm):
        try:
            return self.porcupine.process(pcm) >= 0
        except:
            return False

    def detect_clap(self, pcm):
        try:
            audio_data = np.array(pcm, dtype=np.int16)
            amplitude = np.abs(audio_data).max()

            self.amplitude_history.append(amplitude)
            current_time = time.time()

            amplitude_jump = amplitude - self.previous_amplitude
            sharp_attack = amplitude_jump > (self.clap_threshold * 0.4)
            loud_enough = amplitude > self.clap_threshold

            if len(self.amplitude_history) >= 3:
                avg_recent = sum(self.amplitude_history) / len(self.amplitude_history)
                not_sustained = avg_recent < (self.clap_threshold * 0.5)
            else:
                not_sustained = True

            is_clap = loud_enough and (sharp_attack or not_sustained)

            if is_clap and current_time - self.last_clap_time > 0.1:
                self.clap_times.append(current_time)
                self.last_clap_time = current_time

                self.clap_times = [t for t in self.clap_times if current_time - t < self.clap_interval * 2.5]

                if len(self.clap_times) >= 3:
                    if self.clap_times[-1] - self.clap_times[-3] < self.clap_interval * 2.5:
                        self.clap_times.clear()
                        return 3

                if not self.waiting_for_triple and len(self.clap_times) >= 2:
                    if self.clap_times[-1] - self.clap_times[-2] < self.clap_interval:
                        self.clap_times.clear()
                        return 2

            self.previous_amplitude = amplitude

            if self.clap_times and current_time - self.clap_times[-1] > self.clap_interval * 2:
                self.clap_times.clear()

            return 0
        except:
            return 0

    def activate(self):
        self.is_active = True
        self.activation_time = time.time()
        print("Wake word detected. Listening for claps...")

    def deactivate(self):
        self.is_active = False
        print("Timeout. Say wake word again.")

    def enter_triple_wait_mode(self):
        self.waiting_for_triple = True
        self.triple_wait_time = time.time()
        print("Waiting for triple clap (30s window)")

    def is_triple_wait_active(self):
        if not self.waiting_for_triple:
            return False
        if time.time() - self.triple_wait_time > self.triple_wait_duration:
            self.waiting_for_triple = False
            return False
        return True

    def is_still_active(self):
        if not self.is_active:
            return False
        if time.time() - self.activation_time > self.active_duration:
            self.deactivate()
            return False
        return True

    def launch_all_apps(self):
        print("Double clap detected. Launching apps...")

        tbt_path = r"D:\Trials\chunking"
        subprocess.Popen(["code", tbt_path], shell=True)

        subprocess.Popen(["cmd", "/c", "start", "chrome", "https://chatgpt.com/"])
        

    def play_youtube_video(self):
        print("Triple clap detected. Opening YouTube...")
        youtube_url = "https://www.youtube.com"
        subprocess.Popen(["cmd", "/c", "start", "chrome", youtube_url], shell=True)


    def run(self):
        self.start_audio_stream()

        try:
            while self.running:
                pcm_bytes = self.audio_stream.read(self.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.frame_length, pcm_bytes)

                if not self.is_active and not self.waiting_for_triple:
                    if self.detect_wake_word(pcm):
                        self.activate()

                elif self.is_still_active():
                    clap_type = self.detect_clap(pcm)

                    if clap_type == 2:
                        self.launch_all_apps()
                        self.deactivate()
                        self.enter_triple_wait_mode()

                    elif clap_type == 3:
                        self.play_youtube_video()
                        self.deactivate()

                elif self.is_triple_wait_active():
                    if self.detect_clap(pcm) == 3:
                        self.play_youtube_video()
                        self.waiting_for_triple = False

        finally:
            self.cleanup()

    def cleanup(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
        if self.pa:
            self.pa.terminate()
        if self.porcupine:
            self.porcupine.delete()


def main():
    launcher = UnifiedLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
