"""
Display Pattern: Flask-Based Web Control Panel

Demonstrates running a Flask web server alongside a GStreamer pipeline.
Video displays via GStreamer/OpenCV window (low latency), while the
web UI provides a control panel for adjusting parameters remotely.

Key principle: NEVER stream video over the web — use GStreamer for video
display and web UI only for controls (sliders, buttons, settings).

Usage:
    source setup_env.sh
    python web_ui_example.py --input usb
    # Open http://localhost:8080 in a browser for the control panel
"""
import threading

from flask import Flask, jsonify, request, render_template_string


# ------------------------------------------------------------------------------
# Shared state between pipeline callback and web server
# ------------------------------------------------------------------------------
class AppState:
    """Thread-safe shared state."""
    def __init__(self):
        self.threshold = 0.5
        self.target_labels = ["person"]
        self.count = 0
        self.fps = 0.0
        self.alert_active = False
        self.lock = threading.Lock()


app_state = AppState()


# ------------------------------------------------------------------------------
# Flask web app (runs in background daemon thread)
# ------------------------------------------------------------------------------
flask_app = Flask(__name__)

CONTROL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hailo App Control Panel</title>
    <style>
        body { font-family: sans-serif; max-width: 600px; margin: 40px auto; padding: 0 20px; }
        .card { background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 15px 0; }
        .status { font-size: 1.2em; }
        .alert { background: #ffcccc; border: 2px solid #cc0000; }
        .normal { background: #ccffcc; border: 2px solid #00cc00; }
        input[type=range] { width: 100%; margin: 10px 0; }
        label { font-weight: bold; }
        button { padding: 8px 16px; margin: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>Hailo App Control Panel</h1>

    <div class="card" id="status-card">
        <div class="status">Loading...</div>
    </div>

    <div class="card">
        <label>Confidence Threshold: <span id="thresh-val">0.5</span></label>
        <input type="range" min="0" max="100" value="50" id="threshold"
               oninput="updateThreshold(this.value)">
    </div>

    <div class="card">
        <label>Target Labels:</label><br>
        <button onclick="setLabels(['person'])">Person Only</button>
        <button onclick="setLabels(['car','truck','bus'])">Vehicles</button>
        <button onclick="setLabels(['person','car','truck','bus'])">All</button>
    </div>

    <script>
        function updateThreshold(val) {
            document.getElementById('thresh-val').textContent = (val/100).toFixed(2);
            fetch('/api/threshold', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({value: val/100})
            });
        }

        function setLabels(labels) {
            fetch('/api/labels', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({labels: labels})
            });
        }

        // Poll status every second
        setInterval(() => {
            fetch('/api/status').then(r => r.json()).then(d => {
                const card = document.getElementById('status-card');
                card.className = d.alert_active ? 'card alert' : 'card normal';
                card.innerHTML = `
                    <div class="status">
                        Count: <strong>${d.count}</strong> |
                        FPS: <strong>${d.fps.toFixed(1)}</strong> |
                        Threshold: ${d.threshold.toFixed(2)} |
                        Labels: ${d.target_labels.join(', ')} |
                        ${d.alert_active ? '⚠ ALERT' : 'Normal'}
                    </div>`;
            });
        }, 1000);
    </script>
</body>
</html>
"""


@flask_app.route("/")
def index():
    return render_template_string(CONTROL_HTML)


@flask_app.route("/api/status")
def status():
    with app_state.lock:
        return jsonify(
            count=app_state.count,
            fps=app_state.fps,
            threshold=app_state.threshold,
            target_labels=app_state.target_labels,
            alert_active=app_state.alert_active,
        )


@flask_app.route("/api/threshold", methods=["POST"])
def set_threshold():
    data = request.get_json()
    with app_state.lock:
        app_state.threshold = float(data["value"])
    return jsonify(ok=True)


@flask_app.route("/api/labels", methods=["POST"])
def set_labels():
    data = request.get_json()
    with app_state.lock:
        app_state.target_labels = data["labels"]
    return jsonify(ok=True)


def start_web_server(port=8080):
    """Start Flask in a daemon thread. Call before app.run()."""
    thread = threading.Thread(
        target=lambda: flask_app.run(host="0.0.0.0", port=port, debug=False),
        daemon=True,
    )
    thread.start()
    print(f"Web control panel at http://localhost:{port}")


# ------------------------------------------------------------------------------
# Usage in a pipeline app
# ------------------------------------------------------------------------------
# In your app_callback:
#   with app_state.lock:
#       threshold = app_state.threshold
#       labels = app_state.target_labels
#   # Filter detections using threshold and labels
#   filtered = [d for d in detections
#               if d.get_label() in labels and d.get_confidence() >= threshold]
#   with app_state.lock:
#       app_state.count = len(filtered)
#
# In your main():
#   start_web_server(port=8080)
#   app = GStreamerMyApp(app_callback, user_data)  # Video via GStreamer
#   app.run()
