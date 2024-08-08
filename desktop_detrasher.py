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
    global file_list, file_count


    recent_files = "Recent Files/"

    date = date.today().strftime("%Y-%m-%d")
    directory = QDir(DESKTOP_PATH)
    files = directory.entryInfoList()

    starting_count = len(files)

    # if len(file_list) < 2:
    #     file_list = files

    # if file_count[-1] != len(files):
    #     file_count.append(len(files))

    #     # get different file
    #     for file in files:
    #         if file not in file_list:
    #             new_file = file

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
                    print(file.absoluteFilePath())
            print(True)
        # File was deleted
        elif FileSystem.starting_count > updating_count:
            pass

        return len(files)

    @staticmethod
    def move_file(new_file_list):
        pass

    @staticmethod
    def get_file_group_count():
        groups = FileSystem.manageFiles()
        file_count = len(groups["files"])
        dir_count = len(groups["dirs"])

        return {"files": file_count, "dirs": dir_count}


class WorkerThread(QThread):
    update_signal = pyqtSignal(int)

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
        pass
        # print(dir_filesystem)
        # print(f"Failu skaicius: {dir_filesystem['files']}")
        # print(f"Direktoriju skaicius: {dir_filesystem['dirs']}")


def main():
    app = QApplication([])

    window = Window()

    sys.exit(app.exec_())


main()
