## How It Works

The script operates in a multi-stage listening process:

1.  **Wake Word Detection:** The script continuously listens for the wake word "Jarvis".
2.  **Activation Window:** Upon detecting the wake word, it enters a 5-second "active" mode, indicated by a console message.
3.  **Clap Command Recognition:**
    *   **Double Clap:** If a double clap is detected within the 5-second window, it launches a predefined set of applications (VS Code and Chrome with ChatGPT). After this, it enters a special 30-second window to listen for a triple clap.
    *   **Triple Clap:** If a triple clap is detected (either in the initial 5-second window or the subsequent 30-second window), it opens YouTube in Chrome.
4.  **Timeout:** If no clap command is detected within the active window, the script returns to listening for the wake word.

## Features

*   **Wake Word Activation:** Hands-free activation using the "Jarvis" wake word.
*   **Clap Gesture Control:** Differentiates between double and triple claps to trigger distinct actions.
*   **Low Resource Usage:** Utilizes the efficient Picovoice Porcupine engine for on-device wake word detection.
*   **Customizable Actions:** Easily modify the Python script to change which applications are launched or what actions are performed.

## Prerequisites

*   Python 3.x
*   A microphone connected to your system.
*   A Picovoice Porcupine Access Key. You can get one for free from the [Picovoice Console](https://console.picovoice.ai/).

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/sudhakar1298/J.A.R.V.I.S.git
    cd J.A.R.V.I.S
    ```

2.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```
    *Note: `pyaudio` may require additional system dependencies (e.g., `portaudio`). Please refer to the `pyaudio` documentation for installation help on your OS.*

3.  **Configure the Access Key:**
    Open `jarvis.py` in a text editor and replace the placeholder value for `PORCUPINE_ACCESS_KEY` with your own key from the Picovoice Console.
    ```python
    # jarvis.py
    PORCUPINE_ACCESS_KEY = "YOUR_ACCESS_KEY_HERE"
    ```

4.  **Customize Application Paths (Optional):**
    The default script is configured to launch applications with specific paths and URLs. You can edit the `launch_all_apps` and `play_youtube_video` methods in `jarvis.py` to match your own needs and file system paths.
    ```python
    # Example from launch_all_apps method
    tbt_path = r"D:\Trials\chunking" # Change this path
    subprocess.Popen(["code", tbt_path], shell=True)
    ```
5. **Run at Startup (Background)**

    Press Win + R, type:
     ```sh
    shell:startup
 ```

    Create a new shortcut with this target:
 ```sh
    "C:\Users\sudha\AppData\Local\Programs\Python\Python310\pythonw.exe" "D:\Trials\jarvis\jarvis.py"
```

    Use pythonw.exe (not python.exe) to avoid opening a terminal window.

    Now Jarvis starts silently every time you log in.
## Usage

Run the script from your terminal:

```sh
python jarvis.py
```

The script will initialize and print "Listening for wake word...".

1.  Say **"Jarvis"** out loud.
2.  The console will show "Wake word detected. Listening for claps...".
3.  You now have 5 seconds to perform a clap gesture:
    *   **Double clap** to launch your configured apps.
    *   **Triple clap** to open YouTube.

## Dependencies

*   [pyaudio](https://people.csail.mit.edu/hubert/pyaudio/): For accessing the microphone audio stream.
*   [numpy](https://numpy.org/): For numerical audio data processing.
*   [pvporcupine](https://pypi.org/project/pvporcupine/): The Picovoice Porcupine wake word engine.