# seed.py
from app import app, db
from models import Commission, Expense
import random

def seed_database():
    with app.app_context():
        # Insere 10 entradas de Comissão
        commissions_data = [
            {"name": "Comissão 1", "original_value": 1500, "factor": 0.1, "status": "paga", "month": 1, "year": 2025},
            {"name": "Comissão 2", "original_value": 2000, "factor": 0.3, "status": "aguardando", "month": 2, "year": 2025},
            {"name": "Comissão 3", "original_value": 3000, "factor": 0.5, "status": "em execução", "month": 3, "year": 2025},
            {"name": "Comissão 4", "original_value": 2500, "factor": 0.1, "status": "paga", "month": 4, "year": 2025},
            {"name": "Comissão 5", "original_value": 1800, "factor": 0.3, "status": "aguardando", "month": 5, "year": 2025},
            {"name": "Comissão 6", "original_value": 2200, "factor": 0.5, "status": "em execução", "month": 6, "year": 2025},
            {"name": "Comissão 7", "original_value": 2700, "factor": 0.1, "status": "paga", "month": 7, "year": 2025},
            {"name": "Comissão 8", "original_value": 3100, "factor": 0.3, "status": "aguardando", "month": 8, "year": 2025},
            {"name": "Comissão 9", "original_value": 1950, "factor": 0.5, "status": "em execução", "month": 9, "year": 2025},
            {"name": "Comissão 10", "original_value": 2600, "factor": 0.1, "status": "paga", "month": 10, "year": 2025},
        ]
        for data in commissions_data:
            comissao = Commission(
                name=data["name"],
                original_value=data["original_value"],
                factor=data["factor"],
                status=data["status"],
                month=data["month"],
                year=data["year"],
                reported=False  # Não reportada ainda
            )
            db.session.add(comissao)
        
        # Insere 10 entradas de Despesa
        expenses_data = [
            {"name": "Despesa 1", "value": 100, "month": 1, "year": 2025, "is_recurring": False, "installment_info": ""},
            {"name": "Despesa 2", "value": 150, "month": 2, "year": 2025, "is_recurring": True, "installment_info": ""},
            {"name": "Despesa 3", "value": 200, "month": 3, "year": 2025, "is_recurring": False, "installment_info": ""},
            {"name": "Despesa 4", "value": 250, "month": 4, "year": 2025, "is_recurring": True, "installment_info": ""},
            {"name": "Despesa 5", "value": 300, "month": 5, "year": 2025, "is_recurring": False, "installment_info": ""},
            {"name": "Despesa 6", "value": 350, "month": 6, "year": 2025, "is_recurring": True, "installment_info": ""},
            {"name": "Despesa 7", "value": 400, "month": 7, "year": 2025, "is_recurring": False, "installment_info": ""},
            {"name": "Despesa 8", "value": 450, "month": 8, "year": 2025, "is_recurring": True, "installment_info": ""},
            {"name": "Despesa 9", "value": 500, "month": 9, "year": 2025, "is_recurring": False, "installment_info": ""},
            {"name": "Despesa 10", "value": 550, "month": 10, "year": 2025, "is_recurring": True, "installment_info": ""},
        ]
        for data in expenses_data:
            despesa = Expense(
                name=data["name"],
                value=data["value"],
                month=data["month"],
                year=data["year"],
                is_recurring=data["is_recurring"],
                installment_info=data["installment_info"]
            )
            db.session.add(despesa)
        
        db.session.commit()
        print("Banco de dados semeado com 20 entradas de teste!")

if __name__ == "__main__":
    seed_database()
