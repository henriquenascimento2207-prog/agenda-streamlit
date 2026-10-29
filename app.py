import streamlit as st
import db  # importa o módulo db.py

st.title("Agenda de Contatos")

#Flag para controlar exibição de login 
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False 
    
#botão discreto para abrir o login
if st.sidebar.button("Login"):
    st.session_state["show_login"] = True 
    
#campos de login (aparecem só se flag estiver ativa)
if st.session_state["show_login"]:
    st.sidebar.subheader("Faça seu Login")
    username = st.sidebar.text_input("Usuário")
    senha = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        role = db.validar_login(username, senha)
        if role:
            st.session_state["Usuario"] = username
            st.session_state["role"] = role
            st.success(f"Bem-Vindo, {username} ({role})")
            st.session_state["show_login"] = False # esconde loguin depois de entrar 
        else: 
            st.error("Usuário ou senha inválidos")

# --- Barreira de acesso ---
if "role" in st.session_state:
    if st.session_state["role"] == "admin":
        st.subheader("Funções de Administração")
        st.write("Exportar, buscar, remover contatos...")
        # funções do admin

        st.subheader("Cadastro de Usuário")
        st.write("Formulário de cadastro disponível para todos.")
        # formulário

    elif st.session_state["role"] == "user":
        st.subheader("Agenda de Contatos")
        st.write("Funções comuns de cadastro e consulta...")
        # funções do usuário comum

else:
    # sem login → só cadastro
    st.subheader("Cadastro de Usuário")
    st.write("Formulário de cadastro disponível para todos.")


#controle de permissões
if 'role' in st.session_state:
    if st.session_state["role"] == "admin":
        st.subheader("Funções de Adiministração")
        st.write("Aqui ficam as funções exclusivas do administrador.")
        
        #esportação backup, etc
    elif st.session_state["role"] == "user":
        st.subheader("Agenda de Contatos")
        st.write("Aqui ficam as funções comuns de cadastro e consulta.")
#cadastro, listagem, edição, exclusão
else :
    st.warning("Faça login para acessar a agenda.")     


# Criar tabela ao iniciar
db.criar_tabela()

st.title(" Agenda com Banco de Dados")
# Formulário para adicionar contato
with st.form("novo_contato"):
    nome = st.text_input("Nome")
    cpf = st.text_input("CPF")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    submit = st.form_submit_button("Adicionar")

    if submit:
        db.inserir_contato(nome, cpf, telefone, endereco)
        st.success(f"Contato {nome} adicionado com sucesso!")

# Mostrar contatos cadastrados
st.subheader("📋 Lista de Contatos")
 
opcao_ordem = st.radio(
    "Ordenar contatos por:",
    ("ID", "Nome", "CPF")

)
if opcao_ordem == "Nome":
    contatos = db.listar_contatos_por_nome()
    
elif opcao_ordem == "CPF":
    contatos = db.listar_contatos_por_cpf()

else:
    contatos = db.listar_contatos()    

if contatos:
    for contato in contatos:
        st.write(f"{contato[0]} - {contato[1]} | CPF: {contato[2]} | Tel: {contato[3]} | Endereço: {contato[4]}")
else:
    st.info("Nenhum contato cadastrado ainda.")
    
    
#seção de exportação
st.subheader("Exportar Contatos")

if st.button("Exportar para CSV"):
    arquivo = db.exportar_contatos_csv()
    st.success(f"Contatos exportados para {arquivo}")

if st.button("Exportar para Excel"):
    arquivo = db.exportar_contatos_excel()
    st.success(f"Contatos exportados para {arquivo}")    
    
    
#buscar por nome ou cpf 
st.subheader("Buscar Contato")
termo = st.text_input("Digite nome ou CPF para buscar")
if termo:
    resultados = db.buscar_contatos(termo)
    if resultados:
        for contato in resultados:
            st.write(f"{contato[0]} - {contato[1]} - | CPF: {contato[2]} - | Tel: {contato[3]} | Endereço: {contato[3]}")
    else: 
        st.warning("Nenhum contato encontrado ainda.")        

# Ações gerais no final da lista
st.subheader("⚙️ Ações")

# Inicializar estado
if "show_update" not in st.session_state:
    st.session_state.show_update = False
if "show_delete" not in st.session_state:
    st.session_state.show_delete = False

# Botão Atualizar
if st.button("Atualizar"):
    st.session_state.show_update = True

if st.session_state.show_update:
    id_update = st.number_input("Digite o ID do contato que deseja atualizar", min_value=1, step=1)
    contato = next((c for c in contatos if c[0] == id_update), None)

    if contato:
        novo_nome = st.text_input("Nome", contato[1])
        novo_cpf = st.text_input("CPF", contato[2])
        novo_telefone = st.text_input("Telefone", contato[3])
        novo_endereco = st.text_input("Endereço", contato[4])

        if st.button("Confirmar atualização"):
            db.atualizar_contato(id_update, novo_nome, novo_cpf, novo_telefone, novo_endereco)
            st.success(f"Contato com ID {id_update} atualizado com sucesso!")
            st.session_state.show_update = False  # fecha o formulário
    else:
        st.error("ID não encontrado.")

# Botão Remover
if st.button("Remover"):
    st.session_state.show_delete = True

if st.session_state.show_delete:
    id_delete = st.number_input("Digite o ID do contato que deseja remover", min_value=1, step=1)
    if st.button("Confirmar remoção"):
        db.remover_contato(id_delete)
        st.warning(f"Contato com ID {id_delete} removido com sucesso!")
        st.session_state.show_delete = False  # fecha o formulário

        

   
else:
    st.info("Nenhum contato cadastrado ainda.")     

import os

if os.path.exists("agenda.db"):
    with open("agenda.db", "rb") as f:
        st.download_button(
            label="Baixar Base de Dados (agenda.db)",
            data=f,
            file_name="agenda.db",
            mime="application/octet-stream",
        )