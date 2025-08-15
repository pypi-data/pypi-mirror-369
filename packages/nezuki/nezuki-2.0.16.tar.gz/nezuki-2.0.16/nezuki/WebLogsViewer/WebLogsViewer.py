from time import sleep
from flask import Flask, Blueprint, send_from_directory, jsonify, request, abort
from flask_cors import CORS  # Importa Flask-CORS
import os
import json
from datetime import datetime
import re

app = Flask(__name__, static_folder='../templates/log-viewer/build', static_url_path='/')
CORS(app)  # Abilita CORS per tutte le route

log_path = "./logs"
config_file = "registered_bots.json"
current_version = "2.0.9"

class BotManager:
    def __init__(self, config_file, log_path):
        self.config_file = config_file
        self.log_path = log_path
        self.registered_bots = self.load_registered_bots()

    def load_registered_bots(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_registered_bots(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.registered_bots, f)

    def register_bot(self, bot_username, log_dir):
        self.registered_bots[bot_username] = {
            "log_dir": log_dir,
            "active": True  # Imposta il bot come attivo durante la registrazione
        }
        self.save_registered_bots()

    def remove_bot(self, bot_username):
        if bot_username in self.registered_bots:
            self.registered_bots[bot_username]['active'] = False
            self.save_registered_bots()

    def get_active_bots(self):
        registered_bots = self.load_registered_bots()  # Ricarica i bot registrati dal file
        active_bots_info = []
        for bot_username, info in registered_bots.items():
            active_bots_info.append({
                "username": bot_username,
                "active": info.get("active", False)
            })
        return active_bots_info

    def get_logs(self, bot_username, page=1, limit=50, logLevel=None, searchText=None, excludeInternal=False):
        print("Mostri nuovi log...", page, limit, logLevel, searchText)
        bot_info = self.registered_bots.get(bot_username)
        if not bot_info:
            return None

        bot_log_path = bot_info.get('log_dir')
        log_files = [f for f in os.listdir(bot_log_path) if f.endswith('.log') and "bot_log_size" in f]
        logs = []

        log_regex = re.compile(
            r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \|\| '  # Date
            r'(?P<level>\w+) \|\| '  # Level
            r'(?:(?P<internal>True|False) \|\| )?'  # Internal (opzionale)
            r'(?:(?P<versionLog>\d\.\d\.\d) \|\| )?'  # VersionLog (opzionale)
            r'(?P<esito_funzionale>-?\d+|HTTP\s\d{3}|[\w\s]+) \|\| '  # EsitoFunzionale
            r'(?P<class>[\w_]+) \|\| '  # NomeClasse
            r'(?P<function>\w+) \|\| '  # NomeFunzione
            r'(?P<logID>[a-f0-9\-]+|No LogID) \|\| '  # LogID
            r'(?P<message>.+?)'  # Messaggio (non greedy)
            r'(?: \|\| (?P<details>.*))?$'  # Dettagli opzionali
        )

        # Mappatura dei livelli di log in ordine gerarchico
        log_levels_hierarchy = ['debug', 'info', 'warning', 'error', 'critical']

        for log_file in log_files:
            absolute_path = os.path.abspath(os.path.join(bot_log_path, log_file))
            with open(absolute_path, 'r') as f:
                for line in f:
                    match = log_regex.match(line)
                    if match:
                        log_data = match.groupdict()
                        log_data["file"] = absolute_path
                        log_data['vparser'] = current_version

                        # Filtro per escludere log interni se richiesto
                        if excludeInternal and log_data.get('internal') == 'True':
                            continue
                            
                        # Filtro per livello di log in base alla gerarchia
                        if logLevel:
                            log_level_index = log_levels_hierarchy.index(log_data["level"].lower())
                            filter_level_index = log_levels_hierarchy.index(logLevel.lower())
                            
                            # Salta i log che hanno un livello inferiore al livello selezionato
                            if log_level_index < filter_level_index:
                                continue

                        # Filtro per testo di ricerca
                        if searchText and searchText.lower() not in json.dumps(log_data).lower():
                            continue

                        logs.append(log_data)

        logs.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d %H:%M:%S,%f'), reverse=True)
        
        # Implementa la paginazione
        start = (page - 1) * limit
        end = start + limit
        paginated_logs = logs[start:end]
        
        print("Ritorno log")
        return paginated_logs, len(logs)

# Istanza di BotManager
bot_manager = BotManager(config_file=config_file, log_path=log_path)

bots_blueprint = Blueprint('bots', __name__)

@bots_blueprint.route('/<bot_username>', methods=['GET'])
def bot_home(bot_username):
    return send_from_directory(app.static_folder, 'index.html')

@bots_blueprint.route('/<bot_username>/logs', methods=['GET'])
def logs(bot_username):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    logLevel = request.args.get('logLevel', None)
    searchText = request.args.get('searchText', None)
    excludeInternal = request.args.get('excludeInternal', 'false').lower() == 'true'

    logs, total_logs = bot_manager.get_logs(bot_username, page, limit, logLevel, searchText, excludeInternal)

    print({
        "total_logs": total_logs,
        "logs": len(logs),
        "version": current_version
    })
    return jsonify({
        "logs": logs,
        "total_logs": total_logs,
        "version": current_version
    })

app.register_blueprint(bots_blueprint, url_prefix='/bots')

@app.route('/register', methods=['POST'])
def register_bot():
    try:
        bot_username = request.form['bot_username']
        log_dir = request.form['log_dir']
        bot_manager.register_bot(bot_username, log_dir)
        return "Bot registered successfully", 200
    except Exception as e:
        app.logger.error(f"Error registering bot {bot_username}: {str(e)}")
        return f"Failed to register bot: {str(e)}", 500
    
@app.route('/bots/list', methods=['GET'])
def bots_list():
    try:
        active_bots = bot_manager.get_active_bots()
        return jsonify({"active_bots": active_bots})
    except Exception as e:
        app.logger.error(f"Error retrieving bot list: {str(e)}")
        return f"Failed to retrieve bot list: {str(e)}", 500

@app.route('/remove', methods=['POST'])
def remove_bot():
    try:
        bot_username = request.form['bot_username']
        bot_manager.remove_bot(bot_username)
        return "Bot deactivated successfully", 200
    except Exception as e:
        app.logger.error(f"Error deactivating bot {bot_username}: {str(e)}")
        return f"Failed to deactivate bot: {str(e)}", 500

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/version', methods=['GET'])
def get_version():
    return jsonify({
        "version": current_version
    })

if __name__ == '__main__':
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    app.run(host='0.0.0.0', port=7080)