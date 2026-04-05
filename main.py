# Окно запуска
import sys
sys.dont_write_bytecode = True

from pathlib import Path

# Надёжный запуск
root = Path(__file__).parent.absolute()
sys.path.insert(0, str(root))

from app.launcher import run

if __name__ == "__main__":
    print("Запуск программы..")
    run()