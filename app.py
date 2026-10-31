from flask import Flask, request, render_template_string
import time
import csv
import os

app = Flask(__name__)

db_file = "sfg_tracking.csv"
dummy_job_file = "dummy_job_orders.txt"

html_template = """
<!DOCTYPE html>
<html>
<body>
    <h1>SFG Tracker Prototype</h1>
    
    <h2>1. Log a Send</h2>
    <form action="/send" method="POST">
        Part Name: <input type="text" name="part_name" required><br>
        From Plant: <input type="text" name="from_plant" required><br>
        To Plant: <input type="text" name="to_plant" required><br>
        <input type="submit" value="Log Send">
    </form>

    <h2>2. Confirm Receipt</h2>
    <form action="/receive" method="POST">
        Tracking ID: <input type="text" name="tracking_id" required><br>
        <input type="submit" value="Confirm Receipt">
    </form>

    <h2>Audit Trail</h2>
    <table border="1">
        <tr><th>ID</th><th>Part</th><th>From</th><th>To</th><th>Status</th></tr>
        {% for row in trail %}
        <tr>
            {% for item in row %}
            <td>{{ item }}</td>
            {% endfor %}
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

def init_db():
    if not os.path.exists(db_file):
        with open(db_file, "w", newline='') as f:
            pass

@app.route("/")
def index():
    init_db()
    trail = []
    with open(db_file, "r") as f:
        reader = csv.reader(f)
        trail = list(reader)
    return render_template_string(html_template, trail=trail)

@app.route("/send", methods=["POST"])
def send_part():
    tracking_id = str(int(time.time() * 1000))
    data = [tracking_id, request.form["part_name"], request.form["from_plant"], request.form["to_plant"], "SENT"]
    
    with open(db_file, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)
        
    with open(dummy_job_file, "a") as f:
        f.write(f"Job update: Part {request.form['part_name']} dispatched. Awaiting receipt.\n")
        
    return f"Send logged successfully. Your Tracking ID is: {tracking_id} <br><a href='/'>Return to Dashboard</a>"

@app.route("/receive", methods=["POST"])
def receive_part():
    tid = request.form["tracking_id"]
    rows = []
    
    with open(db_file, "r") as f:
        reader = csv.reader(f)
        rows = list(reader)
        
    for row in rows:
        if row and row[0] == tid:
            row[4] = "RECEIVED"
            
    with open(db_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    return "Receipt confirmed. <br><a href='/'>Return to Dashboard</a>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
