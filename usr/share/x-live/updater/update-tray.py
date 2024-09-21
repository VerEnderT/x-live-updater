#!/usr/bin/python3

import sys
import os
import subprocess
import locale
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
import xupdates  # Modul für X-Live Apps
import xupdater  # Modul zum update installieren

arbeitsverzeichnis = os.path.expanduser('/usr/share/x-live/updater')
os.chdir(arbeitsverzeichnis)

# Übersetzungen für unterstützte Sprachen
translations = {
    'en': {'updates_available': 'updates available', 'no_updates': 'No updates available', 'check_for_updates': 'Check for updates', 'exit': 'Exit', 'flatpak_updates': 'Flatpak updates', 'system_updates': 'System package updates', 'xlive_updates': 'X-Live Apps updates', 'sudoers_missing': 'The Sudoers file for apt update is missing. Please run the following command to add it:\n\necho "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd'},
    'de': {'updates_available': 'Aktualisierungen verfügbar', 'no_updates': 'Keine Aktualisierungen verfügbar', 'check_for_updates': 'Auf Updates prüfen', 'exit': 'Beenden', 'flatpak_updates': 'Flatpak-Aktualisierungen', 'system_updates': 'Systempaket-Aktualisierungen', 'xlive_updates': 'X-Live Apps-Aktualisierungen', 'sudoers_missing': 'Die Sudoers-Datei für apt update fehlt. Bitte führen Sie den folgenden Befehl aus, um sie hinzuzufügen:\n\necho "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd'},
    'it': {'updates_available': 'aggiornamenti disponibili', 'no_updates': 'Nessun aggiornamento disponibile', 'check_for_updates': 'Controlla aggiornamenti', 'exit': 'Esci', 'flatpak_updates': 'Aggiornamenti Flatpak', 'system_updates': 'Aggiornamenti dei pacchetti di sistema', 'xlive_updates': 'Aggiornamenti X-Live Apps', 'sudoers_missing': 'Il file Sudoers per apt update manca. Si prega di eseguire il seguente comando per aggiungerlo:\n\necho "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd'},
    'es': {'updates_available': 'actualizaciones disponibles', 'no_updates': 'No hay actualizaciones disponibles', 'check_for_updates': 'Buscar actualizaciones', 'exit': 'Salir', 'flatpak_updates': 'Actualizaciones de Flatpak', 'system_updates': 'Actualizaciones de paquetes del sistema', 'xlive_updates': 'Actualizaciones de X-Live Apps', 'sudoers_missing': 'Falta el archivo Sudoers para apt update. Ejecute el siguiente comando para agregarlo:\n\necho "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd'},
    'fr': {'updates_available': 'mises à jour disponibles', 'no_updates': 'Pas de mises à jour disponibles', 'check_for_updates': 'Vérifier les mises à jour', 'exit': 'Quitter', 'flatpak_updates': 'Mises à jour Flatpak', 'system_updates': 'Mises à jour des paquets système', 'xlive_updates': 'Mises à jour des applications X-Live', 'sudoers_missing': 'Le fichier Sudoers pour apt update est manquant. Veuillez exécuter la commande suivante pour l\'ajouter:\n\necho "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd'}
}

class UpdateTrayApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.xupdater_app = None
        
        # Ermitteln der Systemsprache mit getlocale(), Standard auf Englisch setzen, falls nicht unterstützt
        lang_code = locale.getlocale()[0][:2] if locale.getlocale()[0] else 'en'
        self.language = translations.get(lang_code, translations['en'])

        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self)
        self.tray_icon.setToolTip(self.language['no_updates'])

        # Kontextmenü erstellen
        self.menu = QMenu()
        self.update_action = QAction(self.language['check_for_updates'])
        self.update_action.triggered.connect(self.check_for_updates)
        self.exit_action = QAction(self.language['exit'])
        self.exit_action.triggered.connect(self.exit)

        self.menu.addAction(self.update_action)
        self.menu.addAction(self.exit_action)
        self.tray_icon.setContextMenu(self.menu)

        self.tray_icon.activated.connect(self.tray_icon_clicked)
        self.tray_icon.show()

        # Überprüfe Sudoers-Datei beim Start
        self.check_and_notify_sudoers()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_updates)
        self.timer.start(1800000)
        self.check_for_updates()

    def check_for_updates(self):
        # Überprüfe APT-Updates
        self.apt_updates = self.check_apt_updates()
        num_apt_updates = len(self.apt_updates)

        # Überprüfe Flatpak-Updates (falls Flatpak installiert ist)
        self.flatpak_updates = self.check_flatpak_updates()
        num_flatpak_updates = len(self.flatpak_updates)

        # Überprüfe X-Live Apps-Updates
        self.xlive_updates = xupdates.update_check()
        num_xlive_updates = len(self.xlive_updates)

        # Tooltip basierend auf verfügbaren Updates dynamisch aktualisieren
        tooltip = ""
        if num_apt_updates > 0:
            tooltip += f"{num_apt_updates} {self.language['system_updates']}\n"
        if num_flatpak_updates > 0:
            tooltip += f"{num_flatpak_updates} {self.language['flatpak_updates']}\n"
        if num_xlive_updates > 0:
            tooltip += f"{num_xlive_updates} {self.language['xlive_updates']}"

        # Wenn keine Updates vorhanden sind, "Keine Aktualisierungen verfügbar" anzeigen
        if not tooltip.strip():
            self.tray_icon.setToolTip(self.language['no_updates'])
            self.tray_icon.setIcon(QIcon("icon.png"))
        else:
            self.tray_icon.setToolTip(tooltip.strip())  # Strip entfernt überflüssige Leerzeichen/Zeilenumbrüche
            self.tray_icon.setIcon(QIcon("icon_red.png"))
        

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

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Linksklick
            if self.xupdater_app == None:
                try:
                    self.check_for_updates()
                    if self.apt_updates or self.flatpak_updates or self.xlive_updates:
                        self.xupdater_app = xupdater.xupdater(self.apt_updates,self.flatpak_updates,self.xlive_updates)
                except Exception as e:
                    print(f"Error triggering update process: {e}")
                
            else:
                pass
                

    def check_and_notify_sudoers(self):
        sudoers_file = '/etc/sudoers.d/99-apt-update-nopasswd'

        # Prüfen, ob die Sudoers-Datei vorhanden ist
        if not os.path.exists(sudoers_file):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Sudoers File Missing")
            msg.setText(self.language['sudoers_missing'])
            msg.setStandardButtons(QMessageBox.Ok)
            retval = msg.exec_()

            # Programm nach Anzeige der Warnung beenden
            self.exit()

    def exit(self):
        self.tray_icon.hide()
        sys.exit()

if __name__ == '__main__':
    app = UpdateTrayApp(sys.argv)
    sys.exit(app.exec_())

