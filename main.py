import customtkinter as ctk
from src.ui import NgrokDarkApp


def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = NgrokDarkApp()
    app.protocol(
        "WM_DELETE_WINDOW", lambda: (app.parar_conexao(), app.destroy())
    )
    app.mainloop()


if __name__ == "__main__":
    main()