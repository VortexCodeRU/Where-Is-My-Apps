# окно добавления ярлыков

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path

from ..windows_utils import get_shortcut_info
from ..models import Shortcut


class AddDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_add_callback):
        super().__init__(parent)
        self.title("Добавить приложения")
        self.geometry("600x200")
        self.configure(fg_color="#1E1E1E")
        self.on_add = on_add_callback

        ctk.CTkLabel(self, 
                     text="Выберите ярлыки (.lnk) из меню Пуск",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(pady=20)

        # Кнопка, которая сразу открывает нужную папку
        btn = ctk.CTkButton(
            self,
            text="Открыть папку меню Пуск и выбрать ярлыки",
            width=380,
            height=45,
            font=ctk.CTkFont(size=14),
            command=self.select_files
        )
        btn.pack(pady=20)

        hint = ctk.CTkLabel(
            self,
            text="Путь: C:\\Users\\User\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs",
            text_color="#888888",
            font=ctk.CTkFont(size=12)
        )
        hint.pack()

    def select_files(self):
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
            self.destroy()
            return

        added = []
        for f in files:
            path = Path(f)
            
            if path.suffix.lower() == ".lnk":
                # Для ярлыков — используем существующий код
                info = get_shortcut_info(f)
                if info:
                    shortcut = Shortcut(
                        name=info["name"],
                        lnk_path=info["lnk_path"],
                        target=info.get("target", "")
                    )
                    added.append(shortcut)
                    
            elif path.suffix.lower() == ".exe":
                # Для .exe создаём "виртуальный" shortcut
                shortcut = Shortcut(
                    name=path.stem, # имя без расширения
                    lnk_path=str(path), # сохраняем путь к .exe как lnk_path
                    target=str(path)
                )
                added.append(shortcut)
                
            else:
                # На всякий случай пропускаем другие файлы
                continue

        if added:
            self.on_add(added)
        self.destroy()