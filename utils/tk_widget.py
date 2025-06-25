import tkinter as tk
from tkinter import filedialog

# fonction pour sélectionner un répertoire
def select_dossier() -> str:
    root = tk.Tk()
    root.lift()  # Mettre au premier plan
    root.attributes("-topmost", True)  # Toujours au-dessus
    root.withdraw()  # Cacher la fenêtre principale
    folder_path = filedialog.askdirectory()
    return folder_path


# si le script est exécuté directement, on appelle la fonction de sélection de dossier
if __name__ == "__main__":
    print(select_dossier())