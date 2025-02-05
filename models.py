# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Commission(db.Model):
    __tablename__ = "commissions"
    id = db.Column(db.Integer, primary_key=True)

    # Em vez de ter month e year separados, você pode continuar tendo (month, year),
    # ou armazenar numa string do tipo "YYYY-MM". Aqui vou manter month e year
    # internamente, mas farei o parse de um campo único no "app.py".
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)

    # Novo campo: nome/descrição da comissão
    name = db.Column(db.String(200), nullable=False)  # Pode ser livre

    original_value = db.Column(db.Float, nullable=False)
    factor = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), nullable=False)

    @property
    def computed_value(self):
        if self.factor:
            return self.original_value * self.factor
        return self.original_value

class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_recurring = db.Column(db.Boolean, default=False)

class MonthlyReport(db.Model):
    __tablename__ = "monthly_reports"
    id = db.Column(db.Integer, primary_key=True)
    report_month = db.Column(db.Integer, nullable=False)
    report_year = db.Column(db.Integer, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_commissions = db.Column(db.Float, nullable=False, default=0.0)
    total_expenses = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    commissions_data = db.Column(db.Text, nullable=True)  # JSON
    expenses_data = db.Column(db.Text, nullable=True)     # JSON
