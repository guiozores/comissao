# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import json
from sqlalchemy import text

from config import Config
from models import db, Commission, Expense, MonthlyReport

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Filtro para formatar valores monetários (exceto o campo "fator")
def format_currency(value):
    try:
        formatted = f"{value:,.2f}"
        # Troca: vírgula -> marcador, ponto -> vírgula, marcador -> ponto.
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return "R$ " + formatted
    except Exception:
        return "R$ " + str(value)

app.jinja_env.filters["currency"] = format_currency

# =====================================================
# Rota para recriar o banco (DESENVOLVIMENTO)
# =====================================================
@app.route("/create_db")
def create_db():
    with app.app_context():
        # Desabilitar verificações de FK (MySQL)
        with db.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.drop_all()
        db.create_all()
        with db.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    return "Tabelas criadas com sucesso!"

# =====================================================
# Rota raiz
# =====================================================
@app.route("/")
def index():
    return redirect(url_for("dashboard"))

# =====================================================
# DASHBOARD: Gerenciamento de Comissões e Despesas
# =====================================================
@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Exibe todas as comissões e despesas (mesmo as reportadas, para consulta)
    commissions = Commission.query.all()
    expenses = Expense.query.all()
    return render_template("dashboard.html", commissions=commissions, expenses=expenses)

# -------------------------------
# CRUD de Comissões
# -------------------------------
@app.route("/dashboard/commission/new", methods=["POST"])
def commission_new():
    # O usuário insere a data no formato "MM/YYYY" ou "YYYY-MM"
    month_year = request.form.get("month_year")
    name = request.form.get("name")
    original_value_str = request.form.get("original_value")
    factor_str = request.form.get("factor")
    status = request.form.get("status")

    if "-" in month_year:
        parts = month_year.split("-")
        y = int(parts[0])
        m = int(parts[1])
    else:
        parts = month_year.split("/")
        m = int(parts[0])
        y = int(parts[1])

    original_value = float(original_value_str.replace(",", ".")) if original_value_str else 0.0
    factor = float(factor_str.replace(",", ".")) if factor_str else None

    new_commission = Commission(
        month=m,
        year=y,
        name=name,
        original_value=original_value,
        factor=factor,
        status=status
    )
    db.session.add(new_commission)
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

    if "-" in month_year:
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

# -------------------------------
# CRUD de Despesas
# -------------------------------
@app.route("/dashboard/expense/new", methods=["POST"])
def expense_new():
    name = request.form.get("name")
    month_year = request.form.get("month_year")
    if "-" in month_year:
        parts = month_year.split("-")
        y = int(parts[0])
        m = int(parts[1])
    else:
        parts = month_year.split("/")
        m = int(parts[0])
        y = int(parts[1])
    value_str = request.form.get("value")
    value = float(value_str.replace(",", ".")) if value_str else 0.0
    is_recurring = True if request.form.get("is_recurring") == "on" else False
    installment_info = request.form.get("installment_info")  # opcional

    new_expense = Expense(
        name=name,
        value=value,
        month=m,
        year=y,
        is_recurring=is_recurring,
        installment_info=installment_info
    )
    db.session.add(new_expense)
    db.session.commit()
    flash("Despesa criada com sucesso!", "success")
    return redirect(url_for("dashboard"))

@app.route("/dashboard/expense/edit/<int:expense_id>", methods=["POST"])
def expense_edit(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    name = request.form.get("name")
    month_year = request.form.get("month_year")
    if "-" in month_year:
        parts = month_year.split("-")
        y = int(parts[0])
        m = int(parts[1])
    else:
        parts = month_year.split("/")
        m = int(parts[0])
        y = int(parts[1])
    value_str = request.form.get("value")
    value = float(value_str.replace(",", ".")) if value_str else 0.0
    is_recurring = True if request.form.get("is_recurring") == "on" else False
    installment_info = request.form.get("installment_info") or ""

    expense.name = name
    expense.month = m
    expense.year = y
    expense.value = value
    expense.is_recurring = is_recurring
    expense.installment_info = installment_info

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

# =====================================================
# RELATÓRIO MENSAL
# =====================================================
@app.route("/monthly_report", methods=["GET", "POST"])
def monthly_report():
    if request.method == "POST":
        # O usuário informa a data do relatório no formato "MM/YYYY"
        report_month_str = request.form.get("report_month")
        if "-" in report_month_str:
            parts = report_month_str.split("-")
            report_year = int(parts[0])
            report_month = int(parts[1])
        else:
            parts = report_month_str.split("/")
            report_month = int(parts[0])
            report_year = int(parts[1])

        # Para comissões: não filtrar pelo lançamento; o usuário seleciona dentre todas as comissões disponíveis (reported == False)
        selected_commission_ids = request.form.getlist("commission_ids", type=int)
        commissions = Commission.query.filter(Commission.id.in_(selected_commission_ids)).all()

        # Para despesas: buscar as que NÃO são recorrentes com o mesmo mês/ano e todas as recorrentes
        normal_expenses = Expense.query.filter_by(month=report_month, year=report_year, is_recurring=False).all()
        recurring_expenses = Expense.query.filter_by(is_recurring=True).all()
        final_expenses = normal_expenses + recurring_expenses

        total_comm = sum(c.computed_value for c in commissions)
        total_exp = sum(e.value for e in final_expenses)
        grand_total = total_comm + total_exp  # soma: comissões + despesas

        # Monta snapshots completos em JSON
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
                "installment_info": e.installment_info,
                "is_recurring": e.is_recurring
            } for e in final_expenses
        ])

        report = MonthlyReport(
            report_month=report_month,
            report_year=report_year,
            total_commissions=total_comm,
            total_expenses=total_exp,
            grand_total=grand_total,
            commissions_data=commissions_data,
            expenses_data=expenses_data
        )
        db.session.add(report)
        db.session.commit()

        # Marcar as comissões utilizadas como reportadas (para que não sejam reutilizadas)
        for c in commissions:
            c.reported = True
        db.session.commit()

        flash("Relatório gerado com sucesso!", "success")
        # Redireciona para a página de visualização do relatório
        return redirect(url_for("monthly_report_view", report_id=report.id))

    # GET: Exibe o formulário para escolher a data do relatório e selecionar as comissões disponíveis
    available_commissions = Commission.query.filter_by(reported=False).all()
    available_expenses = Expense.query.filter_by(is_recurring=False).all()
    return render_template("monthly_report_form.html", 
                           available_commissions=available_commissions, 
                           available_expenses=available_expenses)

@app.route("/monthly_report/view/<int:report_id>")
def monthly_report_view(report_id):
    report = MonthlyReport.query.get_or_404(report_id)
    commissions_data = json.loads(report.commissions_data) if report.commissions_data else []
    expenses_data = json.loads(report.expenses_data) if report.expenses_data else []
    return render_template("monthly_report_view.html",
                           report=report,
                           commissions_data=commissions_data,
                           expenses_data=expenses_data)

@app.route("/monthly_report/delete/<int:report_id>", methods=["POST"])
def monthly_report_delete(report_id):
    report = MonthlyReport.query.get_or_404(report_id)
    # Antes de deletar o relatório, desmarcar as comissões que estavam nele
    if report.commissions_data:
        snapshot = json.loads(report.commissions_data)
        for item in snapshot:
            commission = Commission.query.get(item["id"])
            if commission:
                commission.reported = False
    db.session.delete(report)
    db.session.commit()
    flash("Relatório mensal deletado!", "success")
    return redirect(url_for("monthly_reports_list"))

@app.route("/monthly_reports", methods=["GET"])
def monthly_reports_list():
    reports = MonthlyReport.query.order_by(MonthlyReport.generated_date.desc()).all()
    return render_template("monthly_reports_list.html", reports=reports)

if __name__ == "__main__":
    app.run(debug=True)
