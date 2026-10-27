import mysql.connector

# Conectar ao banco
def conectar():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="584752258",
    database="agenda_db"
 )   

# Criar tabela se não existir
def criar_tabela():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contatos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100),
        cpf VARCHAR(20),
        telefone VARCHAR(20),
        endereco VARCHAR(200)
    )
    """)
    conn.commit()
    conn.close()

# Inserir contato
def inserir_contato(nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contatos (nome, cpf, telefone, endereco) VALUES (%s, %s, %s, %s)",
                   (nome, cpf, telefone, endereco)
    )               
    conn.commit()
    conn.close()
    
    
    # buscar contato por cpf 
def buscar_contatos(termo):
    conn = conectar()
    cursor = conn.cursor()
    consulta = "SELECT * FROM contatos WHERE nome LIKE %s OR cpf LIKE %s"
    cursor.execute(consulta, (f"%{termo}%", f"%{termo}%"))
    resultados = cursor.fetchall()
    conn.close()
    return resultados
    
    

def atualizar_contato(id, nome, cpf, telefone, endereco):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE contatos
        SET nome = %s, cpf = %s, telefone = %s, endereco = %s
        WHERE id = %s
""", (nome, cpf, telefone, endereco, id)) 
    conn.commit()
    conn.cursor()    
    

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
    cursor.execute("DELETE FROM contatos WHERE id = %s",(id,))
    conn.commit()
    conn.cursor()    

def buscar_avancado(nome = None, cpf=None, telefone=None):
    conn = conectar()
    cursor = conn.cursor()
    
    
    consulta = "SELECT * FROM contatos WHERE 1=1"
    parametros = []
    
    if nome:
        consulta += " AND nome LIKE %s"
        parametros.append(f"%{nome}%")
    if cpf:
        consulta += " AND cpf LIKE %s"
        parametros.append(f"%{nome}%")
    if telefone:
        consulta += " AND telefone LIKE %s"
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

import csv
import pandas as pd

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


import hashlib

def cadastrar_usuario(username, senha, role="user"):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute(
        "INSERT INTO usuarios (username, senha,role) VALUES (%s, %s, %s)",
        (username, senha_hash,role)
    )
    conexao.commit()
    conn.close()

def validar_login(username, senha):
    conexao = conectar()
    cursor = conexao.cursor()
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    cursor.execute(
        "SELECT * FROM usuarios WHERE username = %s AND senha =%s",
        (username, senha_hash)
)
    resultado = cursor.fetchone()
    conexao.close()
    return resultado[0] if resultado else None    