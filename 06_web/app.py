from routes.hall import hall_bp
from routes.compare import compare_bp
from routes.api import api_bp
from routes.search import search_bp
from flask import Flask

from routes.dashboard import dashboard_bp
from routes.machine import machine_bp

app = Flask(__name__)

app.register_blueprint(dashboard_bp)
app.register_blueprint(machine_bp)
app.register_blueprint(search_bp)
app.register_blueprint(api_bp)
app.register_blueprint(compare_bp)
app.register_blueprint(hall_bp)

if __name__ == "__main__":
    app.run(debug=True)