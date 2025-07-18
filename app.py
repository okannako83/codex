import os
import re
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
from pdfminer.high_level import extract_text

# configuration
UPLOAD_FOLDER = 'uploads'
DB_PATH = 'invoices.db'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        '''CREATE TABLE IF NOT EXISTS invoices (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               filename TEXT,
               invoice_number TEXT,
               date TEXT,
               gross REAL,
               vat REAL,
               net REAL
           )'''
    )
    conn.commit()
    conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_invoice(filepath):
    text = extract_text(filepath)
    invoice_number = re.search(r"Fatura\s*No\s*[:\-]?\s*(\S+)", text)
    invoice_number = invoice_number.group(1) if invoice_number else None

    date_match = re.search(r"Tarih\s*[:\-]?\s*(\d{1,2}[./]\d{1,2}[./]\d{2,4})", text)
    date = None
    if date_match:
        try:
            date = datetime.strptime(date_match.group(1), '%d.%m.%Y').date().isoformat()
        except ValueError:
            try:
                date = datetime.strptime(date_match.group(1), '%d/%m/%Y').date().isoformat()
            except ValueError:
                date = date_match.group(1)

    def parse_amount(label):
        match = re.search(fr"{label}\s*[:\-]?\s*([0-9.,]+)", text)
        if match:
            return float(match.group(1).replace('.', '').replace(',', '.'))
        return None

    gross = parse_amount('Br[uü]t')
    vat = parse_amount('KDV')
    net = parse_amount('Net')

    return invoice_number, date, gross, vat, net


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('Dosya seçilmedi')
            return redirect(request.url)
        if not allowed_file(file.filename):
            flash('Sadece PDF veya TXT dosyaları desteklenir')
            return redirect(request.url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        invoice_number, date, gross, vat, net = parse_invoice(filepath)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            'INSERT INTO invoices (filename, invoice_number, date, gross, vat, net) VALUES (?,?,?,?,?,?)',
            (file.filename, invoice_number, date, gross, vat, net),
        )
        conn.commit()
        conn.close()
        flash('Fatura yüklendi')
        return redirect(url_for('index'))
    # display invoices
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM invoices', conn)
    conn.close()
    invoices = df.to_dict('records')
    return render_template('index.html', invoices=invoices)


@app.route('/export')
def export_excel():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT invoice_number, date, gross, vat, net FROM invoices', conn)
    conn.close()
    output_path = 'invoice_summary.xlsx'
    df.to_excel(output_path, index=False)
    return send_file(output_path, as_attachment=True)


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    init_db()
    app.run(debug=True)
