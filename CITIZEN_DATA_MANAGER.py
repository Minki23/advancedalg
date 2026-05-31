# ============================================================
#  CITIZEN DATA MANAGER — TRZYGODZINNY PROJEKT STUDENCKI
# ============================================================
# Warianty:
#   CLI:   python citizen_manager.py
#   TESTY: python citizen_manager.py test
#   GUI:   python citizen_manager.py gui
#   API:   python citizen_manager.py api
#
#   DB:    SQLite używana automatycznie w tle (citizens.db)
#
#   Workflow GitHub: patrz zmienna GITHUB_WORKFLOW_YAML na dole pliku
# ============================================================

import sys
import logging
import sqlite3
from dataclasses import dataclass
from typing import List, Optional
import json
from dataclasses import asdict

# ============================================================
# 1. MODEL DANYCH: Citizen
# ============================================================

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
@dataclass
class Citizen:
    """
    Reprezentuje obywatela w systemie.
    """
    id: str
    first_name: str
    last_name: str
    age: int

    def __repr__(self):
        return f"{self.id} | {self.first_name} {self.last_name} | {self.age} lat"


# ============================================================
# 2. LISTA WIĄZANA (Linked List)
# ============================================================

class Node:
    """
    Pojedynczy element listy wiązanej.
    """
    def __init__(self, data: Citizen):
        self.data = data
        self.next: Optional["Node"] = None


class LinkedList:
    """
    Lista wiązana przechowująca obywateli.
    """
    def __init__(self):
        self.head: Optional[Node] = None

    def insert_at_beginning(self, data: Citizen):
        """
        Wstawia nowy element na początek listy.
        O(1)
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete_by_id(self, citizen_id: str) -> bool:
        """
        Usuwa obywatela po ID.
        O(n)
        """
        temp = self.head
        prev = None

        while temp and temp.data.id != citizen_id:
            prev = temp
            temp = temp.next

        if not temp:
            return False

        if prev:
            prev.next = temp.next
        else:
            self.head = temp.next

        return True

    def to_list(self) -> List[Citizen]:
        """
        Konwertuje listę wiązaną na zwykłą listę Pythona.
        """
        arr: List[Citizen] = []
        temp = self.head
        while temp:
            arr.append(temp.data)
            temp = temp.next
        return arr

    def clear(self):
        """
        Czyści listę.
        """
        self.head = None


# ============================================================
# 3. STOS (UNDO HISTORY)
# ============================================================

class Stack:
    """
    Implementacja stosu LIFO.
    """
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop() if self.items else None


# ============================================================
# 4. KOLEJKA (REGISTRATION QUEUE)
# ============================================================

class Queue:
    """
    Implementacja kolejki FIFO.
    """
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0) if self.items else None


# ============================================================
# 5. WARSTWA DB: SQLite
# ============================================================

class CitizenRepository:
    """
    Prosta warstwa dostępu do danych w SQLite.
    """
    def __init__(self, db_path: str = "citizens.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS citizens (
                id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def add(self, citizen: Citizen):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO citizens (id, first_name, last_name, age) VALUES (?, ?, ?, ?)",
            (citizen.id, citizen.first_name, citizen.last_name, citizen.age)
        )
        self.conn.commit()
        logging.info(f"Dodano obywatela {citizen.id}")

    def delete(self, citizen_id: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM citizens WHERE id = ?", (citizen_id,))
        self.conn.commit()
        logging.info(f"Usunięto obywatela {citizen_id}")

    def get_all(self) -> List[Citizen]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, first_name, last_name, age FROM citizens")
        rows = cur.fetchall()
        return [Citizen(*row) for row in rows]

    def close(self):
        self.conn.close()


# ============================================================
# 6. WYSZUKIWANIE
# ============================================================

def linear_search(arr: List[Citizen], target_id: str) -> int:
    """
    Linear search — O(n)
    """
    for i, citizen in enumerate(arr):
        if citizen.id == target_id:
            return i
    return -1


def binary_search(arr: List[Citizen], target_id: str) -> int:
    """
    Binary search — O(log n)
    Wymaga posortowanej listy.
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid].id == target_id:
            return mid
        elif arr[mid].id < target_id:
            left = mid + 1
        else:
            right = mid - 1

    return -1


# ============================================================
# 7. SORTOWANIE
# ============================================================

def bubble_sort(arr: List[Citizen]) -> None:
    """
    Bubble Sort — O(n^2)
    """
    n = len(arr)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if arr[j].id > arr[j + 1].id:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


def selection_sort(arr: List[Citizen]) -> None:
    """
    Selection Sort — O(n^2)
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j].id < arr[min_idx].id:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]


def insertion_sort(arr: List[Citizen]) -> None:
    """
    Insertion Sort — O(n^2)
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j].id > key.id:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key


def merge_sort(arr: List[Citizen]) -> List[Citizen]:
    """
    Merge Sort — O(n log n)
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    return _merge(left, right)


def _merge(left: List[Citizen], right: List[Citizen]) -> List[Citizen]:
    result: List[Citizen] = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i].id <= right[j].id:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(arr: List[Citizen]) -> List[Citizen]:
    """
    Quick Sort — O(n log n) average, O(n^2) worst
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[-1]
    left = [x for x in arr[:-1] if x.id <= pivot.id]
    right = [x for x in arr[:-1] if x.id > pivot.id]

    return quick_sort(left) + [pivot] + quick_sort(right)


# ============================================================
# 8. LOGIKA APLIKACJI (wspólna dla CLI/GUI/API)
# ============================================================

class CitizenService:
    """
    Warstwa logiki biznesowej:
    - trzyma listę wiązaną
    - synchronizuje z bazą SQLite
    """
    def __init__(self, repo: CitizenRepository):
        self.repo = repo
        self.citizens = LinkedList()
        self.history = Stack()
        self.registration_queue = Queue()
        self._load_from_db()

    def _load_from_db(self):
        """
        Wczytuje dane z DB do listy wiązanej.
        """
        self.citizens.clear()
        for c in self.repo.get_all():
            self.citizens.insert_at_beginning(c)
        logging.info(f"Wczytano {len(self.citizens.to_list())} obywateli z bazy danych")

    def add_citizen(self, citizen: Citizen):
        self.citizens.insert_at_beginning(citizen)
        self.repo.add(citizen)
        self.history.push(("add", citizen))
        logging.info(f"Dodano obywatela {citizen.id}")

    def delete_citizen(self, citizen_id: str) -> bool:
        arr = self.citizens.to_list()
        idx = linear_search(arr, citizen_id)
        if idx == -1:
            return False
        logging.info(f"Usunięto obywatela {citizen_id}")

        citizen = arr[idx]
        self.history.push(("delete", citizen))
        deleted = self.citizens.delete_by_id(citizen_id)
        if deleted:
            self.repo.delete(citizen_id)
        return deleted

    def list_citizens(self) -> List[Citizen]:
        return self.citizens.to_list()

    def sort_citizens(self, algorithm: str) -> None:
        arr = self.citizens.to_list()

        if algorithm == "bubble":
            bubble_sort(arr)
        elif algorithm == "selection":
            selection_sort(arr)
        elif algorithm == "insertion":
            insertion_sort(arr)
        elif algorithm == "merge":
            arr = merge_sort(arr)
        elif algorithm == "quick":
            arr = quick_sort(arr)

        self.citizens.clear()
        logging.info(f"Posortowano obywateli algorytmem {algorithm}")
        for c in reversed(arr):
            self.citizens.insert_at_beginning(c)

    def shuffle_citizens(self) -> None:
        arr = self.citizens.to_list()
        import random
        random.shuffle(arr)
        self.citizens.clear()
        for c in reversed(arr):
            self.citizens.insert_at_beginning(c)
        logging.info(f"Przemieszano obywateli losowo")

    def search_citizen(self, citizen_id: str, method: str = "linear") -> int:
        arr = self.citizens.to_list()
        if method == "linear":
            logging.info(f"Szukano obywatela {citizen_id} metodą liniową")
            return linear_search(arr, citizen_id)
        else:
            arr = merge_sort(arr)
            logging.info(f"Szukano obywatela {citizen_id} metodą binarną")
            return binary_search(arr, citizen_id)

    def enqueue_registration(self, citizen_id: str):
        logging.info(f"Dodano obywatela {citizen_id} do kolejki rejestracji")
        self.registration_queue.enqueue(citizen_id)

    def dequeue_registration(self) -> Optional[str]:
        logging.info(f"Obsłużono rejestrację obywatela {self.registration_queue.items[0] if self.registration_queue.items else 'brak'}")
        return self.registration_queue.dequeue()

    def undo(self):
        op = self.history.pop()
        if not op:
            return False
        action, citizen = op
        if action == "add":
            self.citizens.delete_by_id(citizen.id)
            self.repo.delete(citizen.id)
        elif action == "delete":
            self.citizens.insert_at_beginning(citizen)
            self.repo.add(citizen)
        logging.info(f"Cofnięto operację: {action} {citizen.id}")
        return True
    def export_to_json(self, filename="citizens.json"):
        data = [asdict(c) for c in self.list_citizens()]

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=4
            )

        logging.info(f"Eksportowano dane do {filename}")


# ============================================================
# 9. CLI
# ============================================================

def run_cli():
    repo = CitizenRepository()
    service = CitizenService(repo)

    while True:
        print("\n--- SYSTEM OBYWATELI (CLI) ---")
        print("1. Dodaj obywatela")
        print("2. Usuń obywatela")
        print("3. Wyświetl wszystkich")
        print("4. Sortuj")
        print("5. Szukaj")
        print("6. Dodaj do kolejki rejestracji")
        print("7. Obsłuż kolejkę")
        print("8. Cofnij ostatnią operację")
        print("9. Eksport do JSON")
        print("0. Wyjście")

        choice = input("Wybierz: ")

        if choice == "1":
            cid = input("ID: ")
            fn = input("Imię: ")
            ln = input("Nazwisko: ")
            age = int(input("Wiek: "))
            service.add_citizen(Citizen(cid, fn, ln, age))

        elif choice == "2":
            cid = input("Podaj ID do usunięcia: ")
            if service.delete_citizen(cid):
                print("Usunięto.")
            else:
                print("Nie znaleziono.")

        elif choice == "3":
            for c in service.list_citizens():
                print(c)

        elif choice == "4":
            print("1. Bubble 2. Selection 3. Insertion 4. Merge 5. Quick")
            s = input("Wybierz algorytm: ")
            mapping = {
                "1": "bubble",
                "2": "selection",
                "3": "insertion",
                "4": "merge",
                "5": "quick",
            }
            alg = mapping.get(s)
            if alg:
                service.sort_citizens(alg)
            else:
                print("Nieznany algorytm.")

        elif choice == "5":
            cid = input("Podaj ID: ")
            print("1. Linear 2. Binary (wymaga sortowania)")
            s = input("Wybierz: ")
            method = "linear" if s == "1" else "binary"
            idx = service.search_citizen(cid, method)
            print("Znaleziono!" if idx != -1 else "Brak wyniku.")

        elif choice == "6":
            cid = input("ID do rejestracji: ")
            service.enqueue_registration(cid)

        elif choice == "7":
            handled = service.dequeue_registration()
            print("Obsłużono:", handled)

        elif choice == "8":
            if not service.undo():
                print("Brak operacji do cofnięcia.")

        elif choice == "9":
            service.export_to_json()
            print("Wyeksportowano do citizens.json")

        elif choice == "0":
            repo.close()
            break


# ============================================================
# 10. GUI (Tkinter)
# ============================================================

def run_gui():
    import tkinter as tk
    from tkinter import messagebox

    repo = CitizenRepository()
    service = CitizenService(repo)

    root = tk.Tk()
    root.title("Citizen Manager (GUI)")

    listbox = tk.Listbox(root, width=60)
    listbox.pack(padx=10, pady=10)

    def refresh_list():
        listbox.delete(0, tk.END)
        for c in service.list_citizens():
            listbox.insert(tk.END, str(c))

    def add_citizen_gui():
        cid = entry_id.get()
        fn = entry_fn.get()
        ln = entry_ln.get()
        try:
            age = int(entry_age.get())
        except ValueError:
            messagebox.showerror("Błąd", "Wiek musi być liczbą.")
            return
        service.add_citizen(Citizen(cid, fn, ln, age))
        refresh_list()

    def delete_citizen_gui():
        selection = listbox.curselection()
        if not selection:
            return
        line = listbox.get(selection[0])
        cid = line.split("|")[0].strip()
        service.delete_citizen(cid)
        refresh_list()

    def search_citizen_gui():
        cid = entry_search.get()

        idx = service.search_citizen(cid)

        if idx == -1:
            messagebox.showinfo(
                "Wynik",
                "Nie znaleziono obywatela"
            )
        else:
            citizen = service.list_citizens()[idx]

            messagebox.showinfo(
                "Wynik",
                str(citizen)
            )
        

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=5)

    tk.Label(frame, text="ID").grid(row=0, column=0)
    tk.Label(frame, text="Imię").grid(row=1, column=0)
    tk.Label(frame, text="Nazwisko").grid(row=2, column=0)
    tk.Label(frame, text="Wiek").grid(row=3, column=0)

    entry_id = tk.Entry(frame)
    entry_fn = tk.Entry(frame)
    entry_ln = tk.Entry(frame)
    entry_age = tk.Entry(frame)

    entry_id.grid(row=0, column=1)
    entry_fn.grid(row=1, column=1)
    entry_ln.grid(row=2, column=1)
    entry_age.grid(row=3, column=1)

    tk.Label(frame, text="Szukaj ID").grid(row=4, column=0)

    entry_search = tk.Entry(frame)
    entry_search.grid(row=4, column=1)
    btn_add = tk.Button(root, text="Dodaj", command=add_citizen_gui)
    btn_del = tk.Button(root, text="Usuń zaznaczonego", command=delete_citizen_gui)
    btn_sort = tk.Button(root, text="Sortuj", command=lambda: [service.sort_citizens("merge"), refresh_list()])
    btn_shuffle = tk.Button(root, text="Losuj kolejność", command=lambda: [service.shuffle_citizens(), refresh_list()])
    btn_refresh = tk.Button(root, text="Odśwież", command=refresh_list)
    btn_search = tk.Button(
        root,
        text="Szukaj",
        command=search_citizen_gui
    )

    btn_search.pack(pady=2)

    btn_add.pack(pady=2)
    btn_del.pack(pady=2)
    btn_sort.pack(pady=2)
    btn_shuffle.pack(pady=2)    
    btn_refresh.pack(pady=2)

    refresh_list()
    root.mainloop()
    repo.close()


# ============================================================
# 11. API (FastAPI)
# ============================================================

def run_api():
    from fastapi import FastAPI, HTTPException
    import uvicorn

    repo = CitizenRepository()
    service = CitizenService(repo)

    app = FastAPI(title="Citizen Manager API")

    @app.get("/citizens")
    def get_citizens():
        return service.list_citizens()

    @app.post("/citizens")
    def add_citizen(citizen: Citizen):
        service.add_citizen(citizen)
        return {"status": "ok"}

    @app.delete("/citizens/{citizen_id}")
    def delete_citizen(citizen_id: str):
        if not service.delete_citizen(citizen_id):
            raise HTTPException(status_code=404, detail="Citizen not found")
        return {"status": "deleted"}
    
    @app.put("/citizens/{citizen_id}")
    def update_citizen(citizen_id: str, citizen: Citizen):
        if citizen_id != citizen.id:
            raise HTTPException(status_code=400, detail="ID mismatch")
        service.delete_citizen(citizen_id)
        service.add_citizen(citizen)
        return {"status": "updated"}

    uvicorn.run(app, host="0.0.0.0", port=8000)
    repo.close()


# ============================================================
# 12. TESTY JEDNOSTKOWE (unittest)
# ============================================================

import unittest

class TestCitizenManager(unittest.TestCase):

    def setUp(self):
        # używamy in-memory DB dla testów
        self.repo = CitizenRepository(":memory:")
        self.service = CitizenService(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_add_and_list(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertEqual(len(self.service.list_citizens()), 1)

    def test_delete(self):
        self.service.add_citizen(Citizen("1", "Jan", "Kowalski", 30))
        self.assertTrue(self.service.delete_citizen("1"))

    def test_registration_queue(self):
        citizen1 = Citizen("1", "Jan", "Kowalski", 30)
        citizen2 = Citizen("2", "Anna", "Nowak", 25)
        citizen3 = Citizen("3", "Piotr", "Wiśniewski", 40)

        self.service.add_citizen(citizen1)
        self.service.add_citizen(citizen2)
        self.service.add_citizen(citizen3)

        self.service.enqueue_registration(citizen1.id)
        self.service.enqueue_registration(citizen2.id)
        self.service.enqueue_registration(citizen3.id)

        self.assertEqual(self.service.dequeue_registration(), "1")
        self.assertTrue(self.service.delete_citizen("1"))

        self.assertEqual(self.service.dequeue_registration(), "2")
        self.assertTrue(self.service.delete_citizen("2"))

        self.assertEqual(self.service.dequeue_registration(), "3")
        self.assertTrue(self.service.delete_citizen("3"))

        self.assertIsNone(self.service.dequeue_registration())

        self.assertEqual(len(self.service.list_citizens()), 0)

def run_tests():
      unittest.main(
        argv=['first-arg-is-ignored'],
        exit=False,
        verbosity=2
    )

if __name__ == "__main__":
    import sys

    # Allow running mode via command line arguments (case-insensitive substring match)
    # Examples: python script.py api   -> runs API
    #           python script.py gui    -> runs GUI
    #           python script.py cli    -> runs CLI
    #           python script.py test   -> runs tests
    args = " ".join(sys.argv[1:]).lower()
    if args:
        if "api" in args:
            run_api()
        elif "gui" in args:
            run_gui()
        elif "cli" in args:
            run_cli()
        elif "test" in args or "tests" in args or "unittest" in args:
            run_tests()
        else:
            # fallback to interactive if no known keyword provided
            pass

    # Interactive prompt (only if no recognized command-line mode was provided)
    if not args or (args and not any(k in args for k in ("api", "gui", "cli", "test", "tests", "unittest"))):
        print("Wybierz tryb uruchomienia:")
        print("1. GUI")
        print("2. API")
        print("3. CLI")
        print("4. Testy")
        choice = input("Wybierz: ")
        if choice == "1":
            run_gui()
        elif choice == "2":
            run_api()
        elif choice == "3":
            run_cli()
        elif choice == "4":
            run_tests()
    