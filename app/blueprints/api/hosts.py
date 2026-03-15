from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from datetime import timezone, datetime

from app.models import Host, LogSource, LogArchive, Alert, IPRegistry, Host
from app.services.remote_client import RemoteClient
from app.services.win_client import WinClient
from app.services.log_collector import LogCollector
from app.services.data_manager import DataManager
from app.services.log_analyzer import LogAnalyzer
from app.extensions import db


api_bp = Blueprint("api_hosts", __name__)

#crud hosts (ready)

@api_bp.route("/hosts", methods=["GET"])
@login_required
def get_hosts():
    hosts = Host.query.all()
    return jsonify([h.to_dict() for h in hosts])

@api_bp.route("/hosts", methods=["POST"])
@login_required
def add_host():
    data = request.get_json()
    if not data: return jsonify({"error": "Brak danych"}), 400
    if Host.query.filter_by(ip_address=data.get("ip_address")).first():
        return jsonify({"error": "IP musi być unikalne"}), 409
    new_host = Host(hostname=data.get("hostname"), ip_address=data.get("ip_address"), os_type=data.get("os_type"))
    db.session.add(new_host)
    db.session.commit()
    return jsonify(new_host.to_dict()), 201

@api_bp.route("/hosts/<int:host_id>", methods=["DELETE"])
@login_required
def delete_host(host_id):
    host = Host.query.get_or_404(host_id)
    db.session.delete(host)
    db.session.commit()
    return jsonify({"message": "Usunięto hosta"}), 200

@api_bp.route("/hosts/<int:host_id>", methods=["PUT"])
@login_required
def update_host(host_id):
    host = Host.query.get_or_404(host_id)
    data = request.get_json()
    if 'hostname' in data: host.hostname = data['hostname']
    if 'ip_address' in data: host.ip_address = data['ip_address']
    if 'os_type' in data: host.os_type = data['os_type']
    db.session.commit()
    return jsonify(host.to_dict()), 200

#live monitoring (ready)

@api_bp.route("/hosts/<int:host_id>/ssh-info", methods=["GET"])
@login_required
def get_ssh_info(host_id):
    host = Host.query.get_or_404(host_id)
    ssh_user = current_app.config.get("SSH_DEFAULT_USER", "vagrant")
    ssh_port = current_app.config.get("SSH_DEFAULT_PORT", 2222)
    ssh_key = current_app.config.get("SSH_KEY_FILE")

    ssh_pass = current_app.config.get("SSH_PASSWORD")
    try:
        with RemoteClient(host=host.ip_address, user=ssh_user, port=ssh_port, key_file=ssh_key, password=ssh_pass) as remote:
            ram_out, _ = remote.run("free -m | grep Mem | awk '{print $7}'")
            disk_percentage, _ = remote.run("df -h | grep '/$' | awk '{print $5}'")
            if not disk_percentage: disk_percentage, _ = remote.run("df -h | grep '/dev/sda1' | awk '{print $5}'")
            disk_total, _ = remote.run("df -h | grep '/dev/sda1' | awk '{print $2}'")
            cpu_load, _ = remote.run("uptime | awk -F'load average:' '{ print $2 }' | cut -d',' -f1")
            uptime_seconds_str, _ = remote.run("cat /proc/uptime | awk '{print $1}'")
            uptime_formatted = "N/A"
            try:
                total_seconds = float(uptime_seconds_str)
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                uptime_formatted = f"{hours}h {minutes}m"
            except: pass

            return jsonify({
                "free_ram_mb": ram_out.strip(), "disk_info": disk_percentage.strip(),
                "disk_total": disk_total.strip(), "cpu_load": cpu_load.strip(), "uptime_hours": uptime_formatted
            }), 200
    except Exception as e:
        return jsonify({"error": f"Błąd połączenia: {str(e)}"}), 500

@api_bp.route("/hosts/<int:host_id>/windows-info", methods=["GET"])
@login_required
def get_windows_info(host_id):
    import psutil
    host = Host.query.get_or_404(host_id)
    if host.os_type != "WINDOWS": return jsonify({"error": "Wrong OS"}), 400
    try:
        mem = psutil.virtual_memory()
        free_ram_mb = str(round(mem.available / (1024 * 1024)))
        cpu_load = f"{psutil.cpu_percent(interval=0.1)}%"
        try:
            usage = psutil.disk_usage("C:\\")
            disk_percentage = f"{usage.percent}%"
            disk_total = f"{round(usage.total / (1024**3), 1)}GB"
        except:
            disk_percentage, disk_total = "N/A", "?"
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return jsonify({
            "free_ram_mb": free_ram_mb, "disk_info": disk_percentage,
            "disk_total": disk_total, "cpu_load": cpu_load, "uptime_hours": f"{hours}h {minutes}m"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#(to do) log collection and etl pipeline
@api_bp.route("/hosts/<int:host_id>/logs", methods=["POST"])
@login_required
def fetch_logs(host_id):
    host = Host.query.get_or_404(host_id)
    
    #get or create log source
    log_source = LogSource.query.filter_by(host_id=host.id).first()
    if not log_source:
        log_source = LogSource(host_id=host.id, log_type='security', last_fetch=None)
        db.session.add(log_source)
        db.session.commit()
    
    fetch_start_time = log_source.last_fetch 

    logs = []
    try:
        #fetch logs based on os type
        if host.os_type == "LINUX":
            ssh_user = current_app.config.get("SSH_DEFAULT_USER", "vagrant")
            ssh_port = current_app.config.get("SSH_DEFAULT_PORT", 2222)
            ssh_key = current_app.config.get("SSH_KEY_FILE")
            ssh_pass = current_app.config.get("SSH_PASSWORD")
            
            #init remote client and fetch logs
            with RemoteClient(host=host.ip_address, user=ssh_user, port=ssh_port, key_file=ssh_key, password=ssh_pass) as client:
                logs = LogCollector.get_linux_logs(client, last_fetch_time=fetch_start_time)
        
        elif host.os_type == "WINDOWS":
            #fetch windows logs locally
            with WinClient() as client:
                logs = LogCollector.get_windows_logs(client, last_fetch_time=fetch_start_time)

        if not logs:
            return jsonify({"message": "Brak nowych logów do pobrania", "alerts": 0}), 200  
        
        #save to parquet and get record count
        filename, log_count = DataManager.save_logs_to_parquet(logs, host.id)

        #update last fetch timestamp
        log_source.last_fetch = datetime.now(timezone.utc)

        #create archive record
        archive = LogArchive(
            host_id=host.id,
            filename=filename, 
            record_count = log_count
        )
        db.session.add(archive)

        #run threat analysis
        alerts_found = LogAnalyzer.analyze_parquet(filename, host.id)

        db.session.commit()

        return jsonify({
            "message": f"Pobrano {len(logs)} logów",
            "alerts": alerts_found,
            "archive_file": filename
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Błąd procesu ETL: {str(e)}"}), 500
    


#(to do) threat intelligence and alerts api
@api_bp.route("/ips", methods=["GET"])
@login_required
def get_ips():
    #get all registered ips
    ips = IPRegistry.query.order_by(IPRegistry.last_seen.desc()).all()
    return jsonify([ip.to_dict() for ip in ips]) 

@api_bp.route("/ips", methods=["POST"]) 
@login_required
def add_ip():
    #manually add ip to registry
    data = request.get_json()
    if not data or 'ip_address' not in data:
        return jsonify({"error": "Brak adresu IP"}), 400
    
    new_ip = IPRegistry(
        ip_address=data['ip_address'],
        status=data.get('status', 'unknown'),
    )
    db.session.add(new_ip)
    db.session.commit()
    return jsonify(new_ip.to_dict()), 201

@api_bp.route("/ips/<int:ip_id>", methods=["PUT"])
@login_required
def update_ip(ip_id):
    #update ip status entry
    ip_entry = IPRegistry.query.get_or_404(ip_id)
    data = request.get_json()
    if 'status' in data: ip_entry.status = data['status']
    
    db.session.commit()
    return jsonify(ip_entry.to_dict()), 200 

@api_bp.route("/ips/<int:ip_id>", methods=["DELETE"])
@login_required
def delete_ip(ip_id):
    #remove ip from registry
    ip_entry = IPRegistry.query.get_or_404(ip_id)
    db.session.delete(ip_entry)
    db.session.commit()
    return jsonify({"message": "Usunięto wpis z rejestru IP"}), 200  

@api_bp.route("/alerts", methods=["GET"])
@login_required
def get_recent_alerts():
    #latest 20 security alerts
    alerts = db.session.query(Alert, Host).join(Host).order_by(Alert.timestamp.desc()).limit(20).all()
    output = []
    for alert, host in alerts:
        a_dict = alert.to_dict()
        a_dict['hostname'] = host.hostname
        output.append(a_dict)
    return jsonify(output), 200