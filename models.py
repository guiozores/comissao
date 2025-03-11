# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Commission(db.Model):
    __tablename__ = "commissions"
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    original_value = db.Column(db.Float, nullable=False)
    factor = db.Column(db.Float, nullable=True)
    # Status da empresa: indica se o pagamento do cliente já foi recebido, se está aprovado, em execução ou apenas prevista.
    company_status = db.Column(db.String(50), nullable=False)
    # Status do funcionário: indica se o funcionário já recebeu a comissão, se está aguardando ou em análise.
    employee_status = db.Column(db.String(50), nullable=False)
    reported = db.Column(db.Boolean, nullable=False)
    
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
    installment_info = db.Column(db.String(50), nullable=True)

class MonthlyReport(db.Model):
    __tablename__ = "monthly_reports"
    id = db.Column(db.Integer, primary_key=True)
    report_month = db.Column(db.Integer, nullable=False)
    report_year = db.Column(db.Integer, nullable=False)
    generated_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_commissions = db.Column(db.Float, nullable=False, default=0.0)
    total_expenses = db.Column(db.Float, nullable=False, default=0.0)
    grand_total = db.Column(db.Float, nullable=False, default=0.0)
    commissions_data = db.Column(db.Text, nullable=True)
    expenses_data = db.Column(db.Text, nullable=True)

class FixedCost(db.Model):
    __tablename__ = "fixed_costs"
    id = db.Column(db.Integer, primary_key=True)
    vivo = db.Column(db.Float, nullable=False, default=0.0)
    va = db.Column(db.Float, nullable=False, default=0.0)
