import os
import webbrowser
import subprocess
import glob
import wave
import winsound
import re
import json

from piper import PiperVoice
from datetime import datetime


# -------------------------
# CONFIG
# -------------------------

CONFIG_FILE = "config.json"

DEFAULT_VOICE = "voices/en_US-ryan-medium.onnx"


# -------------------------
# VOICE SETTINGS
# -------------------------

def load_voice_settings():

    if not os.path.exists(CONFIG_FILE):

        return {
            "voice": DEFAULT_VOICE
        }

    try:

        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)

        return {
            "voice": config.get(
                "voice",
                DEFAULT_VOICE
            )
        }

    except Exception:

        return {
            "voice": DEFAULT_VOICE
        }


voice_settings = load_voice_settings()


PIPER_MODEL = voice_settings["voice"]


print("Loading Wayne's voice...")

piper_voice = PiperVoice.load(
    PIPER_MODEL
)

print("Wayne's voice loaded!")


def save_voice_settings():

    config = {}

    if os.path.exists(CONFIG_FILE):

        try:

            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)

        except Exception:
            pass


    config["voice"] = voice_settings["voice"]


    with open(CONFIG_FILE, "w") as file:

        json.dump(
            config,
            file,
            indent=4
        )


def set_voice(path):

    global piper_voice

    if not os.path.exists(path):

        print(
            f"Voice file not found: {path}"
        )

        return False


    try:

        print(
            f"Loading voice: {path}"
        )

        new_voice = PiperVoice.load(
            path
        )

        piper_voice = new_voice

        voice_settings["voice"] = path

        save_voice_settings()

        print(
            "Voice changed successfully!"
        )

        return True


    except Exception as e:

        print(
            "Voice error:",
            e
        )

        return False


# -------------------------
# SPEECH CLEANUP
# -------------------------

def clean_for_speech(text):

    # Remove Markdown bold/italic markers
    text = re.sub(
        r"\*\*(.*?)\*\*",
        r"\1",
        text
    )

    text = re.sub(
        r"\*(.*?)\*",
        r"\1",
        text
    )


    # Remove LaTeX math delimiters
    text = text.replace(
        "$",
        ""
    )


    # Convert common LaTeX commands
    replacements = {

        r"\\times":
            " times ",

        r"\\div":
            " divided by ",

        r"\\frac":
            " divided by ",

        r"\\sqrt":
            " square root of ",

        r"\\pi":
            " pi ",

        r"\\pm":
            " plus or minus ",

        r"\\leq":
            " less than or equal to ",

        r"\\geq":
            " greater than or equal to ",

        r"\\neq":
            " not equal to ",
    }


    for pattern, replacement in replacements.items():

        text = re.sub(
            pattern,
            replacement,
            text
        )


    # Convert powers
    text = re.sub(
        r"(\w+)\^(\w+)",
        r"\1 to the power of \2",
        text
    )


    # Remove Markdown headings
    text = re.sub(
        r"^#+\s*",
        "",
        text,
        flags=re.MULTILINE
    )


    # Remove numbered lists
    text = re.sub(
        r"^\s*\d+\.\s*",
        "",
        text,
        flags=re.MULTILINE
    )


    # Remove bullet points
    text = re.sub(
        r"^\s*[-•]\s*",
        "",
        text,
        flags=re.MULTILINE
    )


    # Collapse whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()


# -------------------------
# COMMANDS
# -------------------------

def openinternet():

    print(
        "Opening Internet Web Browser"
    )

    webbrowser.open(
        "https://www.google.com"
    )


def checktime():

    now = datetime.now()

    day = now.strftime(
        "%A"
    )

    date = now.strftime(
        "%B %d, %Y"
    )

    time = now.strftime(
        "%I:%M %p"
    )


    message = (
        f"Today is {day}, "
        f"{date}. "
        f"The time is {time}."
    )


    print(message)

    return message


def log_action(action):

    with open(
        "actions.txt",
        "a"
    ) as file:

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        file.write(
            f"[{timestamp}] {action}\n"
        )


def find_program(program_name):

    program_name = (
        program_name
        .lower()
        .strip()
    )


    start_menu_locations = [

        os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"
        ),

        os.path.expandvars(
            r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs"
        )

    ]


    for location in start_menu_locations:

        for shortcut in glob.glob(
            os.path.join(
                location,
                "**",
                "*"
            ),
            recursive=True
        ):

            filename = (
                os.path.basename(
                    shortcut
                ).lower()
            )


            if filename == (
                program_name + ".lnk"
            ):

                return shortcut


    return None


# -------------------------
# TEXT TO SPEECH
# -------------------------

def speak(text):

    speech_text = clean_for_speech(
        text
    )


    if not speech_text:
        return


    print(
        "Speaking:",
        speech_text
    )


    with wave.open(
        "wayne_tts.wav",
        "wb"
    ) as wav_file:

        wav_file.setnchannels(
            1
        )

        wav_file.setsampwidth(
            2
        )

        wav_file.setframerate(
            piper_voice.config.sample_rate
        )


        for chunk in piper_voice.synthesize(
            speech_text
        ):

            wav_file.writeframes(
                chunk.audio_int16_bytes
            )


    winsound.PlaySound(
        "wayne_tts.wav",
        winsound.SND_FILENAME
    )
