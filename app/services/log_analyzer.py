from datetime import datetime, timezone
from app.extensions import db
from app.models import Alert, IPRegistry
from app.services.data_manager import DataManager

class LogAnalyzer:
    """
    Serce systemu SIEM. Analizuje pliki logów przy użyciu Pandas
    i generuje alerty w bazie danych.
    """

    @staticmethod
    def analyze_parquet(filename, host_id):
        """
        Główna funkcja analityczna.
        """
        # 1. Wczytanie danych (To masz gotowe)
        df = DataManager.load_logs(filename)
        
        if df.empty:
            return 0 
            
        # Zabezpieczenie przed brakiem kolumn
        if 'alert_type' not in df.columns or 'source_ip' not in df.columns:
            return 0

        # 2. Filtrowanie: Interesują nas tylko ataki
        attack_pattern = ['FAILED_LOGIN', 'INVALID_USER', 'WIN_FAILED_LOGIN']
        threats = df[df['alert_type'].isin(attack_pattern)]
        
        if threats.empty:
            return 0

        alerts_created = 0
        
        # 3. Iteracja po zagrożeniach
        for index, row in threats.iterrows():
            ip = row['source_ip']
            user = row.get('user', 'unknown')
            
            # Ignorujemy lokalne
            #if ip in ['LOCAL', 'LOCAL_CONSOLE', '127.0.0.1', '::1']:
                #continue

            # =======================================================
            # TODO: ZADANIE 3 - LOGIKA SIEM (THREAT INTELLIGENCE)
            # =======================================================
            
            # Twoim zadaniem jest ocena powagi incydentu w oparciu o bazę IPRegistry.
            
            # 1. Sprawdź, czy adres IP (zmienna 'ip') znajduje się w tabeli IPRegistry.
            ip_entry = IPRegistry.query.filter_by(ip_address=ip).first()

            severity = 'WARNING'
            message = f"ALERT - Wykryto nieudane logowanie z IP ({ip})"
            
            # 2. Jeśli NIE MA go w bazie -> Dodaj go ze statusem 'UNKNOWN' i obecnym czasem (last_seen).
            if not ip_entry:
                ip_entry = IPRegistry(
                    ip_address = ip,
                    status = 'UNKNOWN',
                    last_seen = datetime.now(timezone.utc)
                )
                db.session.add(ip_entry)
            # 3. Jeśli JEST w bazie -> Zaktualizuj mu last_seen.
            else:
                ip_entry.last_seen = datetime.now(timezone.utc)
            # 4. Ustal poziom alertu (severity) i treść wiadomości (message):
            #    - Domyślny poziom: 'WARNING'.

            # Automatyczne banowanie (Multi-host attack)
            if ip_entry.status == 'UNKNOWN':
                from datetime import timedelta
                ten_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
                
                # Sprawdzamy, czy ten IP atakował inne hosty w ciągu ostatnich 10 min
                other_hosts_attacked = Alert.query.filter(
                    Alert.source_ip == ip,
                    Alert.host_id != host_id,
                    Alert.timestamp >= ten_minutes_ago
                ).count()


                if other_hosts_attacked > 0:
                    ip_entry.status = 'BANNED'
            #    - Jeśli IP ma status 'BANNED' -> Zmień poziom na 'CRITICAL' i dopisz to w treści.
                if ip_entry.status == 'BANNED':
                    severity = 'CRITICAL'
                    message = f"ALERT KRYTYCZNY - Próba logowania ze zbanowanego IP ({ip})"
            
            #    - Jeśli IP ma status 'TRUSTED' -> Możesz pominąć alert (continue) lub ustawić 'INFO'.
                elif ip_entry.status == 'TRUSTED':
                    #continue
                    severity = 'INFO'
                    message = f"Błąd przy próbie logowania z zaufanego IP: ({ip})"
            
            # 5. Stwórz obiekt Alert:
            new_alert = Alert(
                host_id  =host_id,
                timestamp=row['timestamp'],
                alert_type = row['alert_type'],
                message = message,
                severity = severity,
                source_ip = ip
            )
            
            # 6. Dodaj do sesji (db.session.add) i zwiększ licznik alerts_created.
            db.session.add(new_alert)
            alerts_created += 1

        # Zatwierdzenie zmian w bazie
        db.session.commit()
        return alerts_created