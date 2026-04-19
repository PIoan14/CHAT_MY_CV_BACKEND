from pathlib import Path
import shutil

def delete_file(path: str):
    """
    Șterge un fișier specificat prin cale.
    """
    file_path = Path(path)
    try:
        if file_path.is_file():
            file_path.unlink()
            print(f"Fișierul '{path}' a fost șters cu succes.")
        else:
            print(f"Eroare: '{path}' nu este un fișier valid.")
    except Exception as e:
        print(f"A apărut o eroare la ștergere: {e}")

def delete_folder(path: str):
    """
    Șterge un folder și tot conținutul acestuia (recursiv).
    """
    folder_path = Path(path)
    try:
        if folder_path.is_dir():
            # Folosim shutil pentru a șterge folderul chiar dacă nu e gol
            shutil.rmtree(path)
            print(f"Folderul '{path}' și tot conținutul său au fost șterse.")
        else:
            print(f"Eroare: '{path}' nu este un director valid.")
    except Exception as e:
        print(f"A apărut o eroare la ștergerea folderului: {e}")
