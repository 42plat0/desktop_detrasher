import sys
import os
import time
import shutil

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QApplication, QPushButton, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir

from datetime import date

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")


class FileSystem():
    name = "Recent Files"

    directory = QDir(DESKTOP_PATH)
    files = directory.entryInfoList()

    starting_count = len(files)

    recent_files = QDir(f"{DESKTOP_PATH}/{name}/")

    directory.mkdir(name)

    @staticmethod
    def manageFiles():
        directory = QDir(DESKTOP_PATH)

        # updating file info
        files = directory.entryInfoList()
        updating_count = len(files)

        filesystem = {"files": [], "dirs": [], "new_file": None}

        for entity in files:
            if entity.isFile():
                filesystem["files"].append(entity)
            elif entity.isDir():
                filesystem["dirs"].append(entity)
            else:
                raise ValueError("Neither a file nor a directory")

        filesystem["new_file"] = FileSystem.new_file_move(files)

        return filesystem

    @staticmethod
    def new_file_move(files):
        updating_count = len(files)

        # Find updates to directory
        if FileSystem.starting_count < updating_count:
            for file in files:
                if file not in FileSystem.files:
                    FileSystem.move_file(file)
                    new_file = file.completeBaseName()

            FileSystem.files = files

            return new_file
        # File was deleted
        elif FileSystem.starting_count > updating_count:
            FileSystem.files = files

    @staticmethod
    def move_file(new_file):
        if new_file.isFile():
            file_name = f"{new_file.completeBaseName()}.{new_file.suffix()}"
        elif new_file.isDir():
            file_name = new_file.completeBaseName()

        file_path = f"{new_file.absolutePath()}/{file_name}"

        today = date.today().strftime("%Y-%m-%d")

        dir = FileSystem.recent_files

        if not dir.exists(today):
            dir.mkdir(today)

        today_dir = f"{dir.absolutePath()}/{today}/"

        # What if file already exists with the same name?
        try:
            shutil.move(file_path, today_dir)
        except Exception:
            print("File with the same name exists")


class WorkerThread(QThread):
    update_signal = pyqtSignal(dict)

    def run(self):
        while True:
            time.sleep(1)
            self.update_signal.emit(FileSystem.manageFiles())


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUi()

        self.thread = WorkerThread()
        self.thread.update_signal.connect(self.update_file_count)

        if not self.thread.isRunning():
            self.thread.start()

    def initUi(self):
        self.setWindowTitle("Desktop Detrasher")

        self.window = QWidget()
        self.setCentralWidget(self.window)
        self.resize(200, 100)

        file_count = str(len(FileSystem.manageFiles()['files']))
        dir_count = str(len(FileSystem.manageFiles()['dirs']))

        self.file_label = QLabel(self.window)
        self.file_label.setText(f"Failu skaicius: {file_count}")

        self.dir_label = QLabel(self.window)
        self.dir_label.setText(f"Direktoriju skaicius: {dir_count}")

        self.mbox = QMessageBox()

        self.vbox = QVBoxLayout(self.window)

        self.vbox.addWidget(self.file_label)
        self.vbox.addWidget(self.dir_label)

    def update_file_count(self, dir_filesystem):

        file_count = str(len(dir_filesystem['files']))
        dir_count = str(len(dir_filesystem['dirs']))

        self.file_label.setText(f"Failu skaicius: {file_count}")
        self.dir_label.setText(f"Direktoriju skaicius: {dir_count}")

        if dir_filesystem["new_file"] is not None:
            self.mbox.setText(
                f"File {dir_filesystem['new_file']} has been moved")
            self.mbox.exec_()


def main():
    app = QApplication([])

    window = Window()
    window.show()
    sys.exit(app.exec_())


main()
