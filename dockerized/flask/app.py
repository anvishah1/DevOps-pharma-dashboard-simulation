from flask import Flask, render_template_string
import subprocess
import re
import os

app = Flask(__name__)

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HEALTH_SCRIPT = os.path.join(BASE_DIR, "health.sh")
DISK_LOG_FILE = "/host/home/anvi2026/capstone-project/disk_warning_log.txt"

def get_color_class(status):
    status = status.upper()
    if "CRITICAL" in status:
        return "critical"
    elif "WARNING" in status:
        return "warning"
    else:
        return "ok"


def parse_health_output():
    cards = []

    try:
        result = subprocess.run(
            ["bash", HEALTH_SCRIPT],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = result.stdout.strip().splitlines()

        for line in lines:

            # ✅ Ignore header
            if "SERVER HEALTH REPORT" in line.upper():
                continue

            line = line.strip()
            if not line:
                continue

            # ✅ Status detection
            if "CRITICAL" in line.upper():
                status = "CRITICAL"
            elif "WARNING" in line.upper():
                status = "WARNING"
            elif "OK" in line.upper():
                status = "OK"
            else:
                status = "INFO"

            # ✅ Extract percentage if exists
            match = re.search(r"(\d+)%", line)
            value = int(match.group(1)) if match else None

            name = line.split(":")[0] if ":" in line else "Info"

            cards.append({
                "name": name,
                "value": value,
                "display": line,
                "status": status,
                "class": get_color_class(status)
            })

    except Exception as e:
        cards.append({
            "name": "Error",
            "value": None,
            "display": str(e),
            "status": "CRITICAL",
            "class": "critical"
        })

    return cards


def parse_disk_logs():
    rows = []
    current_timestamp = "Unknown"

    if not os.path.exists(DISK_LOG_FILE):
        return []

    with open(DISK_LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("-"):
                current_timestamp = line.strip("- ").strip()
            else:
                if "CRITICAL" in line.upper():
                    status = "CRITICAL"
                elif "WARNING" in line.upper():
                    status = "WARNING"
                else:
                    status = "OK"

                rows.append({
                    "timestamp": current_timestamp,
                    "message": line,
                    "status": status,
                    "class": get_color_class(status)
                })

    return rows


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Dashboard</title>

<!-- ✅ refresh every 5 minutes -->
<meta http-equiv="refresh" content="15">

<style>
body {
    font-family: Arial;
    background:#0f172a;
    color:white;
    padding:20px;
}

/* ✅ SINGLE ROW CARDS */
.cards {
    display:grid;
    grid-template-columns: repeat(auto-fit,minmax(220px, 1fr));
    gap:20px;
}

.card {
    min-width:220px;
    background:#1e293b;
    padding:20px;
    border-radius:10px;
}

.ok { color:#22c55e; }
.warning { color:#f59e0b; }
.critical { color:#ef4444; }

.bar-container {
    background:#334155;
    height:10px;
    border-radius:10px;
}

.bar { height:10px; border-radius:10px; }
.ok-bar { background:#22c55e; }
.warning-bar { background:#f59e0b; }
.critical-bar { background:#ef4444; }

table {
    width:100%;
    margin-top:30px;
    border-collapse: collapse;
}

th,td {
    padding:10px;
    border-bottom:1px solid #334155;
}
</style>
</head>

<body>

<h1>ABC Pharma System Health Dashboard</h1>

<div class="cards">
{% for c in cards %}
<div class="card">

<h3>{{c.name}}</h3>

<!-- ✅ FIX: no more -- -->
<h1 class="{{c.class}}">
{% if c.value %}
    {{c.value}}%
{% else %}
    {{c.status}}
{% endif %}
</h1>

<p class="{{c.class}}">{{c.status}}</p>

{% if c.value %}
<div class="bar-container">
    <div class="bar {{c.class}}-bar" style="width:{{c.value}}%"></div>
</div>
{% endif %}

<p>{{c.display}}</p>

</div>
{% endfor %}
</div>

<h2>Disk Logs</h2>

<table>
<tr>
<th>Timestamp</th>
<th>Disk Info</th>
<th>Status</th>
</tr>

{% for r in disk_rows %}
<tr>
<td>{{r.timestamp}}</td>
<td>{{r.message}}</td>
<td class="{{r.class}}">{{r.status}}</td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(
        HTML,
        cards=parse_health_output(),
        disk_rows=parse_disk_logs()
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
