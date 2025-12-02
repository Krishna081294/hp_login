# utils/logger.py
REPORT = []

def log_step(desc: str, status: str = "PASS") -> None:
    REPORT.append((desc, status))
    print(f"{desc}: {status}")

def generate_report(path: str = "automation_report.html") -> None:
    html = (
        "<html><head><meta charset='utf-8'><title>Automation Report</title></head><body>"
        "<h2>HP Account Automation Report</h2><table border='1'><tr><th>Step</th><th>Status</th></tr>"
    )
    for desc, status in REPORT:
        html += f"<tr><td>{desc}</td><td>{status}</td></tr>"
    html += "</table></body></html>"
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report generated: {path}")
