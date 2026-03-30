from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import dns.resolver
import sqlite3
from datetime import datetime
import os


app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('emails.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_valid BOOLEAN DEFAULT TRUE,
            ip_address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def validate_email_syntax(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def check_mx_record(domain):
    try:
        records = dns.resolver.resolve(domain, 'MX')
        return len(records) > 0
    except:
        return False

def save_email_to_db(email, ip_address=None):
    try:
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO subscribers (email, ip_address) VALUES (?, ?)",
            (email, ip_address)
        )
        conn.commit()
        success = c.rowcount > 0
        conn.close()
        return success, "Email сохранен" if success else "Email уже существует"
    except Exception as e:
        return False, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('email', '')
    
    ip_address = request.remote_addr
    
    if not email:
        return jsonify({'valid': False, 'message': 'Введите email'})
    
    if not validate_email_syntax(email):
        return jsonify({'valid': False, 'message': 'Неверный формат email'})
    
    domain = email.split('@')[1]
    if not check_mx_record(domain):
        return jsonify({'valid': False, 'message': 'Домен не принимает почту'})
    
    saved, save_message = save_email_to_db(email, ip_address)
    
    return jsonify({
        'valid': True, 
        'message': 'Email валиден и сохранен в базу',
        'saved': saved,
        'save_message': save_message
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)


