# X-Live Updater

## Beschreibung der App (Deutsch)

Die *X-Live Updater* App ist ein benutzerfreundliches Tray-Icon-Programm, das die Systemaktualisierungen für Systempakete und X-Live Apps überwacht. Wenn Updates verfügbar sind, wird eine Benachrichtigung angezeigt, und der Benutzer kann auswählen, welche Updates installiert werden sollen. Die App überprüft automatisch jede halbe Stunde nach Updates und bietet die Möglichkeit, diese manuell zu starten.

## Warnung

Bitte beachte, dass diese App erweiterte Berechtigungen benötigt, um `apt update` ohne Passworteingabe auszuführen. Das automatische Ausführen von Befehlen ohne Passwort birgt potenzielle Sicherheitsrisiken. Benutzer sind dafür verantwortlich, sicherzustellen, dass diese Implementierung für ihre Umgebung sicher ist.

## Anweisung zur Sudoers-Datei

Falls die erforderliche Sudoers-Datei für `apt update` nicht vorhanden ist, zeigt die App eine Nachricht an, die den folgenden Befehl vorschlägt:

```bash
echo "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd
```

---
# X-Live Updater

## App Description (English)

The X-Live Updater app is a user-friendly tray icon program that monitors system updates for system packages and X-Live Apps. When updates are available, a notification is displayed, allowing the user to choose which updates to install. The app automatically checks for updates every half hour and offers the option to trigger the check manually.

## Warning

Please note that this app requires elevated permissions to run apt update without a password. Automatically running commands without password prompts can pose potential security risks. Users are responsible for ensuring that this implementation is secure in their environment.

## Instructions for the Sudoers File

If the required Sudoers file for `apt update` is missing, the app will display a message suggesting the following command:

```bash
echo "ALL ALL=(ALL) NOPASSWD: /usr/bin/apt update" | sudo tee /etc/sudoers.d/99-apt-update-nopasswd

