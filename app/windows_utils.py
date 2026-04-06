# работа с .lnk, иконками, свойствами

import os
import subprocess
from pathlib import Path
import win32com.client
from PIL import Image
from icoextract import IconExtractor
# Для получения стандартных иконок приложений
import win32gui
import win32ui
import win32con

# Импорт для лучшего извлечения иконок
try:
    from icoextract import IconExtractor
    ICOEXTRACT_AVAILABLE = True
except ImportError:
    ICOEXTRACT_AVAILABLE = False
    print("Warning: icoextract не установлен. Иконки будут извлекаться только через fallback.")

APP_DIR = Path(os.getenv("LOCALAPPDATA")) / "ParentLauncher"
ICONS_DIR = APP_DIR / "icons"

ICONS_DIR.mkdir(parents=True, exist_ok=True)
#ICONS_DIR = Path("data/icons")
#ICONS_DIR.mkdir(exist_ok=True)

def get_shortcut_info(lnk_path: str) -> dict:
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        sc = shell.CreateShortCut(lnk_path)
        return {
            "name": Path(lnk_path).stem,
            "lnk_path": lnk_path,
            "target": sc.Targetpath,
            "icon_location": sc.IconLocation[0] if sc.IconLocation else sc.Targetpath
        }
    except:
        return None

def extract_icon(lnk_or_exe_path: str, name: str) -> str | None:
    """Универсальная функция извлечения иконки (поддержка новых версий icoextract)"""
    if not lnk_or_exe_path:
        return None

    # Безопасное имя файла
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip("_")
    icon_file = ICONS_DIR / f"{safe_name}.png"

    if icon_file.exists():
        return str(icon_file)

    try:
        # 1. Пытаемся использовать icoextract
        if ICOEXTRACT_AVAILABLE:
            try:
                extractor = None
                path_obj = Path(lnk_or_exe_path)

                # Если это .lnk — получаем реальный .exe
                if path_obj.suffix.lower() == ".lnk":
                    shell = win32com.client.Dispatch("WScript.Shell")
                    sc = shell.CreateShortCut(str(path_obj))
                    target = sc.Targetpath
                else:
                    target = str(path_obj)

                # Пробуем создать extractor из .exe / .dll
                if target and Path(target).exists():
                    try:
                        extractor = IconExtractor(target)
                    except Exception as e:
                        print(f"Не удалось создать IconExtractor для {name}: {e}")

                # Если не получилось — пробуем иконку из ярлыка
                if not extractor and path_obj.suffix.lower() == ".lnk":
                    if sc.IconLocation and sc.IconLocation[0]:
                        icon_loc = sc.IconLocation[0]
                        if Path(icon_loc).exists():
                            try:
                                extractor = IconExtractor(icon_loc)
                            except:
                                pass

                if extractor:
                    # Новая версия icoextract: используем export_icon или get_icon (по индексу)
                    try:
                        # Пробуем извлечь первую иконку
                        img = extractor.get_icon(num=0)
                        if img:
                            img.save(icon_file, "PNG")
                            print(f"Иконка извлечена через icoextract: {name}")
                            return str(icon_file)
                    except:
                        # Альтернатива: export_icon в BytesIO
                        try:
                            from io import BytesIO
                            bio = BytesIO()
                            extractor.export_icon(bio, num=0)
                            bio.seek(0)
                            img = Image.open(bio)
                            img.save(icon_file, "PNG")
                            print(f"Иконка извлечена (export_icon): {name}")
                            return str(icon_file)
                        except:
                            pass

            except Exception as e:
                print(f"icoextract не сработал для {name}: {e}")

        # 2. Fallback — старый базовый метод
        print(f"Используем fallback для {name}")
        return _extract_icon_fallback(lnk_or_exe_path, name)

    except Exception as e:
        print(f"Общая ошибка extract_icon для {name}: {e}")
        return None


def _extract_icon_fallback(lnk_or_exe_path: str, name: str) -> str | None:
    """Базовый метод через win32gui (fallback)"""
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip("_")
    icon_file = ICONS_DIR / f"{safe_name}.png"

    if icon_file.exists():
        return str(icon_file)

    try:
        import win32gui
        import win32ui
        import win32con

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = None
        target = lnk_or_exe_path

        if lnk_or_exe_path.lower().endswith('.lnk'):
            shortcut = shell.CreateShortCut(lnk_or_exe_path)
            target = shortcut.Targetpath

        icon_path = None
        icon_index = 0

        if shortcut and shortcut.IconLocation and shortcut.IconLocation[0]:
            parts = str(shortcut.IconLocation[0]).split(",")
            icon_path = parts[0]
            if len(parts) > 1:
                try:
                    icon_index = int(parts[1])
                except:
                    pass

        if not icon_path or not Path(icon_path).exists():
            icon_path = target
            icon_index = 0

        if not Path(icon_path).exists():
            icon_path = r"C:\Windows\System32\shell32.dll"
            icon_index = 0

        large, _ = win32gui.ExtractIconEx(icon_path, icon_index)
        if not large:
            return None

        hicon = large[0]
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 256, 256)
        hdc_mem = hdc.CreateCompatibleDC()
        hdc_mem.SelectObject(hbmp)

        win32gui.DrawIconEx(hdc_mem.GetHandleOutput(), 0, 0, hicon, 256, 256, 0, None, win32con.DI_NORMAL)

        bmpinfo = hbmp.GetInfo()
        bmpstr = hbmp.GetBitmapBits(True)

        img = Image.frombuffer("RGBA", (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
                               bmpstr, "raw", "BGRA", 0, 1)

        img.save(icon_file)
        win32gui.DestroyIcon(hicon)

        return str(icon_file)

    except Exception as e:
        print(f"Ошибка fallback для {name}: {e}")
        return None

def launch_app(path: str):
    try:
        if path.lower().endswith('.lnk'):
            os.startfile(path)
        else:
            # Для .exe запускаем напрямую
            subprocess.Popen([path], shell=False)
    except Exception as e:
        print(f"Ошибка запуска {path}: {e}")

def show_properties(lnk_path: str):
    """Вомозможна дальнейшая реализация отображения Свойств программы, чтобы посмотреть полное расположение Ярлыка или приложения Windows."""
    """Открывает окно «Свойства» ярлыка (.lnk)"""
    try:
        # Самый стабильный и рекомендуемый способ на Windows 10/11
        # explorer.exe открывает проводник с выделенным файлом + фокус на нём
        result = subprocess.run(
            ['explorer.exe', '/select,', lnk_path],
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Explorer вернул код ошибки: {result.returncode}")
        
        print(f"Открыто окно свойств для: {Path(lnk_path).name}")
        
    except Exception as e:
        print(f"Ошибка при открытии свойств: {e}")
        
        # Крайний запасной вариант
        try:
            os.startfile(lnk_path, 'properties')
        except Exception as e2:
            print(f"Запасной вариант тоже не сработал: {e2}")
