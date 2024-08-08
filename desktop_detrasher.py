import sys
import os
import time
import shutil

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QApplication, QPushButton
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir

from datetime import date

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")


class FileSystem():
    recent_files = "Recent Files/"
        
    
    directory = QDir(DESKTOP_PATH)
    files = directory.entryInfoList()

    starting_count = len(files)

    recent_files = QDir(f"{DESKTOP_PATH}/Recent Files/")

    @staticmethod
    def manageFiles():
        directory = QDir(DESKTOP_PATH)

        # updating file info
        files = directory.entryInfoList()
        updating_count = len(files)

        filesystem = {"files": [], "dirs": []}

        for entity in files:
            if entity.isFile():
                filesystem["files"].append(entity)
            elif entity.isDir():
                filesystem["dirs"].append(entity)
            else:
                raise ValueError("Neither a file nor a directory")
            
        
        # Find updates to directory 
        if FileSystem.starting_count < updating_count:            
            for file in files:
                if file not in FileSystem.files:
                    FileSystem.move_file(file)
                    print(f"File {file.completeBaseName()} has been moved")

            FileSystem.files = files
        # File was deleted
        elif FileSystem.starting_count > updating_count:
            FileSystem.files = files

        return filesystem

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

        self.filesystem = FileSystem()

        self.thread = WorkerThread()
        self.thread.update_signal.connect(self.update_file_count)

        if not self.thread.isRunning():
            self.thread.start()

    def update_file_count(self, dir_filesystem):

        file_count = len(dir_filesystem['files'])
        dir_count = len(dir_filesystem['dirs'])

        print(f"Failu skaicius: {file_count}")
        print(f"Direktoriju skaicius: {dir_count}")


def main():
    app = QApplication([])

    window = Window()

    sys.exit(app.exec_())


main()
