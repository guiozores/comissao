# config.py
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "minha_chave_secreta"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://dbuser:dbpass@localhost/comissao_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
