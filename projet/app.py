import sqlite3
from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape   # ✅ ajout landscape
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

# --- Init DB ---
def init_db():
    conn = sqlite3.connect("prestations.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS prestations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom TEXT,
                    nature TEXT,
                    periode TEXT,
                    montant_prestation REAL,
                    montant_retenir REAL,
                    montant_paye_precedent REAL,
                    imputation TEXT,
                    observations TEXT,
                    projet TEXT,
                    remarque TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# --- Home ---
@app.route("/")
def index():
    conn = sqlite3.connect("prestations.db")
    c = conn.cursor()
    c.execute("SELECT * FROM prestations")
    rows = c.fetchall()
    conn.close()

    # Calcul des montants restants et totaux
    prestations = []
    total_restant = 0
    total_paye_prec = 0

    for row in rows:
        montant_restant = row[4] - row[5] - row[6]
        prestations.append(row + (montant_restant,))
        total_restant += montant_restant
        total_paye_prec += row[6]

    return render_template("index.html", prestations=prestations,
                           total_restant=total_restant,
                           total_paye_prec=total_paye_prec)

# --- Ajouter ---
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        nom = request.form["nom"]
        nature = request.form["nature"]
        periode = request.form["periode"]
        montant_prestation = float(request.form["montant_prestation"])
        montant_retenir = float(request.form.get("montant_retenir", 0))
        montant_paye_precedent = float(request.form.get("montant_paye_precedent", 0))
        imputation = request.form["imputation"]
        observations = request.form["observations"]
        projet = request.form["projet"]
        remarque = request.form["remarque"]

        conn = sqlite3.connect("prestations.db")
        c = conn.cursor()
        c.execute("INSERT INTO prestations (nom, nature, periode, montant_prestation, montant_retenir, montant_paye_precedent, imputation, observations, projet, remarque) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (nom, nature, periode, montant_prestation, montant_retenir, montant_paye_precedent, imputation, observations, projet, remarque))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add.html")

# --- Modifier ---
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("prestations.db")
    c = conn.cursor()

    if request.method == "POST":
        nom = request.form["nom"]
        nature = request.form["nature"]
        periode = request.form["periode"]
        montant_prestation = float(request.form["montant_prestation"])
        montant_retenir = float(request.form.get("montant_retenir", 0))
        montant_paye_precedent = float(request.form.get("montant_paye_precedent", 0))
        imputation = request.form["imputation"]
        observations = request.form["observations"]
        projet = request.form["projet"]
        remarque = request.form["remarque"]

        c.execute("""UPDATE prestations 
                     SET nom=?, nature=?, periode=?, montant_prestation=?, 
                         montant_retenir=?, montant_paye_precedent=?, 
                         imputation=?, observations=?, projet=?, remarque=?
                     WHERE id=?""",
                  (nom, nature, periode, montant_prestation, montant_retenir,
                   montant_paye_precedent, imputation, observations, projet, remarque, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    c.execute("SELECT * FROM prestations WHERE id=?", (id,))
    prestation = c.fetchone()
    conn.close()
    return render_template("edit.html", prestation=prestation)

# --- Supprimer ---
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("prestations.db")
    c = conn.cursor()
    c.execute("DELETE FROM prestations WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

# --- Export Excel ---
@app.route("/export/excel")
def export_excel():
    conn = sqlite3.connect("prestations.db")
    df = pd.read_sql_query("SELECT * FROM prestations", conn)
    conn.close()

    df["montant_restant"] = df["montant_prestation"] - df["montant_retenir"] - df["montant_paye_precedent"]

    path = "export_prestations.xlsx"
    df.to_excel(path, index=False)
    return send_file(path, as_attachment=True)

# --- Export PDF ---
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import sqlite3
import pandas as pd
from flask import send_file

@app.route("/export/pdf")
def export_pdf():
    conn = sqlite3.connect("prestations.db")
    df = pd.read_sql_query("SELECT * FROM prestations", conn)
    conn.close()

    df["montant_restant"] = df["montant_prestation"] - df["montant_retenir"] - df["montant_paye_precedent"]

    path = "export_prestations.pdf"
    doc = SimpleDocTemplate(path, pagesize=landscape(A4))
    styles = getSampleStyleSheet()
    elements = []

    # --- Préparer les données ---
    data = []

    # En-têtes avec wrap automatique
    headers = [Paragraph(str(col), styles["Normal"]) for col in df.columns.tolist()]
    data.append(headers)

    # Contenu avec wrap automatique
    for row in df.values.tolist():
        new_row = []
        for cell in row:
            text = str(cell) if cell is not None else ""
            new_row.append(Paragraph(text, styles["Normal"]))
        data.append(new_row)

    # --- Largeur dynamique ---
    page_width, _ = landscape(A4)
    col_count = len(df.columns)
    col_width = page_width / col_count

    # --- Créer tableau ---
    table = Table(data, colWidths=[col_width] * col_count)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),  # Wrap aligné en haut
    ]))

    elements.append(Paragraph("Liste des Prestations", styles["Title"]))
    elements.append(table)

    doc.build(elements)
    return send_file(path, as_attachment=True)

