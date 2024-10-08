#!/usr/bin/python3

import sys
import os
import re
import subprocess
import xupdates
import urllib.request
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox, QTextEdit
from PyQt5.QtCore import QProcess, QTimer, Qt
from PyQt5.QtGui import QTextCursor, QIcon

arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/updater')
os.chdir(arbeitsverzeichnis)

class xupdater(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle("X-Live Software Updater ")
        self.setGeometry(100, 100, 400, 500)
        self.setMinimumWidth(450)
        icon = QIcon("./icon.png")
        self.setWindowIcon(icon)
        self.flag = True
        self.check_for_updates()
        apt_list = self.apt_list
        flat_list = self.flat_list
        xlive_list = self.xlive_list
        #------ > self.xlive_check()
        self.url_list,self.update_list = self.xlive_check()
        self.xlive_list = self.update_list

        self.layout = QVBoxLayout()
        info_txt = "Keine Updates vorhanden"
        if apt_list or flat_list or xlive_list:
            info_txt = "Aktuallisierungen" 
        if apt_list:
            if len(apt_list) <= 5:
                info_txt = info_txt + f"\n\n{str(len(apt_list))} Systempakete:" + "\n" + "\n".join(apt_list)
            else:
                info_txt = info_txt + f"\n\n{str(len(apt_list))} Systempakete:" + "\n" + "\n".join(apt_list[:5])+f"\n und {str(len(apt_list)-5)} weitere"
        
        if flat_list:
            if len(flat_list) <= 5:
                info_txt = info_txt + f"\n\n{str(len(flat_list))} FLatpak:" + "\n" + "\n".join(flat_list)
            else:
                info_txt = info_txt + f"\n\n{str(len(flat_list))} FLatpak:" + "\n" + "\n".join(flat_list[:5])+f"\n und {str(len(flat_list)-5)} weitere"
        
        
        if xlive_list:
            if len(xlive_list) <= 5:
                info_txt = info_txt + f"\n\n{str(len(xlive_list))} X-Live Apps:" + "\n" + "\n".join(xlive_list)
            else:
                info_txt = info_txt + f"\n\n{str(len(xlive_list))} X-Live Apps:" + "\n" + "\n".join(xlive_list[:5])+f"\n und {str(len(flat_list)-5)} weitere "
                

        # Label to display package information
        self.info_label = QLabel(info_txt, self)
        self.layout.addWidget(self.info_label)

        # Button to install the package
        self.install_button = QPushButton("Install Package", self)
        self.install_button.clicked.connect(self.start_install_packages)
        self.install_button.setEnabled(False)
        self.layout.addWidget(self.install_button)


        # Text area to show process output
        self.output_area = QTextEdit(self)
        self.output_area.setReadOnly(True)
        self.layout.addWidget(self.output_area)
        self.output_area.hide()
        
        self.setLayout(self.layout)

        
        self.background_color()
        self.adjustSize()
        self.show()
        self.process = None  
        self.install_button.setEnabled(False)
        if apt_list or flat_list or xlive_list:
            self.install_button.setEnabled(True)
        
    def start_install_packages(self):
        self.install_button.setEnabled(False)
        self.start_download(self.url_list)

    def install_packages(self):
        self.output_area.append("\nStarte Paket Installation...\n")
        self.output_area.moveCursor(QTextCursor.End)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.read_output)
        self.process.finished.connect(self.process_finished)
        
        # Prepare the command
        
        start_command = "apt update"       
        xlive_command = "apt install -y /tmp/x-live/debs/*.deb" 
        apt_command = "apt upgrade -y"
        
        command = ""
        #if apt_list or flat_list or xlive_list:
        if self.apt_list or self.xlive_list:
            command = start_command
            if self.xlive_list: 
                command = command + " && " + xlive_command
            if self.apt_list: 
                command = command + " && " + apt_command
                
        print(command)
             
        
        if self.apt_list or self.xlive_list:
            self.process.start('pkexec', ['sh', '-c', command])
        if self.flat_list: 
            self.process.start('flatpak', ['update', '-y'])

    def read_output(self):
        if self.process:
            output = self.process.readAll().data().decode()
            output = output.replace('\r\n', '\n').replace('\r', '\n')
            self.output_area.moveCursor(QTextCursor.End)
            self.output_area.insertPlainText(output)
            self.output_area.moveCursor(QTextCursor.End)

    def process_finished(self, exit_code, exit_status):
        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.output_area.append("\nInstallation erfolgreich beendet!")
            self.output_area.moveCursor(QTextCursor.End)
            QMessageBox.information(self, "Erfolg", "Installation erfolgreich beendet!")
        else:
            self.output_area.append("\nInstallation fehlgeschlagen.")
            self.output_area.moveCursor(QTextCursor.End)
            QMessageBox.critical(self, "Fehler", "Installation Fehlgeschlagen.")
     


    def xlive_check(self):
        author = "verendert"
        repos = self.xlive_list
        update_list = []
        url_list = {}
        for package in repos:
            try:
                test = xupdates.update_info(author, package)
                if test["update"] == "u":
                    update_list.append(package)
                    url_list[package]=test['url']
                    #print(test)

            except Exception as e:
                fehler = str(e).split(":")[-1]
                print(f"Fehler: {fehler}")

        return url_list,update_list

    # downloader

    def start_download(self, packages):
        os.system("rm /tmp/x-live/debs/*")
        self.output_area.show()
        self.adjustSize()
        if packages:
            self.packages = packages
            self.download_next_package()
        else:
            self.output_area.append("No X-Live packages to download.")
            QTimer.singleShot(1000, self.install_packages) 

    def download_next_package(self):
        if self.packages:
            self.current_package, url = self.packages.popitem()
            package_filename = f"{self.current_package}.deb"
            self.output_area.append(f"Start downloading: {package_filename}")
            save_directory = '/tmp/x-live/debs/'

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            self.filename = os.path.join(save_directory, package_filename)

            if not self.process:
                self.process = QProcess(self)

            # Setup QProcess for wget command
            self.process.setProgram('wget')
            self.process.setArguments(['--progress=bar:force', '-O', self.filename, url])
            self.process.setWorkingDirectory(save_directory)
            self.process.setProcessChannelMode(QProcess.MergedChannels)
            self.process.readyRead.connect(self.read_output)
            self.process.finished.connect(self.handle_finished)
            self.process.start()
        else:
            if self.flag:            
                self.flag = False                
                self.output_area.append("All downloads finished.")
                QTimer.singleShot(1000, self.install_packages) 

    def handle_finished(self):
        self.output_area.append(f"Finished downloading: {self.filename}")
        QTimer.singleShot(1000, self.download_next_package)


       
    # Farbprofil abrufen und anwenden

    def get_current_theme(self):
        try:
            # Versuche, das Theme mit xfconf-query abzurufen
            result = subprocess.run(['xfconf-query', '-c', 'xsettings', '-p', '/Net/ThemeName'], capture_output=True, text=True)
            theme_name = result.stdout.strip()
            if theme_name:
                return theme_name
        except FileNotFoundError:
            print("xfconf-query nicht gefunden. Versuche gsettings.")
        except Exception as e:
            print(f"Error getting theme with xfconf-query: {e}")

        try:
            # Fallback auf gsettings, falls xfconf-query nicht vorhanden ist
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'gtk-theme'], capture_output=True, text=True)
            theme_name = result.stdout.strip().strip("'")
            if theme_name:
                return theme_name
        except Exception as e:
            print(f"Error getting theme with gsettings: {e}")

        return None

    def extract_color_from_css(self,css_file_path, color_name):
        try:
            with open(css_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                #print(content)
                # Muster zum Finden der Farbe
                pattern = r'{}[\s:]+([#\w]+)'.format(re.escape(color_name))
                match = re.search(pattern, content)
                if match:
                    return match.group(1)
                return None
        except IOError as e:
            print(f"Error reading file: {e}")
            return None
            
            
    def background_color(self):
        theme_name = self.get_current_theme()
        if theme_name:
            print(f"Current theme: {theme_name}")

            # Pfad zur GTK-CSS-Datei des aktuellen Themes
            css_file_path = f'/usr/share/themes/{theme_name}/gtk-3.0/gtk.css'
            if os.path.exists(css_file_path):
                bcolor = self.extract_color_from_css(css_file_path, ' background-color')
                color = self.extract_color_from_css(css_file_path, ' color')
                self.setStyleSheet(f"background: {bcolor};color: {color}")
            else:
                print(f"CSS file not found: {css_file_path}")
        else:
            print("Unable to determine the current theme.")






    def check_for_updates(self):
        # Überprüfe APT-Updates
        self.apt_list = self.check_apt_updates()
    
        # Überprüfe Flatpak-Updates (falls Flatpak installiert ist)
        self.flat_list = self.check_flatpak_updates()

        # Überprüfe X-Live Apps-Updates
        self.xlive_list = xupdates.update_check()

        return

    def check_apt_updates(self):
        try:
            # Zuerst sudo apt update ausführen, um die Paketlisten zu aktualisieren
            subprocess.run(['sudo', 'apt', 'update'], check=False)

            # Setze die Umgebungsvariable für englische Ausgabe für apt-get
            env = {'LC_ALL': 'C', **os.environ}

            # Führe den apt-get-Befehl aus, um nach aktualisierbaren Paketen zu suchen
            result = subprocess.run(['apt-get', '-s', 'upgrade'], stdout=subprocess.PIPE, text=True, env=env)
            
            # Filtere die Ausgabe, um aktualisierbare Pakete zu finden
            updates = [line.split()[1] for line in result.stdout.split('\n') if 'Conf' in line]
            #print(f"Updates:\n{updates}")            

            return updates
        except Exception as e:
            print(f"Error checking APT updates: {e}")
            return []
    
    def check_flatpak_updates(self):
        try:
            # Überprüfen, ob Flatpak installiert ist
            if subprocess.run(['which', 'flatpak'], stdout=subprocess.PIPE).returncode != 0:
                print("Flatpak is not installed.")
                return []

            # Führe den Befehl aus, um nach Flatpak-Updates zu suchen
            result = subprocess.run(['flatpak', 'remote-ls', '--updates'], stdout=subprocess.PIPE, text=True)
            updates = result.stdout.strip().split('\n')
            #print(f"Flatpak Updates:\n{updates}")
            
            # Berechne die Anzahl der Flatpak-Updates (leerzeilen ignorieren)
            flatpak_updates = [line.split("\t")[0] for line in updates if line]
            return flatpak_updates

        except Exception as e:
            print(f"Error checking Flatpak updates: {e}")
            return []
            
    def open_widget(self):
        print(self.apt_list,self.flat_list,self.xlive_list)
        app = QApplication(sys.argv)
        xupdater(self.apt_list,self.flat_list,self.xlive_list)
        sys.exit(app.exec_())
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_update = xupdater()
    start_update.show()
    sys.exit(app.exec_())