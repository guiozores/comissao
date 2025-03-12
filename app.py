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
    calcula o número de meses decorridos entre a data de lançamento e o relatório.
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
                diff = (report_year - e.year) * 12 + (report_month - e.month)
                current_installment = diff + 1
                if current_installment >= 1 and current_installment <= total_installments:
                    e.installment_info = f"{current_installment}/{total_installments}"
                    filtered.append(e)
            else:
                diff = (report_year - e.year) * 12 + (report_month - e.month)
                if diff >= 0:
                    filtered.append(e)
        else:
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
    filter_month_year = request.args.get("filter_month_year")  # Ex: "YYYY-MM"
    filter_year = request.args.get("filter_year")
    page_comm = request.args.get("page_comm", 1, type=int)
    page_exp = request.args.get("page_exp", 1, type=int)
    
    per_page = 8  # Exibir 8 itens por página

    # Query para Comissões (ordenadas por ano e mês em ordem decrescente)
    commissions_query = Commission.query
    if filter_mode == "month" and filter_month_year:
        parts = filter_month_year.split("-")
        if len(parts) == 2:
            y = int(parts[0])
            m = int(parts[1])
            commissions_query = commissions_query.filter(Commission.year == y, Commission.month == m)
    elif filter_mode == "year" and filter_year:
        commissions_query = commissions_query.filter(Commission.year == int(filter_year))
    # Novamente aqui.
    filter_name = request.args.get("filter_name")
    if filter_name:
        commissions_query = commissions_query.filter(Commission.name.ilike(f"%{filter_name}%"))
    commissions_query = commissions_query.order_by(Commission.year.desc(), Commission.month.desc())
    comm_pagination = commissions_query.paginate(page=page_comm, per_page=per_page, error_out=False)

    # Query para despesas
    expenses_query = Expense.query
    if filter_mode == "month" and filter_month_year:
        parts = filter_month_year.split("-")
        if len(parts) == 2:
            y = int(parts[0])
            m = int(parts[1])
            expenses_query = expenses_query.filter(Expense.year == y, Expense.month == m)
    elif filter_mode == "year" and filter_year:
        expenses_query = expenses_query.filter(Expense.year == int(filter_year))
    filter_expense_name = request.args.get("filter_expense_name")
    if filter_expense_name:
        expenses_query = expenses_query.filter(Expense.name.ilike(f"%{filter_expense_name}%"))
    expenses_query = expenses_query.order_by(Expense.year.desc(), Expense.month.desc())
    exp_pagination = expenses_query.paginate(page=page_exp, per_page=per_page, error_out=False)

    return render_template("dashboard.html", 
                           commissions=comm_pagination.items, 
                           expenses=exp_pagination.items,
                           comm_pagination=comm_pagination,
                           exp_pagination=exp_pagination,
                           filter_mode=filter_mode,
                           filter_month_year=filter_month_year,
                           filter_year=filter_year,
                           filter_name=filter_name)

# -------------------------------
# CRUD de Comissões (Dashboard)
# -------------------------------
@app.route("/dashboard/commission/new", methods=["POST"])
def commission_new():
    month_year = request.form.get("month_year")
    name = request.form.get("name")
    original_value_str = request.form.get("original_value")
    factor_str = request.form.get("factor")
    company_status = request.form.get("company_status")
    employee_status = request.form.get("employee_status")

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
        company_status=company_status,
        employee_status=employee_status,
        reported=False
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
    company_status = request.form.get("company_status")
    employee_status = request.form.get("employee_status")

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
    commission.company_status = company_status
    commission.employee_status = employee_status

    db.session.commit()
    flash("Comissão atualizada com sucesso!", "success")
    
    # Recupera parâmetros ocultos para manter o estado
    page_comm = request.form.get("page_comm", type=int)
    filter_mode = request.form.get("filter_mode")
    filter_month_year = request.form.get("filter_month_year")
    filter_year = request.form.get("filter_year")
    
    return redirect(url_for("dashboard",
                            filter_mode=filter_mode,
                            filter_month_year=filter_month_year,
                            filter_year=filter_year,
                            page_comm=page_comm))

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
        
        # Comissões selecionadas
        selected_commission_ids = request.form.getlist("commission_ids", type=int)
        commissions = Commission.query.filter(Commission.id.in_(selected_commission_ids)).all()
        
        # Despesas não recorrentes do período
        normal_expenses = Expense.query.filter_by(month=report_month, year=report_year, is_recurring=False).all()
        # Todas as despesas recorrentes
        recurring_expenses = Expense.query.filter_by(is_recurring=True).all()
        final_expenses = normal_expenses + recurring_expenses

        # Despesas extras inseridas via textarea
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
                db.session.flush()
                final_expenses.append(new_exp)
            db.session.commit()

        # Soma de comissões e despesas
        total_comm = sum(c.computed_value for c in commissions)
        total_exp = sum(e.value for e in final_expenses)
        
        # >>>> NOVO: recupera custos fixos e soma ao total de despesas <<<<
        fixed_cost = FixedCost.query.get(1)
        vivo = fixed_cost.vivo if fixed_cost else 0.0
        va = fixed_cost.va if fixed_cost else 0.0
        cost_fixed = vivo + va
        
        # Ajusta total de despesas para incluir os custos fixos
        total_expenses_with_fixed = total_exp + cost_fixed
        
        # Grand total = comissões + despesas + custos fixos
        grand_total = total_comm + total_expenses_with_fixed

        # Converte comissões e despesas para JSON (snapshot)
        commissions_data = json.dumps([
            {
                "id": c.id,
                "name": c.name,
                "month": c.month,
                "year": c.year,
                "original_value": c.original_value,
                "factor": c.factor,
                "company_status": c.company_status,
                "employee_status": c.employee_status,
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

        # Salva o relatório, incluindo a soma atualizada
        report = MonthlyReport(
            report_month=report_month,
            report_year=report_year,
            total_commissions=total_comm,
            total_expenses=total_expenses_with_fixed,  # Despesas + Vivo + VA
            grand_total=grand_total,                   # Soma final com custos fixos
            commissions_data=commissions_data,
            expenses_data=expenses_data
        )
        db.session.add(report)
        db.session.commit()

        # Marcar as comissões como reportadas
        for c in commissions:
            c.reported = True
        db.session.commit()

        flash("Relatório gerado com sucesso!", "success")
        return redirect(url_for("monthly_report_view", report_id=report.id))
    
    # GET
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
    fixed_cost = FixedCost.query.get(1)
    vivo = fixed_cost.vivo if fixed_cost else 0.0
    va = fixed_cost.va if fixed_cost else 0.0
    return render_template("monthly_report_view.html",
                           report=report,
                           commissions_data=commissions_data,
                           expenses_data=expenses_data,
                           fixed_vivo=vivo,
                           fixed_va=va)

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

@app.route("/monthly_reports", methods=["GET"])
def monthly_reports_list():
    reports = MonthlyReport.query.order_by(MonthlyReport.generated_date.desc()).all()
    return render_template("monthly_reports_list.html", reports=reports)

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

@app.route("/commission_balance", methods=["GET"])
def commission_balance():
    """
    Rota para exibir o balanço de comissões com filtros.
    Permite filtrar por ano, mês, status da empresa e status do funcionário.
    Calcula o valor total das comissões filtradas.
    """
    filter_year = request.args.get("filter_year")
    filter_month = request.args.get("filter_month")
    filter_company_status = request.args.get("filter_company_status")
    filter_employee_status = request.args.get("filter_employee_status")
    
    commissions_query = Commission.query
    if filter_year and filter_year != "all":
        commissions_query = commissions_query.filter(Commission.year == int(filter_year))
    if filter_month and filter_month != "all":
        commissions_query = commissions_query.filter(Commission.month == int(filter_month))
    if filter_company_status and filter_company_status != "all":
        commissions_query = commissions_query.filter(Commission.company_status == filter_company_status)
    if filter_employee_status and filter_employee_status != "all":
        commissions_query = commissions_query.filter(Commission.employee_status == filter_employee_status)
    filter_name = request.args.get("filter_name")
    if filter_name:
        commissions_query = commissions_query.filter(Commission.name.ilike(f"%{filter_name}%"))
    
    commissions = commissions_query.order_by(Commission.year.desc(), Commission.month.desc()).all()
    total_value = sum(comm.computed_value for comm in commissions)
    
    years = db.session.query(Commission.year).distinct().order_by(Commission.year.desc()).all()
    years = [year[0] for year in years]
    months = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"),
        (5, "Maio"), (6, "Junho"), (7, "Julho"), (8, "Agosto"),
        (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]
    statuses_company = [
        ("previsto", "Previsto"),
        ("em execução", "Em Execução"),
        ("medição aprovada", "Medição Aprovada"),
        ("em caixa", "Em Caixa"),
        ("pago", "Pago")
    ]
    statuses_employee = [
        ("previsto", "Previsto"),
        ("aguardando pagamento", "Aguardando Pagamento"),
        ("pago", "Pago")
    ]
    
    return render_template("commission_balance.html",
                           commissions=commissions,
                           total_value=total_value,
                           years=years,
                           months=months,
                           statuses_company=statuses_company,
                           statuses_employee=statuses_employee,
                           filter_year=filter_year,
                           filter_month=filter_month,
                           filter_company_status=filter_company_status,
                           filter_employee_status=filter_employee_status)

if __name__ == "__main__":
    app.run(debug=True)
