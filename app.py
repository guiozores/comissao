from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import json
import re
from sqlalchemy import text

from config import Config
from models import db, Commission, Expense, MonthlyReport, FixedCost

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Filtro para formatação monetária (exceto o campo "fator")
def format_currency(value):
    try:
        formatted = f"{value:,.2f}"
        # Troca: vírgula -> marcador, ponto -> vírgula, marcador -> ponto.
        formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
        return "R$ " + formatted
    except Exception:
        return "R$ " + str(value)

app.jinja_env.filters["currency"] = format_currency

@app.context_processor
def inject_fixed_cost_model():
    from models import FixedCost
    fixed = FixedCost.query.get(1)
    return dict(FixedCost=FixedCost, fixed_cost=fixed)


# -------------------------------------------------
# Função para processar despesas extras (na tela do relatório)
# -------------------------------------------------
def parse_extra_expenses(text):
    """
    Processa o texto de despesas extras.
    Cada linha deve estar no formato: DESCRIÇÃO;VALOR
    Se não houver ';', tenta extrair o último valor encontrado via regex.
    Retorna uma lista de dicionários com 'name' e 'value'.
    """
    expenses = []
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    value_pattern = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d{2})')
    for line in lines:
        if ";" in line:
            parts = line.split(";")
            description = parts[0].strip()
            value_str = parts[1].strip()
        else:
            matches = value_pattern.findall(line)
            if matches:
                value_str = matches[-1]
                description = value_pattern.sub("", line).strip()
            else:
                continue
        try:
            value = float(value_str.replace(".", "").replace(",", "."))
        except Exception:
            value = 0.0
        expenses.append({"name": description, "value": value})
    return expenses

# -------------------------------------------------
# Função para filtrar despesas recorrentes com parcelas
# -------------------------------------------------
def filter_recurring_expenses(expenses, report_month, report_year):
    """
    Para cada despesa recorrente com installment_info no formato "X/Y",
    calcula o número de meses decorridos entre o lançamento e o relatório.
    Se o número de parcelas atual (diff + 1) for menor ou igual ao total,
    atualiza o installment_info para o valor atual e inclui a despesa.
    Caso contrário, ignora a despesa.
    Despesas recorrentes sem installment_info (ou não no formato X/Y) são incluídas se a data de lançamento é anterior ou igual ao período do relatório.
    """
    filtered = []
    for e in expenses:
        if e.installment_info:
            m = re.match(r"(\d+)/(\d+)", e.installment_info)
            if m:
                start_installment = int(m.group(1))  # geralmente 1
                total_installments = int(m.group(2))
                # Calcular a diferença de meses entre a data de lançamento e o relatório
                diff = (report_year - e.year) * 12 + (report_month - e.month)
                current_installment = diff + 1
                if current_installment >= 1 and current_installment <= total_installments:
                    # Atualiza o installment_info para refletir o valor atual
                    e.installment_info = f"{current_installment}/{total_installments}"
                    filtered.append(e)
            else:
                # Se não seguir o padrão, incluir se o lançamento for anterior ou igual ao relatório
                diff = (report_year - e.year) * 12 + (report_month - e.month)
                if diff >= 0:
                    filtered.append(e)
        else:
            # Despesa recorrente sem installment_info: incluir se o lançamento é anterior ou igual
            diff = (report_year - e.year) * 12 + (report_month - e.month)
            if diff >= 0:
                filtered.append(e)
    return filtered

# =====================================================
# Rota para recriar o banco (DESENVOLVIMENTO)
# =====================================================
@app.route("/create_db")
def create_db():
    with app.app_context():
        with db.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        db.drop_all()
        db.create_all()
        # Cria também um registro para FixedCost, se não existir
        if not FixedCost.query.get(1):
            fc = FixedCost(vivo=50.0, va=100.0)
            db.session.add(fc)
            db.session.commit()
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
# DASHBOARD: Listagem com Filtro e Paginação
# =====================================================
@app.route("/dashboard", methods=["GET"])
def dashboard():
    # Obter parâmetros de filtro via query string
    # filter_mode: "month" ou "year" ou vazio (sem filtro)
    filter_mode = request.args.get("filter_mode")
    filter_month_year = request.args.get("filter_month_year")  # quando for "month": formato "YYYY-MM"
    filter_year = request.args.get("filter_year")              # quando for "year"
    page_comm = request.args.get("page_comm", 1, type=int)
    page_exp = request.args.get("page_exp", 1, type=int)
    
    per_page = 8 if filter_mode in ["month", "year"] else 5

    # Query para Comissões
    commissions_query = Commission.query
    if filter_mode == "month" and filter_month_year:
        parts = filter_month_year.split("-")
        if len(parts) == 2:
            y = int(parts[0])
            m = int(parts[1])
            commissions_query = commissions_query.filter(Commission.year == y, Commission.month == m)
    elif filter_mode == "year" and filter_year:
        commissions_query = commissions_query.filter(Commission.year == int(filter_year))
    commissions_query = commissions_query.order_by(Commission.id.desc())
    comm_pagination = commissions_query.paginate(page=page_comm, per_page=per_page, error_out=False)

    # Query para Despesas
    expenses_query = Expense.query
    if filter_mode == "month" and filter_month_year:
        parts = filter_month_year.split("-")
        if len(parts) == 2:
            y = int(parts[0])
            m = int(parts[1])
            # Para despesas não recorrentes, filtrar por mês/ano
            expenses_query = expenses_query.filter(Expense.year == y, Expense.month == m, Expense.is_recurring==False)
    elif filter_mode == "year" and filter_year:
        expenses_query = expenses_query.filter(Expense.year == int(filter_year), Expense.is_recurring==False)
    expenses_query = expenses_query.order_by(Expense.id.desc())
    exp_pagination = expenses_query.paginate(page=page_exp, per_page=per_page, error_out=False)

    return render_template("dashboard.html", 
                           commissions=comm_pagination.items, 
                           expenses=exp_pagination.items,
                           comm_pagination=comm_pagination,
                           exp_pagination=exp_pagination,
                           filter_mode=filter_mode,
                           filter_month_year=filter_month_year,
                           filter_year=filter_year)

# -------------------------------
# CRUD de Comissões (Dashboard)
# -------------------------------
@app.route("/dashboard/commission/new", methods=["POST"])
def commission_new():
    month_year = request.form.get("month_year")  # "MM/YYYY" ou "YYYY-MM"
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
# CRUD de Despesas (Dashboard)
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
    installment_info = request.form.get("installment_info")

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
# RELATÓRIO MENSAL: Geração e Processamento
# =====================================================
@app.route("/monthly_report", methods=["GET", "POST"])
def monthly_report():
    if request.method == "POST":
        # O usuário informa a data do relatório no formato "MM/YYYY" (input type="month" retorna "YYYY-MM")
        report_month_str = request.form.get("report_month")
        if "-" in report_month_str:
            parts = report_month_str.split("-")
            report_year = int(parts[0])
            report_month = int(parts[1])
        else:
            parts = report_month_str.split("/")
            report_month = int(parts[0])
            report_year = int(parts[1])
        
        # As comissões são selecionadas via checkbox (podem ter sido lançadas em qualquer período, desde que ainda não reportadas)
        selected_commission_ids = request.form.getlist("commission_ids", type=int)
        commissions = Commission.query.filter(Commission.id.in_(selected_commission_ids)).all()
        
        # Para despesas:
        # - Despesas NÃO recorrentes do período (selecionadas via checkbox)
        normal_expenses = Expense.query.filter_by(month=report_month, year=report_year, is_recurring=False).all()
        # - Todas as despesas recorrentes (independentemente do período)
        recurring_expenses = Expense.query.filter_by(is_recurring=True).all()
        final_expenses = normal_expenses + recurring_expenses

        # Processa as despesas extras inseridas no textarea:
        # Aqui, adicionamos a condição extra_expenses_text and extra_expenses_text.strip() para garantir que não seja vazio
        extra_expenses_text = request.form.get("extra_expenses")
        if extra_expenses_text and extra_expenses_text.strip():
            parsed_extras = parse_extra_expenses(extra_expenses_text)
            for exp in parsed_extras:
                new_exp = Expense(
                    name=exp["name"],
                    value=exp["value"],
                    month=report_month,
                    year=report_year,
                    is_recurring=False,
                    installment_info=""
                )
                db.session.add(new_exp)
                db.session.flush()  # Para garantir que o novo registro receba um ID
                final_expenses.append(new_exp)
            db.session.commit()

        total_comm = sum(c.computed_value for c in commissions)
        total_exp = sum(e.value for e in final_expenses)
        grand_total = total_comm + total_exp

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

        # Marcar as comissões utilizadas como reportadas para que não sejam reutilizadas
        for c in commissions:
            c.reported = True
        db.session.commit()

        flash("Relatório gerado com sucesso!", "success")
        return redirect(url_for("monthly_report_view", report_id=report.id))
    
    # GET: Exibe o formulário para gerar o relatório
    available_commissions = Commission.query.filter_by(reported=False).all()
    available_expenses = Expense.query.filter_by(is_recurring=False).all()
    return render_template("monthly_report_form.html", 
                           available_commissions=available_commissions, 
                           available_expenses=available_expenses)


# =====================================================
# VISUALIZAÇÃO DO RELATÓRIO MENSAL
# =====================================================
@app.route("/monthly_report/view/<int:report_id>")
def monthly_report_view(report_id):
    report = MonthlyReport.query.get_or_404(report_id)
    commissions_data = json.loads(report.commissions_data) if report.commissions_data else []
    expenses_data = json.loads(report.expenses_data) if report.expenses_data else []
    fixed_cost = FixedCost.query.get(1)
    vivo = fixed_cost.vivo if fixed_cost else 0.0
    va = fixed_cost.va if fixed_cost else 0.0
    return render_template("monthly_report_view.html",
                           report=report,
                           commissions_data=commissions_data,
                           expenses_data=expenses_data,
                           fixed_vivo=vivo,
                           fixed_va=va)


# =====================================================
# DELEÇÃO DO RELATÓRIO MENSAL (Libera as comissões)
# =====================================================
@app.route("/monthly_report/delete/<int:report_id>", methods=["POST"])
def monthly_report_delete(report_id):
    report = MonthlyReport.query.get_or_404(report_id)
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

# =====================================================
# LISTAGEM DE TODOS OS RELATÓRIOS
# =====================================================
@app.route("/monthly_reports", methods=["GET"])
def monthly_reports_list():
    reports = MonthlyReport.query.order_by(MonthlyReport.generated_date.desc()).all()
    return render_template("monthly_reports_list.html", reports=reports)

# =====================================================
# Rota para atualizar os Custos Fixos via Modal
# =====================================================
@app.route("/update_fixed_costs", methods=["POST"])
def update_fixed_costs():
    vivo = request.form.get("vivo")
    va = request.form.get("va")
    try:
        vivo_val = float(vivo.replace(",", "."))
    except:
        vivo_val = 0.0
    try:
        va_val = float(va.replace(",", "."))
    except:
        va_val = 0.0
    fixed_cost = FixedCost.query.get(1)
    if not fixed_cost:
        fixed_cost = FixedCost(vivo=vivo_val, va=va_val)
        db.session.add(fixed_cost)
    else:
        fixed_cost.vivo = vivo_val
        fixed_cost.va = va_val
    db.session.commit()
    flash("Custos fixos atualizados!", "success")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)
