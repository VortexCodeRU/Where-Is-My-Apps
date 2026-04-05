# логика лаунчера

from .ui.main_window import MainWindow

def run():
    app = MainWindow()
    app.mainloop()