# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import json

from config import Config
from models import db, Commission, Expense, MonthlyReport

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route("/create_db")
def create_db():
    with app.app_context():
        db.create_all()
    return "Tabelas criadas com sucesso!"

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

#################
# DASHBOARD
#################
@app.route("/dashboard", methods=["GET"])
def dashboard():
    commissions = Commission.query.all()
    expenses = Expense.query.all()
    return render_template("dashboard.html", commissions=commissions, expenses=expenses)

##########
# COMMISSION (CRUD)
##########

@app.route("/dashboard/commission/new", methods=["POST"])
def commission_new():
    # Campo "month_year" no formato "YYYY-MM" ou "MM/YYYY"
    month_year = request.form.get("month_year")
    name = request.form.get("name")  # Nome/descrição da comissão
    original_value_str = request.form.get("original_value")  # pode ter vírgula
    factor_str = request.form.get("factor")  # também pode ter vírgula
    status = request.form.get("status")

    # Converter month_year em month e year
    # Se usar <input type="month"> = "YYYY-MM"
    if "-" in month_year:  # Exemplo: "2023-06"
        parts = month_year.split("-")
        y = int(parts[0])
        m = int(parts[1])
    else:
        # Caso contrário, se fosse "06/2023"
        parts = month_year.split("/")
        m = int(parts[0])
        y = int(parts[1])

    # Converter original_value e factor (trocando vírgula por ponto)
    original_value = float(original_value_str.replace(",", ".")) if original_value_str else 0.0
    factor = float(factor_str.replace(",", ".")) if factor_str else None

    commission = Commission(
        month=m,
        year=y,
        name=name,
        original_value=original_value,
        factor=factor,
        status=status
    )
    db.session.add(commission)
    db.session.commit()

    flash("Comissão criada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/commission/edit/<int:commission_id>", methods=["POST"])
def commission_edit(commission_id):
    commission = Commission.query.get_or_404(commission_id)

    month_year = request.form.get("month_year")
    name = request.form.get("name")
    original_value_str = request.form.get("original_value")
    factor_str = request.form.get("factor")
    status = request.form.get("status")

    # Parse do month_year
    if "-" in month_year:  # "2023-06"
        parts = month_year.split("-")
        y = int(parts[0])
        m = int(parts[1])
    else:
        parts = month_year.split("/")
        m = int(parts[0])
        y = int(parts[1])

    commission.month = m
    commission.year = y
    commission.name = name
    commission.original_value = float(original_value_str.replace(",", ".")) if original_value_str else 0.0
    commission.factor = float(factor_str.replace(",", ".")) if factor_str else None
    commission.status = status

    db.session.commit()
    flash("Comissão atualizada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/commission/delete/<int:commission_id>", methods=["POST"])
def commission_delete(commission_id):
    commission = Commission.query.get_or_404(commission_id)
    db.session.delete(commission)
    db.session.commit()
    flash("Comissão deletada!", "success")
    return redirect(url_for("dashboard"))

##########
# EXPENSE (CRUD)
##########
@app.route("/dashboard/expense/new", methods=["POST"])
def expense_new():
    name = request.form.get("name")
    value_str = request.form.get("value")
    month = request.form.get("month", type=int)
    year = request.form.get("year", type=int)
    is_recurring = True if request.form.get("is_recurring") == "on" else False

    # Trocar vírgula por ponto no valor
    value = float(value_str.replace(",", ".")) if value_str else 0.0

    expense = Expense(
        name=name,
        value=value,
        month=month,
        year=year,
        is_recurring=is_recurring
    )
    db.session.add(expense)
    db.session.commit()
    flash("Despesa criada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/expense/edit/<int:expense_id>", methods=["POST"])
def expense_edit(expense_id):
    expense = Expense.query.get_or_404(expense_id)

    name = request.form.get("name")
    value_str = request.form.get("value")
    month = request.form.get("month", type=int)
    year = request.form.get("year", type=int)
    is_recurring = True if request.form.get("is_recurring") == "on" else False

    expense.name = name
    expense.value = float(value_str.replace(",", ".")) if value_str else 0.0
    expense.month = month
    expense.year = year
    expense.is_recurring = is_recurring

    db.session.commit()
    flash("Despesa atualizada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/expense/delete/<int:expense_id>", methods=["POST"])
def expense_delete(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    flash("Despesa deletada!", "success")
    return redirect(url_for("dashboard"))

##########
# MONTHLY REPORT
##########
@app.route("/monthly_report", methods=["GET", "POST"])
def monthly_report():
    if request.method == "POST":
        report_month_str = request.form.get("report_month")
        # Se for "2023-08" (YYYY-MM) ou "08/2023" (MM/YYYY)
        if "-" in report_month_str:
            parts = report_month_str.split("-")
            y = int(parts[0])
            m = int(parts[1])
        else:
            parts = report_month_str.split("/")
            m = int(parts[0])
            y = int(parts[1])

        selected_commissions = request.form.getlist("commission_ids", type=int)
        selected_expenses = request.form.getlist("expense_ids", type=int)

        commissions = Commission.query.filter(Commission.id.in_(selected_commissions)).all()
        expenses = Expense.query.filter(Expense.id.in_(selected_expenses)).all()

        total_comm = sum(c.computed_value for c in commissions)
        total_exp = sum(e.value for e in expenses)
        grand_total = total_comm - total_exp

        # Monta JSON p/ salvar snapshot
        commissions_data = json.dumps([
            {
                "id": c.id,
                "name": c.name,
                "month": c.month,
                "year": c.year,
                "original_value": c.original_value,
                "factor": c.factor,
                "status": c.status,
                "computed_value": c.computed_value
            } for c in commissions
        ])
        expenses_data = json.dumps([
            {
                "id": e.id,
                "name": e.name,
                "value": e.value,
                "month": e.month,
                "year": e.year,
                "is_recurring": e.is_recurring
            } for e in expenses
        ])

        report = MonthlyReport(
            report_month=m,
            report_year=y,
            total_commissions=total_comm,
            total_expenses=total_exp,
            grand_total=grand_total,
            commissions_data=commissions_data,
            expenses_data=expenses_data
        )
        db.session.add(report)
        db.session.commit()

        flash("Relatório gerado com sucesso!", "success")
        return redirect(url_for("monthly_report_view", report_id=report.id))

    # GET
    commissions = Commission.query.all()
    expenses = Expense.query.all()
    return render_template("monthly_report_form.html", commissions=commissions, expenses=expenses)

@app.route("/monthly_report/view/<int:report_id>")
def monthly_report_view(report_id):
    report = MonthlyReport.query.get_or_404(report_id)
    commissions_data = json.loads(report.commissions_data) if report.commissions_data else []
    expenses_data = json.loads(report.expenses_data) if report.expenses_data else []
    return render_template(
        "monthly_report_view.html",
        report=report,
        commissions_data=commissions_data,
        expenses_data=expenses_data
    )


# Roda a aplicação ao executar "python app.py"
if __name__ == "__main__":
    app.run(debug=True)
