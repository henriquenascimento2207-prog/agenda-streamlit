import sqlite3
import csv
import pandas as pd
import hashlib

def conectar():
    # Cria ou conecta-se a um arquivo local chamado agenda.db
    conn = sqlite3.connect("agenda.db")
    return conn

# Criar tabela se não existir (Contatos e Usuários)
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
    
    # Tabela de Usuários (para a barreira de acesso/login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        senha TEXT,
        role TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# Inserir contato
def inserir_contato(nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contatos (nome, cpf, telefone, endereco) VALUES (?, ?, ?, ?)",
        (nome, cpf, telefone, endereco)
    )                
    conn.commit()
    conn.close()
    
# Buscar contato por termo
def buscar_contatos(termo):
    conn = conectar()
    cursor = conn.cursor()
    consulta = "SELECT * FROM contatos WHERE nome LIKE ? OR cpf LIKE ?"
    cursor.execute(consulta, (f"%{termo}%", f"%{termo}%"))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def atualizar_contato(id, nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contatos
        SET nome = ?, cpf = ?, telefone = ?, endereco = ?
        WHERE id = ?
    """, (nome, cpf, telefone, endereco, id)) 
    conn.commit()
    conn.close()    

# Listar contatos
def listar_contatos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contatos")
    contatos = cursor.fetchall()
    conn.close()
    return contatos
    
def remover_contato(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contatos WHERE id = ?", (id,))
    conn.commit()
    conn.close()    

def buscar_avancado(nome=None, cpf=None, telefone=None):
    conn = conectar()
    cursor = conn.cursor()
    
    consulta = "SELECT * FROM contatos WHERE 1=1"
    parametros = []
    
    if nome:
        consulta += " AND nome LIKE ?"
        parametros.append(f"%{nome}%")
    if cpf:
        consulta += " AND cpf LIKE ?"
        parametros.append(f"%{cpf}%") # Corrigido de nome para cpf
    if telefone:
        consulta += " AND telefone LIKE ?"
        parametros.append(f"%{telefone}%")

    cursor.execute(consulta, tuple(parametros))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def listar_contatos_por_nome():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contatos ORDER BY nome ASC")
    contatos = cursor.fetchall()
    conn.close()
    return contatos
    
def listar_contatos_por_cpf():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contatos ORDER BY cpf ASC")
    contatos = cursor.fetchall()
    conn.close()
    return contatos

def exportar_contatos_csv(nome_arquivo="contatos.csv"):
    contatos = listar_contatos()
    with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["ID", "Nome", "CPF", "Telefone", "Endereço"])
        for contato in contatos:
            escritor.writerow(contato)
    return nome_arquivo

def exportar_contatos_excel(nome_arquivo="contatos.xlsx"):
    contatos = listar_contatos()
    df = pd.DataFrame(contatos, columns=["ID", "Nome", "CPF", "Telefone", "Endereço"])
    df.to_excel(nome_arquivo, index=False)
    return nome_arquivo

def cadastrar_usuario(username, senha, role="user"):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO usuarios (username, senha, role) VALUES (?, ?, ?)",
        (username, senha_hash, role)
    )
    conexao.commit()
    conexao.close() # Corrigido de conn para conexao

def validar_login(username, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute(
        "SELECT * FROM usuarios WHERE username = ? AND senha = ?",
        (username, senha_hash)
    )
    resultado = cursor.fetchone()
    conexao.close()
    return resultado[0] if resultado else None