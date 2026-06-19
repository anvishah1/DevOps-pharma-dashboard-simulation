from flask import Flask, render_template_string
import subprocess
import re
import os

app = Flask(__name__)

HEALTH_SCRIPT = "/home/anvi2026/capstone-project/health.sh"
DISK_LOG_FILE = "/home/anvi2026/capstone-project/disk_warning_log.txt"


def get_status_from_percentage(value):
    """
    Decide status based on percentage.
    You can adjust thresholds later.
    """
    if value >= 90:
        return "CRITICAL"
    elif value >= 70:
        return "WARNING"
    else:
        return "OK"


def get_color_class(status):
    """
    Convert status into CSS class.
    """
    status = status.upper()

    if "CRITICAL" in status:
        return "critical"
    elif "WARNING" in status:
        return "warning"
    else:
        return "ok"


def parse_health_output():
    """
    Runs health.sh and converts the output into dashboard cards.
    """
    cards = []

    try:
        result = subprocess.run(
            ["bash", HEALTH_SCRIPT],
            capture_output=True,
            text=True,
            timeout=5
        )

        output = result.stdout.strip()

        if not output:
            return [
                {
                    "name": "Health Script",
                    "value": 0,
                    "display": "No output from health.sh",
                    "status": "WARNING",
                    "class": "warning"
                }
            ]

        lines = output.splitlines()

        for line in lines:
            line = line.strip()

            if not line:
                continue

            percentage_match = re.search(r"(\d+)%", line)

            if percentage_match:
                value = int(percentage_match.group(1))

                if "CRITICAL" in line.upper():
                    status = "CRITICAL"
                elif "WARNING" in line.upper():
                    status = "WARNING"
                elif "OK" in line.upper():
                    status = "OK"
                else:
                    status = get_status_from_percentage(value)

                clean_name = line.split(":")[0] if ":" in line else line

                cards.append(
                    {
                        "name": clean_name,
                        "value": value,
                        "display": line,
                        "status": status,
                        "class": get_color_class(status)
                    }
                )
            else:
                cards.append(
                    {
                        "name": "Info",
                        "value": 0,
                        "display": line,
                        "status": "OK",
                        "class": "ok"
                    }
                )

    except Exception as e:
        cards.append(
            {
                "name": "Error",
                "value": 0,
                "display": f"Could not run health.sh: {e}",
                "status": "CRITICAL",
                "class": "critical"
            }
        )

    return cards


def parse_disk_logs():
    """
    Reads disk_warning_log.txt and converts timestamped blocks into table rows.
    """
    rows = []
    current_timestamp = "Unknown time"

    if not os.path.exists(DISK_LOG_FILE):
        return [
            {
                "timestamp": "No logs yet",
                "message": "disk_warning_log.txt not found",
                "status": "WARNING",
                "class": "warning"
            }
        ]

    with open(DISK_LOG_FILE, "r") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith("-"):
                current_timestamp = line.strip("-").strip()
            else:
                if "CRITICAL" in line.upper():
                    status = "CRITICAL"
                elif "WARNING" in line.upper():
                    status = "WARNING"
                elif "OK" in line.upper():
                    status = "OK"
                else:
                    status = "INFO"

                rows.append(
                    {
                        "timestamp": current_timestamp,
                        "message": line,
                        "status": status,
                        "class": get_color_class(status)
                    }
                )

    if not rows:
        rows.append(
            {
                "timestamp": "No log data",
                "message": "No disk log entries available",
                "status": "WARNING",
                "class": "warning"
            }
        )

    return rows


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>System Health Dashboard</title>
    <meta http-equiv="refresh" content="15">

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
        }

        .container {
            padding: 30px;
        }

        h1 {
            margin-bottom: 5px;
            color: #ffffff;
        }

        .subtitle {
            color: #94a3b8;
            margin-bottom: 30px;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .card {
            background: #1e293b;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            border: 1px solid #334155;
        }

        .card-title {
            font-size: 16px;
            color: #cbd5e1;
            margin-bottom: 10px;
        }

        .card-value {
            font-size: 34px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .status {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 14px;
        }

        .bar-background {
            width: 100%;
            height: 12px;
            background: #334155;
            border-radius: 999px;
            overflow: hidden;
            margin-bottom: 12px;
        }

        .bar {
            height: 100%;
            border-radius: 999px;
        }

        .ok-text {
            color: #22c55e;
        }

        .warning-text {
            color: #f59e0b;
        }

        .critical-text {
            color: #ef4444;
        }

        .ok-bar {
            background: #22c55e;
        }

        .warning-bar {
            background: #f59e0b;
        }

        .critical-bar {
            background: #ef4444;
        }

        .raw-line {
            font-size: 13px;
            color: #94a3b8;
            word-break: break-word;
        }

        .section-title {
            margin-top: 20px;
            margin-bottom: 15px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 14px;
            overflow: hidden;
        }

        th {
            background: #334155;
            color: #f8fafc;
            text-align: left;
            padding: 14px;
        }

        td {
            padding: 12px 14px;
            border-bottom: 1px solid #334155;
            color: #e5e7eb;
        }

        tr:hover {
            background: #273449;
        }

        .badge {
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
        }

        .badge.ok {
            background: rgba(34,197,94,0.15);
            color: #22c55e;
        }

        .badge.warning {
            background: rgba(245,158,11,0.15);
            color: #f59e0b;
        }

        .badge.critical {
            background: rgba(239,68,68,0.15);
            color: #ef4444;
        }

        .footer {
            margin-top: 18px;
            color: #64748b;
            font-size: 13px;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>System Health Dashboard</h1>
        <div class="subtitle">
            Auto-refreshes every 15 seconds | Data from health.sh and disk_warning_log.txt
        </div>

        <h2 class="section-title">Health Summary</h2>

        <div class="cards">
            {% for card in cards %}
            <div class="card">
                <div class="card-title">{{ card.name }}</div>

                {% if card.value > 0 %}
                    <div class="card-value {{ card.class }}-text">{{ card.value }}%</div>
                {% else %}
                    <div class="card-value {{ card.class }}-text">INFO</div>
                {% endif %}

                <div class="status {{ card.class }}-text">{{ card.status }}</div>

                {% if card.value > 0 %}
                <div class="bar-background">
                    <div class="bar {{ card.class }}-bar" style="width: {{ card.value }}%;"></div>
                </div>
                {% endif %}

                <div class="raw-line">{{ card.display }}</div>
            </div>
            {% endfor %}
        </div>

        <h2 class="section-title">Disk Warning Logs</h2>

        <table>
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Disk Information</th>
                    <th>Status</th>
                </tr>
            </thead>

            <tbody>
                {% for row in disk_rows %}
                <tr>
                    <td>{{ row.timestamp }}</td>
                    <td>{{ row.message }}</td>
                    <td>
                        <span class="badge {{ row.class }}">{{ row.status }}</span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="footer">
            Dashboard powered by Flask, Bash scripts, and cron automation.
        </div>
    </div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    cards = parse_health_output()
    disk_rows = parse_disk_logs()
    return render_template_string(
        HTML_TEMPLATE,
        cards=cards,
        disk_rows=disk_rows
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
