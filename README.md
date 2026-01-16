# 🛡️ mini-SIEM (Security Information & Event Management)

Projekt autorskiego systemu klasy **SIEM** przeznaczonego do monitorowania bezpieczeństwa infrastruktury IT, centralizacji logów systemowych oraz automatycznej detekcji incydentów w czasie rzeczywistym. System oparty jest na architekturze **Klient-Serwer** z wykorzystaniem frameworka Flask oraz nowoczesnego stacku Data Engineering.



## 🚀 Kluczowe Funkcjonalności

* **Asset Management:** Centralny rejestr monitorowanych hostów (Windows/Linux) z funkcją Health-Check (CPU, RAM, HDD).
* **Data Lake (Retention):** Składowanie surowych logów w wysokowydajnym formacie kolumnowym **Apache Parquet** dla celów informatyki śledczej (forensics).
* **Threat Intelligence Engine:** Silnik korelujący przychodzące logi z bazą reputacji adresów IP (IOC).
* **Incremental Fetch:** Inteligentny mechanizm pobierania przyrostowego, który optymalizuje ruch sieciowy dzięki śledzeniu znacznika `last_fetch` dla każdego hosta.
* **Security Hardening:** System posiada zaimplementowane bezpieczne uwierzytelnianie (hash + salt) oraz kontrolę dostępu do API (IAM).

## 🛠 Stos Technologiczny

* **Backend:** Python 3.x, Flask
* **Baza danych:** SQLite (Relacyjna), Apache Parquet (Storage)
* **Komunikacja:** SSH (Paramiko), PowerShell/WMI
* **Frontend:** Vanilla JS, Bootstrap 5

## 📂 Struktura Projektu

```text
├── app/
│   ├── blueprints/
│   │   ├── api/          # REST API dla danych SIEM
│   │   ├── auth.py       # Zarządzanie dostępem (IAM)
│   │   └── ui.py         # Interfejs Dashboardu
│   ├── services/
│   │   ├── log_collector.py  # Kolektor i parser logów (Regex/XML)
│   │   ├── log_analyzer.py   # Silnik korelacji i Threat Intel
│   │   └── data_manager.py   # Obsługa warstwy Parquet
│   └── models.py         # Modele bazy danych (Users, Hosts, Alerts)
├── config.py             # Konfiguracja środowiska
└── requirements.txt      # Zależności bibliotek

```
## ⚙️ Instalacja i Uruchomienie

### 1. Przygotowanie środowiska
Zaleca się użycie wirtualnego środowiska Pythona, aby odizolować zależności projektu:

```bash
# Tworzenie wirtualnego środowiska
python -m venv venv

# Aktywacja - Linux/macOS
source venv/bin/activate  

# Aktywacja - Windows
.\venv\Scripts\activate   

# Instalacja wymaganych bibliotek
pip install -r requirements.txt
```
### 2. Konfiguracja bazy danych
Zainicjuj strukturę tabel w lokalnej bazie danych SQLite:


```bash
flask shell
```
```python
from app.extensions import db
db.create_all()
exit()
```
### 3. Tworzenie konta administratora
Ponieważ system jest zamknięty, pierwszego użytkownika (administratora) należy dodać ręcznie z poziomu konsoli:

```bash
flask shell
Python
from app.models import User
from app.extensions import db

admin = User(username="admin")
admin.set_password("TwojeTajneHaslo") # Metoda haszująca z models.py
db.session.add(admin)
db.session.commit()
exit()
```

### 4. Uruchomienie aplikacji
Po skonfigurowaniu bazy możesz uruchomić serwer deweloperski:

```bash
flask 
```
Domyślnie system dostępny jest pod adresem: http://127.0.0.1:5000

