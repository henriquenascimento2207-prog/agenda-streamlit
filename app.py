import streamlit as st
import db

# 1. Cria a tabela e o admin padrão ao iniciar
db.criar_tabela()

st.title("Agenda de Contatos")

# 2. Inicializa o estado da sessão se não existir
if "show_login" not in st.session_state:
    st.session_state["show_login"] = False
if "role" not in st.session_state:
    st.session_state["role"] = None

# 3. Botão e formulário de login na barra lateral
if st.sidebar.button("Login"):
    st.session_state["show_login"] = True

if st.session_state["show_login"] and not st.session_state["role"]:
    st.sidebar.subheader("Faça seu Login")
    username = st.sidebar.text_input("Usuário", key="input_user")
    senha = st.sidebar.text_input("Senha", type="password", key="input_senha")
    
    if st.sidebar.button("Entrar"):
        role = db.validar_login(username, senha)
        if role:
            st.session_state["Usuario"] = username
            st.session_state["role"] = role
            st.sidebar.success(f"Bem-Vindo, {username} ({role})")
            st.session_state["show_login"] = False
            st.rer() if hasattr(st, "rer") else st.rerun()
        else:
            st.sidebar.error("Usuário ou senha inválidos")

# Se já estiver logado, mostra opção de sair na barra lateral
if st.session_state["role"]:
    st.sidebar.write(f"Conectado como: **{st.session_state['Usuario']}**")
    if st.sidebar.button("Sair / Logout"):
        st.session_state["role"] = None
        st.session_state["Usuario"] = None
        st.rerun()

# ==========================================
# ÁREA PÚBLICA (Disponível para qualquer um)
# ==========================================
st.subheader("Cadastro de Novo Contato")
with st.form("novo_contato"):
    nome = st.text_input("Nome")
    cpf = st.text_input("CPF")
    telefone = st.text_input("Telefone")
    endereco = st.text_input("Endereço")
    submit = st.form_submit_button("Adicionar")

    if submit:
        if nome and telefone:
            db.inserir_contato(nome, cpf, telefone, endereco)
            st.success(f"Contato {nome} adicionado com sucesso!")
        else:
            st.error("Preencha pelo menos o Nome e o Telefone.")

# ==========================================
# ÁREA EXCLUSIVA DO ADMINISTRADOR
# ==========================================
if st.session_state["role"] == "admin":
    st.markdown("---")
    st.header("🔒 Painel do Administrador")

    st.subheader("📋 Lista de Contatos")
    opcao_ordem = st.radio("Ordenar contatos por:", ("ID", "Nome", "CPF"))
    
    if opcao_ordem == "Nome":
        contatos = db.listar_contatos_por_nome()
    elif opcao_ordem == "CPF":
        contatos = db.listar_contatos_por_cpf()
    else:
        contatos = db.listar_contatos()   

    if contatos:
        for contato in contatos:
            st.write(f"**ID:** {contato[0]} - **Nome:** {contato[1]} | **CPF:** {contato[2]} | **Tel:** {contato[3]} | **Endereço:** {contato[4]}")
    else:
        st.info("Nenhum contato cadastrado ainda.")
        
    st.subheader("Exportar Contatos")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Exportar para CSV"):
            arquivo = db.exportar_contatos_csv()
            st.success(f"Contatos exportados para {arquivo}")
    with col2:
        if st.button("Exportar para Excel"):
            arquivo = db.exportar_contatos_excel()
            st.success(f"Contatos exportados para {arquivo}")    
        
    st.subheader("Buscar Contato")
    termo = st.text_input("Digite nome ou CPF para buscar")
    if termo:
        resultados = db.buscar_contatos(termo)
        if resultados:
            for contato in resultados:
                st.write(f"**ID:** {contato[0]} - **Nome:** {contato[1]} | **CPF:** {contato[2]} | **Tel:** {contato[3]} | **Endereço:** {contato[4]}")
        else: 
            st.warning("Nenhum contato encontrado.")         

    st.subheader("⚙️ Gerenciar Contatos (Atualizar / Remover)")

    if "show_update" not in st.session_state:
        st.session_state.show_update = False
    if "show_delete" not in st.session_state:
        st.session_state.show_delete = False

    col_atu, col_rem = st.columns(2)
    with col_atu:
        if st.button("Atualizar Contato"):
            st.session_state.show_update = True
            st.session_state.show_delete = False
    with col_rem:
        if st.button("Remover Contato"):
            st.session_state.show_delete = True
            st.session_state.show_update = False

    if st.session_state.show_update and contatos:
        id_update = st.number_input("Digite o ID do contato que deseja atualizar", min_value=1, step=1)
        contato_atual = next((c for c in contatos if c[0] == id_update), None)

        if contato_atual:
            novo_nome = st.text_input("Novo Nome", contato_atual[1])
            novo_cpf = st.text_input("Novo CPF", contato_atual[2])
            novo_telefone = st.text_input("Novo Telefone", contato_atual[3])
            novo_endereco = st.text_input("Novo Endereço", contato_atual[4])

            if st.button("Confirmar atualização"):
                db.atualizar_contato(id_update, novo_nome, novo_cpf, novo_telefone, novo_endereco)
                st.success(f"Contato com ID {id_update} atualizado com sucesso!")
                st.session_state.show_update = False
                st.rerun()
        else:
            st.error("ID não encontrado.")

    if st.session_state.show_delete:
        id_delete = st.number_input("Digite o ID do contato que deseja remover", min_value=1, step=1)
        if st.button("Confirmar remoção"):
            db.remover_contato(id_delete)
            st.warning(f"Contato com ID {id_delete} removido com sucesso!")
            st.session_state.show_delete = False
            st.rerun()

else:
    st.markdown("---")
    st.info("ℹ️ A lista de contatos, ferramentas de busca, exportação e gestão são restritas ao Administrador. Faça login na barra lateral para aceder a essas funções.")