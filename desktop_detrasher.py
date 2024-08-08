import sys
import os
import time
import shutil

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QApplication, QPushButton, QMessageBox, QFileSystemModel, QTreeView
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDir

from datetime import date

DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

PARENT_DIR_NAME = "Recent Files"
PARENT_DIR_PATH = f"{DESKTOP_PATH}/{PARENT_DIR_NAME}/"

class FileSystem():

    target_dir = QDir(DESKTOP_PATH)
    target_dir.mkdir(PARENT_DIR_NAME)

    files_on_init = target_dir.entryInfoList()
    file_count_on_init = len(files_on_init)

    parent_dir = QDir(PARENT_DIR_PATH)

    @staticmethod
    def manageFiles():

        # updating file info
        target_dir = QDir(DESKTOP_PATH)
        files = target_dir.entryInfoList()

        # Track file groups
        filesystem = {"files": [], "dirs": [], "new_file": None}

        for entity in files:
            if entity.isFile():
                filesystem["files"].append(entity)
            elif entity.isDir():
                filesystem["dirs"].append(entity)
            else:
                raise ValueError("Neither a file nor a directory")

        new_file = FileSystem.get_new_file(files)

        if new_file is not None:
            # Used to display message to user
            filesystem["new_file"] = new_file.completeBaseName()
            
            FileSystem.move_file(new_file)

        return filesystem

    @staticmethod
    def get_new_file(files):
        updating_count = len(files)

        # File was created
        if FileSystem.file_count_on_init < updating_count:
            for file in files:
                if file not in FileSystem.files_on_init:
                    return file
        # File was deleted
        elif FileSystem.file_count_on_init > updating_count:
            FileSystem.files_on_init = files

    @staticmethod
    def move_file(new_file):
        dir = FileSystem.parent_dir
        
        today = date.today().strftime("%Y-%m-%d")
        today_dir = f"{dir.absolutePath()}/{today}/"

        # Suffix needed to move file
        if new_file.isFile():
            file_name = f"{new_file.completeBaseName()}.{new_file.suffix()}"
        elif new_file.isDir():
            file_name = new_file.completeBaseName()

        file_path = f"{new_file.absolutePath()}/{file_name}"

        if not dir.exists(today):
            dir.mkdir(today)

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
        self.resize(500, 400)
        
        # Conversion to str for label display
        file_count = str(len(FileSystem.manageFiles()['files']))
        dir_count = str(len(FileSystem.manageFiles()['dirs']))

        self.file_label = QLabel(self.window)
        self.file_label.setText(f"Failu skaicius: {file_count}")

        self.dir_label = QLabel(self.window)
        self.dir_label.setText(f"Direktoriju skaicius: {dir_count}")

        self.mbox = QMessageBox()

        self.model = QFileSystemModel(self.window)
        self.model.setRootPath("")

        self.tree = QTreeView(self.window)
        self.tree.setModel(self.model)

        self.vbox = QVBoxLayout(self.window)

        self.vbox.addWidget(self.tree)
        self.vbox.addWidget(self.file_label)
        self.vbox.addWidget(self.dir_label)

    def update_file_count(self, dir_filesystem):

        for i in self.tree.selectedIndexes():
            print(i.data())

        file_count = str(len(dir_filesystem['files']))
        dir_count = str(len(dir_filesystem['dirs']))

        self.file_label.setText(f"Failu skaicius: {file_count}")
        self.dir_label.setText(f"Direktoriju skaicius: {dir_count}")

        # New file was created
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
