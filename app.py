import os
import streamlit as st
import db

# Configuração da página
st.set_page_config(page_title="Agenda de Contatos", page_icon="")
db.criar_tabela()

# Inicialização segura do estado da sessão
if "role" not in st.session_state:
    st.session_state["role"] = None
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# MENU DE NAVEGAÇÃO LATERAL
st.sidebar.title(" Navegação")
opcao_tela = st.sidebar.radio(
    "Escolha uma página:",
    [" Cadastrar Contato", " Painel do Administrador"]
)

# ==========================================================
# TELA 1: CADASTRO PÚBLICO DE CONTATOS
# ==========================================================
if opcao_tela == " Cadastrar Contato":
    st.title(" Agenda de Contatos")
    st.subheader("Cadastrar Novo Contato")
    st.write("Preencha os dados abaixo para adicionar um novo contato.")

    with st.form("form_novo_contato", clear_on_submit=True):
        nome = st.text_input("Nome completo")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        endereco = st.text_input("Endereço")
        
        submit = st.form_submit_button("Salvar Contato")

        if submit:
            if nome and telefone:
                db.inserir_contato(nome, cpf, telefone, endereco)
                st.success(f"Contato **{nome}** cadastrado com sucesso!")
            else:
                st.error("Por favor, preencha pelo menos o Nome e o Telefone.")

# ==========================================================
# TELA 2: PAINEL DO ADMINISTRADOR (RESTRITO)
# ==========================================================
elif opcao_tela == " Painel do Administrador":
    st.title(" Área do Administrador")

    # SE NÃO ESTIVER LOGADO COMO ADMIN -> MOSTRA LOGIN
    if st.session_state["role"] != "admin":
        st.info("Por favor, faça login com as credenciais de administrador para acessar o painel.")
        
        with st.form("form_login_admin"):
            user_input = st.text_input("Usuário")
            senha_input = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Entrar no Painel")

            if btn_entrar:
                role = db.validar_login(user_input, senha_input)
                if role:
                    st.session_state["usuario"] = user_input
                    st.session_state["role"] = "admin"
                    st.success("Login efetuado com sucesso! Atualizando...")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

    # SE JÁ ESTIVER LOGADO COMO ADMIN -> MOSTRA O PAINEL COMPLETO
    else:
        # Barra superior com informações do usuário e botão de logout
        col_user, col_logout = st.columns([3, 1])
        with col_user:
            st.success(f"Conectado como: **{st.session_state['usuario']}** (Administrador)")
        with col_logout:
            if st.button("Sair / Logout"):
                st.session_state["role"] = None
                st.session_state["usuario"] = None
                st.rerun()

        st.markdown("---")

        # --- 1. LISTA DE CONTATOS ---
        st.subheader(" Lista de Contatos Cadastrados")
        opcao_ordem = st.radio("Ordenar por:", ("ID", "Nome", "CPF"), horizontal=True, key="ordem_contatos")
        
        if opcao_ordem == "Nome":
            contatos = db.listar_contatos_por_nome()
        elif opcao_ordem == "CPF":
            contatos = db.listar_contatos_por_cpf()
        else:
            contatos = db.listar_contatos()

        if contatos:
            for c in contatos:
                st.write(f"**ID {c[0]}** | **Nome:** {c[1]} | **CPF:** {c[2]} | **Tel:** {c[3]} | **Endereço:** {c[4]}")
        else:
            st.info("Nenhum contato cadastrado no momento.")

        st.markdown("---")

        # --- 2. EXPORTAÇÃO E BUSCA ---
        col_exp, col_busca = st.columns(2)
        
        with col_exp:
            st.subheader(" Exportar Dados")
            if st.button("Exportar para CSV"):
                arq = db.exportar_contatos_csv()
                st.success(f"Exportado para {arq}")
            if st.button("Exportar para Excel"):
                arq = db.exportar_contatos_excel()
                st.success(f"Exportado para {arq}")

        with col_busca:
            st.subheader(" Buscar Contato")
            termo = st.text_input("Buscar por Nome ou CPF", key="termo_busca")
            if termo:
                resultados = db.buscar_contatos(termo)
                if resultados:
                    for c in resultados:
                        st.write(f"**ID {c[0]}** | **Nome:** {c[1]} | **Tel:** {c[3]}")
                else:
                    st.warning("Nenhum registro encontrado.")

        st.markdown("---")

        # --- 3. GERENCIAR (ATUALIZAR / REMOVER) ---
        st.subheader("⚙️ Gerenciar Registros")
        
        if "show_update" not in st.session_state:
            st.session_state.show_update = False
        if "show_delete" not in st.session_state:
            st.session_state.show_delete = False

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("Editar Contato"):
                st.session_state.show_update = True
                st.session_state.show_delete = False
        with col_b2:
            if st.button("Excluir Contato"):
                st.session_state.show_delete = True
                st.session_state.show_update = False

        # Formulário de Atualização
        if st.session_state.show_update and contatos:
            id_up = st.number_input("ID do contato para editar", min_value=1, step=1, key="id_up")
            contato_sel = next((c for c in contatos if c[0] == id_up), None)
            
            if contato_sel:
                n_nome = st.text_input("Novo Nome", contato_sel[1], key="n_nome")
                n_cpf = st.text_input("Novo CPF", contato_sel[2], key="n_cpf")
                n_tel = st.text_input("Novo Telefone", contato_sel[3], key="n_tel")
                n_end = st.text_input("Novo Endereço", contato_sel[4], key="n_end")
                
                if st.button("Salvar Alterações"):
                    db.atualizar_contato(id_up, n_nome, n_cpf, n_tel, n_end)
                    st.success("Contato atualizado com sucesso!")
                    st.session_state.show_update = False
                    st.rerun()
            else:
                st.error("ID não encontrado.")

        # Formulário de Exclusão
        if st.session_state.show_delete:
            id_del = st.number_input("ID do contato para remover", min_value=1, step=1, key="id_del")
            if st.button("Confirmar Exclusão"):
                db.remover_contato(id_del)
                st.warning("Contato removido com sucesso!")
                st.session_state.show_delete = False
                st.rerun()

# ==========================================
# BOTÃO DE BACKUP DA BASE DE DADOS (NA BARRA LATERAL)
# ==========================================
st.sidebar.markdown("---")
if os.path.exists("agenda.db"):
    with open("agenda.db", "rb") as f:
        st.sidebar.download_button(
            label=" Baixar Backup (agenda.db)",
            data=f,
            file_name="agenda.db",
            mime="application/octet-stream"
        )