import sys
import os
import time

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QApplication, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir

from datetime import date

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

file_count = [0, ]
file_list = []

class FileSystem():
    def __init__(self):
        global file_list, file_count

        self.directory = QDir(DESKTOP_PATH)

        self.recent_files = "Recent Files/"

        self.date = date.today().strftime("%Y-%m-%d")

        self.files = self.directory.entryInfoList()

        if len(file_list) < 2:
            file_list = self.files

        if file_count[-1] != len(self.files):
            file_count.append(len(self.files))

            # get different file
            for file in self.files:
                if file not in file_list:
                    self.new_file = file


    def get_dir_file_groups(self):
        is_state_diff = self.is_state_changed()

        filesystem = {"files": [], "dirs": []}

        for entity in self.files:
            if entity.isFile():
                filesystem["files"].append(entity)
            elif entity.isDir():
                filesystem["dirs"].append(entity)
            else:
                raise ValueError("Neither a file nor a directory")

        if is_state_diff is True:
            self.manage_new_file()
            print(self.new_file)

        return filesystem

    def is_state_changed(self):
        global file_count

        if len(file_count) > 2:
            file_count.pop(0)
            return file_count[-1] != file_count[-2]

    def get_file_group_count(self):
        groups = self.get_dir_file_groups()

        file_count = len(groups["files"])
        dir_count = len(groups["dirs"])

        return {"files": file_count, "dirs": dir_count}

    # sukurti folderi naujiem fialam, jei data ta pati sukurimo fialo,
        # QDir.exists()
    # tai tada dedam i ta pacia data pagla kuria sukurtas folderis
    # tada sukuriam nauja jei nauja data ir ner ta data folderio

    def manage_new_file(self):
        # create new parent dir
        # doesnt recreate if exists
        self.directory.mkdir(self.recent_files)

        self.recent_files_dir = QDir(f"{DESKTOP_PATH}/{self.recent_files}")

        date_dir = f"{self.recent_files_dir.path()}/{self.date}/"

        # second created file in a day
        if self.recent_files_dir.exists(self.date):
            print(self.new_file)
            # os.replace(self.new_file.absoluteFilePath(), date_dir)
        else:  # first file
            self.recent_files_dir.mkdir(self.date)

#   TWO THREADS
# Vienas threadas updatina counta, kitas threadas lygina ar pasikeite:


class WorkerThread(QThread):
    update_signal = pyqtSignal(dict)

    def run(self):
        while True:
            time.sleep(1)
            self.update_signal.emit(FileSystem().get_file_group_count())


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.filesystem = FileSystem()

        self.initUi()

        self.thread = WorkerThread()
        self.thread.update_signal.connect(self.update_file_count)

        if not self.thread.isRunning():
            self.thread.start()

    def initUi(self):
        self.setWindowTitle("Desktop Detrasher")

        window = QWidget()
        self.setCentralWidget(window)
        self.resize(200, 100)

        dir_filesystem = self.filesystem.get_file_group_count()

        file_count = str(dir_filesystem["files"])
        dir_count = str(dir_filesystem["dirs"])

        self.file_label = QLabel(window)
        self.file_label.setText(f"Failu skaicius: {file_count}")

        self.dir_label = QLabel(window)
        self.dir_label.setText(f"Direktoriju skaicius: {dir_count}")

        vbox = QVBoxLayout(window)

        # vbox.addWidget(desktop)
        vbox.addWidget(self.file_label)
        vbox.addWidget(self.dir_label)

    def update_file_count(self, dir_filesystem):
        self.file_label.setText(f"Failu skaicius: {dir_filesystem['files']}")
        self.dir_label.setText(f"Direktoriju skaicius: {dir_filesystem['dirs']}")


def main():
    app = QApplication([])

    window = Window()

    window.show()

    sys.exit(app.exec_())


main()
