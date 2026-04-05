# главное окно

import customtkinter as ctk
from tkinter import filedialog

import ctypes
from pathlib import Path

from ..models import Shortcut
from ..storage import load_apps, save_apps
from ..windows_utils import get_shortcut_info, launch_app, show_properties, extract_icon
from .icon_grid import IconGrid


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Для Tkinter добавление ico делается через ctypes
        # ID приложения для Windows (чтобы была своя иконка в панели задач)
        try:
            myappid = "parental.launcher.app"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        # Установка иконки
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        icon_path = BASE_DIR / "assets" / "photo.ico"

        if icon_path.exists():
            self.iconbitmap(str(icon_path))
            print("Иконка окна установлена")
        else:
            print("Иконка не найдена")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Родительский Лаунчер")
        self.geometry("1150x720") # Основной размер окна при запуске
        self.minsize(950, 650) # Минимальный размер
        self.maxsize(950, 650) # Максимальный размер
        self.configure(fg_color="#1E1E1E")

        self.apps: list[Shortcut] = load_apps()
        self.grid = None
        
        self.create_ui()
        self.refresh_grid()

    def create_ui(self):
        # Верхняя панель
        top = ctk.CTkFrame(self, fg_color="#2A2A2A", height=70)
        top.pack(fill="x", padx=12, pady=12)
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="Мои приложения", font=ctk.CTkFont(size=22, weight="bold")).pack(side="left", padx=25)

        # Поиск
        self.search_var = ctk.StringVar()
        search = ctk.CTkEntry(top, placeholder_text="Поиск приложений...", 
                              textvariable=self.search_var, width=350, height=35)
        search.pack(side="left", fill="x", expand=True, padx=10)
        self.search_var.trace("w", lambda *a: self.refresh_grid())

        # Кнопка "+ Добавить"
        add_btn = ctk.CTkButton(top, text="+ Добавить", width=140, height=35,
                                command=self.open_add_dialog)
        add_btn.pack(side="right", padx=25)

        # Прокручиваемая область с иконками
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#1E1E1E")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.grid = IconGrid(self.scroll, on_delete_callback=self.delete_app)

    def open_add_dialog(self):
        """Добавление приложений: поддержка и .lnk, и .exe"""
        files = filedialog.askopenfilenames(
            title="Выберите ярлыки или исполняемые файлы",
            initialdir=r"C:\Users\User\AppData\Roaming\Microsoft\Windows\Start Menu\Programs",
            filetypes=[
                ("Ярлыки и приложения", "*.lnk *.exe"),
                ("Ярлыки Windows", "*.lnk"),
                ("Исполняемые файлы", "*.exe"),
                ("Все файлы", "*.*")
            ]
        )
       
        if not files:
            return

        added = []
        for f in files:
            path = Path(f)
            ext = path.suffix.lower()

            if ext == ".lnk":
                # Для ярлыков Windows
                info = get_shortcut_info(f)
                if info:
                    shortcut = Shortcut(
                        name=info["name"],
                        lnk_path=info["lnk_path"],
                        target=info.get("target", "")
                    )
                    if not any(a.lnk_path == shortcut.lnk_path for a in self.apps):
                        added.append(shortcut)

            elif ext == ".exe":
                # Для .exe файлов
                name = path.stem  # имя без .exe
                exe_path = str(path)

                shortcut = Shortcut(
                    name=name,
                    lnk_path=exe_path, # важно: lnk_path хранит путь к .exe
                    target=exe_path
                )
                if not any(a.lnk_path == shortcut.lnk_path for a in self.apps):
                    added.append(shortcut)

            else:
                continue # пропускаем другие типы файлов

        if added:
            self.apps.extend(added)
            save_apps(self.apps)
            self.refresh_grid()
            print(f"Добавлено {len(added)} приложений")
        else:
            print("Не добавлено ни одного нового приложения")

    def delete_app(self, app: Shortcut):
        self.apps = [a for a in self.apps if a.lnk_path != app.lnk_path]
        save_apps(self.apps)
        self.refresh_grid()

    def refresh_grid(self):
        self.grid.clear()
        text = self.search_var.get().lower().strip()

        filtered = [app for app in self.apps if not text or text in app.name.lower()]

        for i, app in enumerate(filtered):
            frame = self.grid.add_icon(app)
            frame.grid(row=i//5, column=i%5, padx=15, pady=20, sticky="n")