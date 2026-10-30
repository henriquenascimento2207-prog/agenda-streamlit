import sqlite3
import hashlib
import pandas as pd
import os

DB_NAME = "agenda.db"

def conectar():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de Contatos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cpf TEXT,
        telefone TEXT,
        endereco TEXT
    )
    """)
    
    # Tabela de Usuários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        senha TEXT,
        role TEXT
    )
    """)
    
    # Verifica se já existe admin cadastrado, senão cria o padrão
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE role = 'admin'")
    total_admin = cursor.fetchone()[0]
    
    if total_admin == 0:
        senha_hash = hashlib.sha256("1234".encode()).hexdigest()
        cursor.execute(
            "INSERT INTO usuarios (username, senha, role) VALUES (?, ?, ?)",
            ("admin", senha_hash, "admin")
        )
    
    conn.commit()
    conn.close()

def validar_login(username, senha):
    conn = conectar()
    cursor = conn.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute("SELECT role FROM usuarios WHERE username = ? AND senha = ?", (username, senha_hash))
    resultado = cursor.fetchone()
    conn.close()
    if resultado:
        return resultado[0]
    return None

def inserir_contato(nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contatos (nome, cpf, telefone, endereco) VALUES (?, ?, ?, ?)",
        (nome, cpf, telefone, endereco)
    )
    conn.commit()
    conn.close()

def listar_contatos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, telefone, endereco FROM contatos")
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_contatos_por_nome():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, telefone, endereco FROM contatos ORDER BY nome ASC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def listar_contatos_por_cpf():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cpf, telefone, endereco FROM contatos ORDER BY cpf ASC")
    dados = cursor.fetchall()
    conn.close()
    return dados

def buscar_contatos(termo):
    conn = conectar()
    cursor = conn.cursor()
    termo_like = f"%{termo}%"
    cursor.execute(
        "SELECT id, nome, cpf, telefone, endereco FROM contatos WHERE nome LIKE ? OR cpf LIKE ?",
        (termo_like, termo_like)
    )
    dados = cursor.fetchall()
    conn.close()
    return dados

def atualizar_contato(id_contato, nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE contatos SET nome = ?, cpf = ?, telefone = ?, endereco = ? WHERE id = ?",
        (nome, cpf, telefone, endereco, id_contato)
    )
    conn.commit()
    conn.close()

def remover_contato(id_contato):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contatos WHERE id = ?", (id_contato,))
    conn.commit()
    conn.close()

def exportar_contatos_csv():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM contatos", conn)
    conn.close()
    arquivo = "contatos.csv"
    df.to_csv(arquivo, index=False, encoding="utf-8-sig")
    return arquivo

def exportar_contatos_excel():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM contatos", conn)
    conn.close()
    arquivo = "contatos.xlsx"
    df.to_excel(arquivo, index=False)
    return arquivo