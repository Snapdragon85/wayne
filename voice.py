import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import tempfile
import os
import json


CONFIG_FILE = "config.json"
RECORD_SECONDS = 6

print("Loading Whisper...")

model = WhisperModel(
    "tiny.en",
    device="cpu",
    compute_type="int8"
)

print("Whisper loaded!")


def get_microphones():
    """Return all available input microphones."""

    devices = sd.query_devices()

    microphones = []

    for index, device in enumerate(devices):
        if device["max_input_channels"] > 0:
            microphones.append({
                "index": index,
                "name": device["name"],
                "samplerate": int(device["default_samplerate"])
            })

    return microphones


def get_default_microphone():
    """Get the Windows/sounddevice default input device."""

    device = sd.default.device[0]

    if device is None or device < 0:
        raise RuntimeError("No default microphone found.")

    info = sd.query_devices(device)

    if info["max_input_channels"] <= 0:
        raise RuntimeError("The default audio device is not a microphone.")

    return {
        "index": device,
        "name": info["name"],
        "samplerate": int(info["default_samplerate"])
    }


def load_saved_microphone():
    """Load the user's previously selected microphone."""

    if not os.path.exists(CONFIG_FILE):
        return None

    try:
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        return config.get("microphone")

    except Exception:
        return None


def save_microphone(name):
    """Save the selected microphone."""

    config = {}

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
        except Exception:
            pass

    config["microphone"] = name

    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file, indent=4)


def find_microphone():

    microphones = get_microphones()

    if not microphones:
        raise RuntimeError("No microphones were found.")

    saved_name = load_saved_microphone()

    # Try the saved microphone first
    if saved_name:

        for mic in microphones:
            if mic["name"] == saved_name:
                return mic

    # Otherwise use Windows default
    return get_default_microphone()


CURRENT_MIC = find_microphone()

print(
    f"Using microphone: "
    f"{CURRENT_MIC['name']} "
    f"({CURRENT_MIC['samplerate']} Hz)"
)


def set_microphone(name):

    global CURRENT_MIC

    microphones = get_microphones()

    for mic in microphones:

        if mic["name"] == name:

            # Make sure the microphone actually works
            sd.check_input_settings(
                device=mic["index"],
                samplerate=mic["samplerate"],
                channels=1,
                dtype="int16"
            )

            CURRENT_MIC = mic

            save_microphone(name)

            print(
                f"Microphone changed to: {mic['name']}"
            )

            return True

    return False


def test_microphone():

    print(
        f"Testing microphone: "
        f"{CURRENT_MIC['name']}"
    )

    try:

        recording = sd.rec(
            int(1 * CURRENT_MIC["samplerate"]),
            samplerate=CURRENT_MIC["samplerate"],
            channels=1,
            dtype="int16",
            device=CURRENT_MIC["index"]
        )

        sd.wait()

        # Check whether we actually received audio
        if recording.size == 0:
            return False

        print("Microphone test successful!")

        return True

    except Exception as e:

        print("Microphone test failed:", e)

        return False


def listen():

    samplerate = CURRENT_MIC["samplerate"]
    device = CURRENT_MIC["index"]

    print("Listening...")

    # How quiet the microphone must be before we consider it silence
    SILENCE_THRESHOLD = 500

    # How long silence must last before we stop recording
    SILENCE_DURATION = 0.8

    # Maximum amount of time to listen
    MAX_DURATION = 10

    # Minimum amount of speech required
    MIN_DURATION = 0.2

    import numpy as np
    import time

    audio_chunks = []

    speech_started = False
    silence_start = None

    start_time = time.time()

    with sd.InputStream(
        samplerate=samplerate,
        channels=1,
        dtype="int16",
        device=device,
        blocksize=1024
    ) as stream:

        while True:

            data, overflowed = stream.read(1024)

            audio = data[:, 0]

            volume = np.abs(audio).mean()

            # -------------------------
            # WAITING FOR SPEECH
            # -------------------------

            if not speech_started:

                if volume > SILENCE_THRESHOLD:

                    print("Speech detected!")

                    speech_started = True

                    audio_chunks.append(audio.copy())

                    silence_start = None

                else:

                    # Don't listen forever
                    if time.time() - start_time > MAX_DURATION:
                        return ""

            # -------------------------
            # RECORDING SPEECH
            # -------------------------

            else:

                audio_chunks.append(audio.copy())

                if volume < SILENCE_THRESHOLD:

                    if silence_start is None:
                        silence_start = time.time()

                    elif time.time() - silence_start >= SILENCE_DURATION:

                        print("Speech ended.")

                        break

                else:

                    silence_start = None

                if time.time() - start_time >= MAX_DURATION:

                    print("Maximum recording time reached.")

                    break


    if not audio_chunks:
        return ""

    recording = np.concatenate(audio_chunks)

    # Ignore extremely short recordings
    if len(recording) < samplerate * MIN_DURATION:
        return ""


    print("Processing...")


    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as file:

        filename = file.name


    try:

        wav.write(
            filename,
            samplerate,
            recording
        )

        segments, info = model.transcribe(
            filename,
            language="en",
            beam_size=5
        )

        text = " ".join(
            segment.text for segment in segments
        ).strip()

        text = text.rstrip(".!?")
        text = text.lower()

    finally:

        if os.path.exists(filename):
            os.remove(filename)


    print("You said:", text)

    return text
