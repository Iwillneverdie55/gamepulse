"""GamePulse — Flask backend with SQLite. No auth, single shared workspace."""
import json
import os
import sqlite3
from contextlib import contextmanager
from flask import Flask, request, jsonify, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=BASE_DIR)
DB_PATH = os.path.join(BASE_DIR, "gamepulse.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                char_id TEXT, account_id TEXT, char_name TEXT,
                server TEXT, order_id TEXT, channel TEXT,
                amount REAL, region TEXT, tz INTEGER,
                priority TEXT, report_time TEXT, report_local TEXT,
                sla_deadline TEXT, sla_hours REAL,
                desc TEXT, status TEXT,
                created_at TEXT, resolved_at TEXT, notes TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id TEXT PRIMARY KEY,
                source TEXT, category TEXT,
                char_id TEXT, account_id TEXT, char_name TEXT,
                server TEXT, region TEXT,
                content TEXT, impact TEXT, severity TEXT,
                created_at TEXT, status TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS liveops (
                id TEXT PRIMARY KEY,
                name TEXT, type TEXT,
                start TEXT, "end" TEXT,
                regions TEXT, note TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS networks (
                id TEXT PRIMARY KEY,
                region TEXT, type TEXT, time TEXT,
                affected INTEGER, desc TEXT,
                created_at TEXT
            )
        """)
        conn.commit()

def snake_to_camel(s):
    parts = s.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])

def row_to_dict(row):
    return {snake_to_camel(k): row[k] for k in row.keys()}

# ── API ──────────────────────────────────────────────

@app.route("/api/data")
def api_data():
    with get_db() as conn:
        payments = [row_to_dict(r) for r in conn.execute("SELECT * FROM payments ORDER BY created_at DESC").fetchall()]
        feedbacks = [row_to_dict(r) for r in conn.execute("SELECT * FROM feedbacks ORDER BY created_at DESC").fetchall()]
        liveops = [row_to_dict(r) for r in conn.execute("SELECT * FROM liveops ORDER BY created_at DESC").fetchall()]
        networks = [row_to_dict(r) for r in conn.execute("SELECT * FROM networks ORDER BY created_at DESC").fetchall()]
    return jsonify({"payments": payments, "feedbacks": feedbacks, "liveops": liveops, "networks": networks})

@app.route("/api/payments", methods=["POST"])
def api_add_payment():
    p = request.json
    with get_db() as conn:
        conn.execute("""
            INSERT INTO payments (id, char_id, account_id, char_name, server,
                order_id, channel, amount, region, tz, priority,
                report_time, report_local, sla_deadline, sla_hours,
                desc, status, created_at, resolved_at, notes)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (p["id"], p.get("charId",""), p.get("accountId",""), p.get("charName",""),
              p.get("server",""), p.get("orderId",""), p.get("channel",""), p.get("amount",0),
              p.get("region",""), p.get("tz",8), p.get("priority","mid"),
              p.get("reportTime",""), p.get("reportLocal",""), p.get("slaDeadline",""),
              p.get("slaHours",4), p.get("desc",""), p.get("status","pending"),
              p.get("createdAt",""), p.get("resolvedAt"), p.get("notes","")))
        conn.commit()
    return jsonify({"ok": True}), 201

VALID_TRANSITIONS = {
    "pending": ["progress", "deleted"],
    "progress": ["done", "deleted"],
    "done": [],         # final state, no transitions allowed
    "deleted": [],      # final state
    "verified": ["reissued", "deleted"],
    "reissued": ["done", "deleted"],
}

@app.route("/api/payments/<pid>", methods=["PUT"])
def api_update_payment(pid):
    p = request.json
    new_status = p.get("status")
    with get_db() as conn:
        current = conn.execute("SELECT status FROM payments WHERE id=?", (pid,)).fetchone()
        if not current:
            return jsonify({"ok": False, "error": "not found"}), 404
        old_status = current["status"]
        allowed = VALID_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            return jsonify({"ok": False, "error": f"Cannot change from '{old_status}' to '{new_status}'"}), 409
        conn.execute("UPDATE payments SET status=?, resolved_at=?, notes=? WHERE id=?",
                     (new_status, p.get("resolvedAt"), p.get("notes",""), pid))
        conn.commit()
    return jsonify({"ok": True})

@app.route("/api/feedbacks", methods=["POST"])
def api_add_feedback():
    f = request.json
    with get_db() as conn:
        conn.execute("""
            INSERT INTO feedbacks (id, source, category, char_id, account_id,
                char_name, server, region, content, impact, severity, created_at, status)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (f["id"], f.get("source",""), f.get("category",""), f.get("charId",""),
              f.get("accountId",""), f.get("charName",""), f.get("server",""),
              f.get("region",""), f.get("content",""), f.get("impact","some"),
              f.get("severity","major"), f.get("createdAt",""), "open"))
        conn.commit()
    return jsonify({"ok": True}), 201

@app.route("/api/liveops", methods=["POST"])
def api_add_liveops():
    lo = request.json
    with get_db() as conn:
        conn.execute("""
            INSERT INTO liveops (id, name, type, start, "end", regions, note, created_at)
            VALUES (?,?,?,?,?,?,?,?)
        """, (lo["id"], lo.get("name",""), lo.get("type",""), lo.get("start",""),
              lo.get("end",""), json.dumps(lo.get("regions",[])), lo.get("note",""),
              lo.get("createdAt","")))
        conn.commit()
    return jsonify({"ok": True}), 201

@app.route("/api/networks", methods=["POST"])
def api_add_network():
    n = request.json
    with get_db() as conn:
        conn.execute("""
            INSERT INTO networks (id, region, type, time, affected, desc, created_at)
            VALUES (?,?,?,?,?,?,?)
        """, (n["id"], n.get("region",""), n.get("type",""), n.get("time",""),
              n.get("affected",0), n.get("desc",""), n.get("createdAt","")))
        conn.commit()
    return jsonify({"ok": True}), 201

# ── Static files ─────────────────────────────────────

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# Auto-init DB on startup (works in both WSGI and dev modes)
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 GamePulse running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
