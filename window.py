import tkinter as tk
import tkinter.messagebox as messagebox
import queue
import os

from voice import (
    get_microphones,
    set_microphone,
    test_microphone,
    CURRENT_MIC
)

from commands import (
    set_voice,
    voice_settings
)


messages = queue.Queue()
commands = queue.Queue()


# -------------------------
# COLORS
# -------------------------

BG = "#0b0f14"
PANEL = "#111820"
PANEL_LIGHT = "#18222d"
ACCENT = "#00aaff"
ACCENT_HOVER = "#0088cc"
TEXT = "#e8f1f8"
TEXT_DIM = "#7f95a8"


def loadGUI():

    window = tk.Tk()

    window.title("WAYNE")
    window.geometry("700x800")
    window.minsize(600, 700)

    window.configure(
        bg=BG
    )


    # -------------------------
    # HEADER
    # -------------------------

    header = tk.Frame(
        window,
        bg=BG
    )

    header.pack(
        fill="x",
        padx=25,
        pady=(20, 10)
    )


    title = tk.Label(
        header,
        text="WAYNE",
        font=("Arial", 28, "bold"),
        fg=ACCENT,
        bg=BG
    )

    title.pack(
        side="left"
    )


    status = tk.Label(
        header,
        text="● ONLINE",
        font=("Arial", 10, "bold"),
        fg=ACCENT,
        bg=BG
    )

    status.pack(
        side="right",
        pady=10
    )


    # -------------------------
    # CHAT AREA
    # -------------------------

    chat_frame = tk.Frame(
        window,
        bg=PANEL
    )

    chat_frame.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=10
    )


    chat = tk.Text(
        chat_frame,
        bg=PANEL,
        fg=TEXT,
        insertbackground=ACCENT,
        font=("Arial", 12),
        relief="flat",
        borderwidth=0,
        wrap="word",
        padx=15,
        pady=15
    )

    chat.pack(
        fill="both",
        expand=True
    )

    chat.config(
        state="disabled"
    )


    # -------------------------
    # INPUT AREA
    # -------------------------

    input_frame = tk.Frame(
        window,
        bg=BG
    )

    input_frame.pack(
        fill="x",
        padx=25,
        pady=(5, 15)
    )


    entry = tk.Entry(
        input_frame,
        font=("Arial", 13),
        bg=PANEL_LIGHT,
        fg=TEXT,
        insertbackground=ACCENT,
        relief="flat",
        borderwidth=0
    )

    entry.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=10,
        padx=(0, 10)
    )


    def send_command():

        command = entry.get().strip()

        if command:

            commands.put(command)

            entry.delete(
                0,
                tk.END
            )


    send_button = tk.Button(
        input_frame,
        text="SEND",
        command=send_command,
        bg=ACCENT,
        fg="white",
        activebackground=ACCENT_HOVER,
        activeforeground="white",
        relief="flat",
        borderwidth=0,
        font=("Arial", 10, "bold"),
        padx=20,
        pady=10,
        cursor="hand2"
    )

    send_button.pack(
        side="right"
    )


    entry.bind(
        "<Return>",
        lambda event: send_command()
    )


    # -------------------------
    # SETTINGS
    # -------------------------

    def open_settings():

        settings = tk.Toplevel(window)

        settings.title("WAYNE Settings")
        settings.geometry("500x500")

        settings.configure(
            bg=BG
        )


        tk.Label(
            settings,
            text="WAYNE SETTINGS",
            font=("Arial", 22, "bold"),
            fg=ACCENT,
            bg=BG
        ).pack(pady=(25, 20))


        # -------------------------
        # MICROPHONE
        # -------------------------

        tk.Label(
            settings,
            text="MICROPHONE",
            font=("Arial", 11, "bold"),
            fg=TEXT_DIM,
            bg=BG
        ).pack(
            anchor="w",
            padx=30
        )


        microphones = get_microphones()

        microphone_names = [
            mic["name"]
            for mic in microphones
        ]


        selected_microphone = tk.StringVar()

        selected_microphone.set(
            CURRENT_MIC["name"]
        )


        microphone_menu = tk.OptionMenu(
            settings,
            selected_microphone,
            *microphone_names
        )

        microphone_menu.config(
            width=42,
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="white",
            highlightthickness=0
        )

        microphone_menu.pack(
            pady=(5, 15)
        )


        def test_selected_microphone():

            name = selected_microphone.get()

            try:

                if not set_microphone(name):

                    raise Exception(
                        "Could not select microphone."
                    )


                if test_microphone():

                    messagebox.showinfo(
                        "WAYNE",
                        "Microphone is working!"
                    )

                else:

                    messagebox.showerror(
                        "WAYNE",
                        "No audio was received."
                    )


            except Exception as e:

                messagebox.showerror(
                    "Microphone Error",
                    str(e)
                )


        tk.Button(
            settings,
            text="TEST MICROPHONE",
            command=test_selected_microphone,
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(
            pady=(0, 25)
        )


        # -------------------------
        # VOICE
        # -------------------------

        tk.Label(
            settings,
            text="VOICE",
            font=("Arial", 11, "bold"),
            fg=TEXT_DIM,
            bg=BG
        ).pack(
            anchor="w",
            padx=30
        )


        voice_folder = "voices"

        voice_files = []

        if os.path.exists(voice_folder):

            for filename in os.listdir(voice_folder):

                if filename.endswith(".onnx"):

                    voice_files.append(
                        os.path.join(
                            voice_folder,
                            filename
                        )
                    )


        voice_names = [
            os.path.basename(path)
            for path in voice_files
        ]


        selected_voice = tk.StringVar()

        current_voice = os.path.basename(
            voice_settings["voice"]
        )


        if current_voice in voice_names:

            selected_voice.set(
                current_voice
            )

        elif voice_names:

            selected_voice.set(
                voice_names[0]
            )


        voice_menu = tk.OptionMenu(
            settings,
            selected_voice,
            *voice_names
        )

        voice_menu.config(
            width=42,
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="white",
            highlightthickness=0
        )

        voice_menu.pack(
            pady=(5, 10)
        )


        def apply_voice():

            name = selected_voice.get()

            path = os.path.join(
                voice_folder,
                name
            )


            if set_voice(path):

                messagebox.showinfo(
                    "WAYNE",
                    "Voice changed!"
                )

            else:

                messagebox.showerror(
                    "WAYNE",
                    "Could not load voice."
                )


        tk.Button(
            settings,
            text="APPLY VOICE",
            command=apply_voice,
            bg=PANEL_LIGHT,
            fg=TEXT,
            activebackground=ACCENT,
            activeforeground="white",
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=8,
            cursor="hand2"
        ).pack(
            pady=5
        )


        # -------------------------
        # CLOSE
        # -------------------------

        tk.Button(
            settings,
            text="CLOSE",
            command=settings.destroy,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            relief="flat",
            borderwidth=0,
            padx=25,
            pady=10,
            cursor="hand2"
        ).pack(
            pady=25
        )


    # -------------------------
    # SETTINGS BUTTON
    # -------------------------

    settings_button = tk.Button(
        window,
        text="⚙ SETTINGS",
        command=open_settings,
        bg=BG,
        fg=TEXT_DIM,
        activebackground=BG,
        activeforeground=ACCENT,
        relief="flat",
        borderwidth=0,
        cursor="hand2"
    )

    settings_button.pack(
        pady=(0, 10)
    )


    # -------------------------
    # MESSAGE UPDATE
    # -------------------------

    def update_gui():

        try:

            while True:

                message = messages.get_nowait()

                chat.config(
                    state="normal"
                )

                chat.insert(
                    tk.END,
                    f"Wayne: {message}\n\n"
                )

                chat.see(
                    tk.END
                )

                chat.config(
                    state="disabled"
                )

        except queue.Empty:

            pass


        window.after(
            100,
            update_gui
        )


    update_gui()

    entry.focus()

    window.mainloop()
