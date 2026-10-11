import os
import threading

from commands import *
from window import loadGUI, messages, commands
from voice import listen
from ai import ask_ai


messages.put("Hello!")
log_action("Started Program")

voice_ready = threading.Event()
voice_ready.set()

def respond(text):
    messages.put(text)
    speak(text)

    voice_ready.set()

    
def voice_loop():
    while True:

        # Don't listen while Wane is processing/speaking
        voice_ready.wait()

        command = listen()

        if not command:
            continue

        command = command.lower().strip()
        command = command.rstrip(".!?")

        print("Heard:", command)

        if command.startswith("wayne"):
            command = command[5:].strip()
            command = command.lstrip(",.!? ")

            if command:
                print("Wayne command:", command)

                # Stop listening while the command is handled
                voice_ready.clear()

                commands.put(command)

def main():

    while True:

        command = commands.get()

        if command == "internet":

            openinternet()
            log_action("Opened Internet")
            respond("Opening the Internet")

        elif command == "time":

            message = checktime()
            respond(message)
            log_action("Checked Time")

        elif command.startswith("open "):

            prog = command[5:].strip()

            program = find_program(prog)

            if program:

                respond("Opening Program")
                os.startfile(program)

                log_action(f"Opened {prog}")

            else:

                respond(f"Program '{prog}' not found")
                log_action(f"Could not find {prog}")

        elif command == "stop":

            respond("Goodnight")
            os._exit(0)

        else:

            print("Sending to AI:", command)

            try:

                response = ask_ai(command)

                print("Wayne:", response)

                respond(response)

            except Exception as e:

                print("AI Error:", e)
                respond("I'm having trouble connecting to my AI.")


wane_thread = threading.Thread(
    target=main,
    daemon=True
)

wane_thread.start()


voice_thread = threading.Thread(
    target=voice_loop,
    daemon=True
)

voice_thread.start()


loadGUI()
