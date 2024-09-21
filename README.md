# X-Live Updater

## Beschreibung der App

Die *X-Live Updater* App ist ein benutzerfreundliches Tray-Icon-Programm, das die Systemaktualisierungen für Systempakete, Flatpak (optional) und X-Live Apps überwacht. Wenn Updates verfügbar sind, wird eine Benachrichtigung angezeigt, und der Benutzer kann auswählen, welche Updates installiert werden sollen. Die App überprüft automatisch jede halbe Stunde nach Updates und bietet die Möglichkeit, diese manuell zu starten.

## Warnung

Bitte beachte, dass diese App erweiterte Berechtigungen benötigt, um `apt update` ohne Passworteingabe auszuführen. Das automatische Ausführen von Befehlen ohne Passwort birgt potenzielle Sicherheitsrisiken. Benutzer sind dafür verantwortlich, sicherzustellen, dass diese Implementierung für ihre Umgebung sicher ist.

## Anweisung zur Sudoers-Datei

Falls die erforderliche Sudoers-Datei für `apt update` nicht vorhanden ist, zeigt die App eine Nachricht an, die den folgenden Befehl vorschlägt:

```bash
echo "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd
