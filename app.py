from flask import Flask, render_template, request, redirect, url_for, Response, send_from_directory, session, send_file
import os
from pdfkit import from_file
import random
from string import digits
import mysql.connector
from flask_mail import Mail, Message
import PySimpleGUI as sg
import json
import subprocess
from PyPDF2 import PdfFileWriter, PdfFileReader




app = Flask(__name__, static_folder='static')
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'guiaraujo2007@outlook.com'
app.config['MAIL_PASSWORD'] = 'gui28141528'
mail = Mail(app)
app.secret_key = 'sua_chave_secreta_aqui'



@app.route('/', methods=['GET'])
def conexao():
    return render_template('login-perfil1.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/', methods=['POST'])
def vendas_html():
    user = request.form.get('nome')
    senha = request.form.get('password')

    # Variaveis de senha
    user1 = "teste4321"
    senha1 = "senha4321"

    # Função de conexão
    if user == user1 and senha == senha1:
        return redirect('/menu')
    else:
        return conexao()
    





@app.route('/cliente_app')
def cliente_app(): 
    return render_template('clientes.html') and exibir_tabela()




# Banco de dados para Tabela HTML
@app.route('/acao')
def exibir_tabela():
    
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    cursor = conexao.cursor()
    # Executa uma consulta SQL para recuperar os dados da tabela
    cursor.execute('SELECT Id_nome, nome, tipo, cnpj, cpf, telefone, email, id_endereco FROM tb_clientes')

    # Obtém os resultados da consulta
    resultados = cursor.fetchall()

    # Fecha o cursor
    cursor.close()

    # Renderiza a tabela HTML com os resultados
    return render_template('clientes.html', resultados=resultados)

@app.route('/buscar', methods=['POST'])
def buscar_dados():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
        
    pesquisa = request.form['pesquisa']
    filtro = request.form['filtro']

    # Conectar ao banco de dados
    cursor = conexao.cursor()

    # Executar consulta SQL baseada nos valores do formulário
    if filtro == 'opcao1':
        pesquisa = pesquisa.replace("'", "''")  # Lidar com apóstrofos
        pesquisa = pesquisa.replace("%", r"\%")  # Escapar caracteres curinga %
        query = "SELECT * FROM tb_clientes WHERE nome LIKE '%{}%' OR nome LIKE '%{}%'".format(pesquisa, pesquisa)
    elif filtro == 'opcao2':
        query = "SELECT * FROM tb_clientes WHERE Id_nome = '{}'".format(pesquisa)
    elif filtro == 'opcao3':
        query = "SELECT * FROM tb_clientes WHERE nome = '{}'".format(pesquisa)
    elif filtro == 'opcao4':
        query = "SELECT * FROM tb_clientes WHERE tipo = '{}'".format(pesquisa)
    elif filtro == 'opcao5':
        query = "SELECT * FROM tb_clientes WHERE cnpj = '{}'".format(pesquisa)
    elif filtro == 'opcao36':
        query = "SELECT * FROM tb_clientes WHERE cpf = '{}'".format(pesquisa)
    elif filtro == 'opcao7':
        query = "SELECT * FROM tb_clientes WHERE telefone = '{}'".format(pesquisa)
    elif filtro == 'opcao8':
        query = "SELECT * FROM tb_clientes WHERE email = '{}'".format(pesquisa)
    # Adicione mais opções de filtro conforme necessário

    cursor.execute(query)
    resultados = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    # Retornar os resultados para a página web
    return render_template('clientes.html', resultados=resultados)

@app.route('/')
def delete_cliente():
    return '''
    <html>
    <head>
    </head>
    <body>
        <button onclick="confirmarExclusao()">Excluir</button>
        <script>
            function confirmarExclusao() {
                // Exibe a caixa de diálogo de confirmação
                var confirmacao = confirm("Tem certeza que deseja excluir?");

                // Verifica se o usuário confirmou a exclusão
                if (confirmacao) {
                    // Chama a rota do Flask para executar a função Python
                    window.location.href = '/excluir';
                } else {
                    // Executa a lógica para cancelar a exclusão
                    console.log("Exclusão cancelada");
                }
            }
        </script>
    </body>
    </html>
    '''


# Exclusão funções:
@app.route('/excluir/<int:id_cliente>', methods=['POST'])
def excluir_cliente(id_cliente):
        

    if delete_cliente():
            conexao = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='sampanature',
        )
            # Conecte-se ao banco de dados
            cursor = conexao.cursor()

            # Execute a consulta SQL para excluir o cliente
            cursor.execute('DELETE FROM tb_clientes WHERE Id_nome = %s', (id_cliente,))

            # Commit a transação
            conexao.commit()

            # Feche o cursor e a conexão com o banco de dados
            cursor.close()
            conexao.close()

            # Redirecione para a página de exibição da tabela
            return redirect('/acao')
    else:
        return redirect('/acao')













@app.route('/adicionar_cliente', methods=['POST'])
def adicionar_cliente():
    # Obter os dados do formulário do cliente
    nome = request.form['nome']
    tipo = request.form['tipo']
    cnpj = request.form['cnpjcliente']
    cpf = request.form['cpfcliente']
    telefone = request.form['telefone']
    email = request.form['email']
    id_endereco = request.form['idend']

    # Obter os dados do formulário do endereço
    rua = request.form['idrua']
    numero = request.form['idnumerorua']
    cep = request.form['idcep']
    cidade = request.form['idcidade']
    estado = request.form['iduf']
    complemento = request.form['idcompletemento']


    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM tb_clientes WHERE cnpj = %s AND cpf = %s', (cnpj, cpf)) 
    cursor_procura = cursor.fetchall()  # Ou fetchone(), dependendo da sua necessidade de leitura


    # Consulta para obter o maior valor da coluna id_endereco
    cursor.execute("SELECT MAX(id_endereco) FROM tb_enderecos")
    maior_id_endereco = cursor.fetchone()[0]

    # Incrementa o valor obtido em 1 para obter o novo valor para id_endereco
    idend = maior_id_endereco + 1

    # Comando de inserção para a tabela 'tb_clientes'
    comando_sql_cliente = "INSERT INTO tb_clientes (nome, tipo, cnpj, cpf, telefone, email, id_endereco) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    valores_cliente = (nome, tipo, cnpj, cpf, telefone, email, idend)
    cursor.execute(comando_sql_cliente, valores_cliente)
    result = cursor.fetchone()
    print(result)
    # Comando de inserção para a tabela 'tb_enderecos'
    comando_sql_endereco = "INSERT INTO tb_enderecos (rua, numero, cep, cidade, uf, complemento) VALUES (%s, %s, %s, %s, %s, %s)"
    valores_endereco = (rua, numero, cep, cidade, estado, complemento)
    cursor.execute(comando_sql_endereco, valores_endereco)

    # Confirmar a transação e fechar a conexão
    conexao.commit()
    cursor.close()
    conexao.close()

    return redirect(url_for('clientes'))








@app.route('/clientes')
def clientes():
    
    # Realizar a inserção dos dados no MySQL
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()

    cursor.execute('SELECT Id_nome, nome, tipo, cnpj, cpf, telefone, email, id_endereco FROM tb_clientes') 
    
    # Obtém os resultados da consulta
    resultados = cursor.fetchall()
    # Confirmar a transação e fechar a conexão
    conexao.commit()
    cursor.close()

    return render_template('clientes.html', resultados=resultados)








#   _._     _,-'""`-._
# (,-.`._,'(       |\`-/|
#     `-.-' \ )-`( , o o)
#           `-    \`_`"'-



# Configuração da página de Endereços
@app.route('/enderecos_app') # Rota Principal
def enderecos_app():
    return render_template('enderecos.html') and exibir_tabela1()

# Banco de dados para Tabela HTML
@app.route('/acao1')
def exibir_tabela1():
    
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    cursor = conexao.cursor()
    # Executa uma consulta SQL para recuperar os dados da tabela
    cursor.execute('SELECT id_endereco, rua, numero, cep, cidade, uf, complemento FROM tb_enderecos')

    # Obtém os resultados da consulta
    resultados = cursor.fetchall()

    # Fecha o cursor
    cursor.close()

    # Renderiza a tabela HTML com os resultados
    return render_template('enderecos.html', resultados=resultados)


@app.route('/buscarum', methods=['POST'])
def buscar_dados1():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
        
    pesquisa = request.form['pesquisa']
    filtro = request.form['filtro']

    # Conectar ao banco de dados
    cursor = conexao.cursor()

    # Executar consulta SQL baseada nos valores do formulário
    if filtro == 'opcao1':
        pesquisa = pesquisa.replace("'", "''")  # Lidar com apóstrofos
        pesquisa = pesquisa.replace("%", r"\%")  # Escapar caracteres curinga %
        query = "SELECT * FROM tb_enderecos WHERE id_endereco LIKE '%{}%' OR rua LIKE '%{}%' OR numero LIKE '%{}%' OR cep LIKE '%{}%' OR cidade LIKE '%{}%' OR uf LIKE '%{}%'".format(pesquisa, pesquisa, pesquisa, pesquisa, pesquisa, pesquisa)
    elif filtro == 'opcao2':
        query = "SELECT * FROM tb_enderecos WHERE id_endereco LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao3':
        query = "SELECT * FROM tb_enderecos WHERE rua LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao4':
        query = "SELECT * FROM tb_enderecos WHERE numero LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao5':
        query = "SELECT * FROM tb_enderecos WHERE cep LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao6':
        query = "SELECT * FROM tb_enderecos WHERE cidade LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao7':
        query = "SELECT * FROM tb_enderecos WHERE uf LIKE '%{}%'".format(pesquisa)
    # Adicione mais opções de filtro conforme necessário

    cursor.execute(query)
    resultados = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    # Retornar os resultados para a página web
    return render_template('enderecos.html', resultados=resultados)






def delete_cliente1(id_endereco):
    # Conecte-se ao banco de dados
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    # Crie um cursor
    cursor = conexao.cursor()

    # Execute a consulta SQL para excluir o cliente
    cursor.execute('DELETE FROM tb_enderecos WHERE id_endereco = %s', (id_endereco,))

    # Commit a transação
    conexao.commit()

    # Feche o cursor e a conexão com o banco de dados
    cursor.close()
    conexao.close()

    return True

@app.route('/excluir1/<int:id_endereco>', methods=['POST'])
def excluir_cliente1(id_endereco):
    if delete_cliente1(id_endereco):
        # Redirecione para a página de exibição da tabela
        return redirect(url_for('enderecos_app'))
    else:
        # Mostre uma mensagem de erro
        return render_template('clientes.html', mensagem='Erro ao excluir o cliente.')







# Página de Estoque
@app.route('/estoque')
def estoque():
    return render_template('estoque.html') and exibir_tabela2()




# Tabela na tela
# Banco de dados para Tabela HTML
@app.route('/acao2')
def exibir_tabela2():
    
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    cursor = conexao.cursor()
    # Executa uma consulta SQL para recuperar os dados da tabela
    cursor.execute('SELECT id_produto, nome_produto, descricao_produto, quantidade_estoque, preco_produto, peso_produto, fornecedor, status_produto FROM tb_estoque')

    # Obtém os resultados da consulta
    resultados = cursor.fetchall()

    # Fecha o cursor
    cursor.close()

    # Renderiza a tabela HTML com os resultados
    return render_template('estoque.html', resultados=resultados)


# Função de Adicionar

@app.route('/adicionar_produto', methods=['POST'])
def adicionar_produto():
    # Puxa os dados do formulário
    nome = request.form['nome']
    iddesc = request.form['iddesc']
    idquantidade = request.form['idquantidade']
    idpreco = request.form['idpreco']
    idfornecedor = request.form['idfornecedor']
    idstatus = request.form['tipo']
    idpeso = request.form.get('idpesoproduto', '')

    # Realizar a inserção dos dados no MySQL
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()

    # Comando de inserção para a tabela 'tb_clientes'
    comando_sql = "INSERT INTO tb_estoque (nome_produto, descricao_produto, quantidade_estoque, preco_produto, peso_produto, fornecedor, status_produto) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    valores = (nome, iddesc, idquantidade, idpreco, idpeso, idfornecedor, idstatus)
    cursor.execute(comando_sql, valores)

    # Obter a lista atualizada de produtos
    cursor.execute("SELECT nome_produto FROM tb_estoque")
    produtos = [produto[0] for produto in cursor.fetchall()]

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    # Retornar a lista de produtos como uma resposta JSON
    return redirect(url_for('estoque'))

@app.route('/produtos', methods=['GET'])
def obter_produtos():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()
    cursor.execute("SELECT nome_produto FROM tb_estoque WHERE quantidade_estoque > 0")
    produtos = [produto[0] for produto in cursor.fetchall()]

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    return json.dumps(produtos)

@app.route('/vendas', methods=['GET'])
def vendas():
    # Obtém a lista de produtos da rota /produtos usando a função que você definiu
    produtos = obter_produtos()

    # Renderiza o template vendas.html e passa a lista de produtos como uma variável para o template
    return render_template('vendas.html', produtos=produtos)

# Função de Exclusão
# /excluir2/
def delete_cliente2(id_produto):
    # Conecte-se ao banco de dados
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    # Crie um cursor
    cursor = conexao.cursor()

    # Execute a consulta SQL para excluir o cliente
    cursor.execute('DELETE FROM tb_estoque WHERE id_produto = %s', (id_produto,))

    # Commit a transação
    conexao.commit()

    # Feche o cursor e a conexão com o banco de dados
    cursor.close()
    conexao.close()

    return True

@app.route('/excluir2/<int:id_produto>', methods=['POST'])
def excluir_cliente2(id_produto):
    if delete_cliente2(id_produto):
        # Redirecione para a página de exibição da tabela
        return redirect(url_for('estoque'))
    else:
        # Mostre uma mensagem de erro
        return render_template('clientes.html', mensagem='Erro ao excluir o cliente.')



@app.route('/procura_estoque', methods=['POST'])
def buscar_dados2():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
        
    pesquisa = request.form['pesquisa']
    filtro = request.form['filtro']

    # Conectar ao banco de dados
    cursor = conexao.cursor()

    # Executar consulta SQL baseada nos valores do formulário
    if filtro == 'opcao1':
        pesquisa = pesquisa.replace("'", "''")  # Lidar com apóstrofos
        pesquisa = pesquisa.replace("%", r"\%")  # Escapar caracteres curinga %
        query = "SELECT * FROM tb_estoque WHERE id_produto LIKE '%{}%' OR nome_produto LIKE '%{}%' OR descricao_produto LIKE '%{}%' OR fornecedor LIKE '%{}%' OR preco_produto LIKE '%{}%' OR status_produto LIKE '%{}%' ".format(pesquisa, pesquisa, pesquisa, pesquisa, pesquisa, pesquisa)
    elif filtro == 'opcao2':
        query = "SELECT * FROM tb_estoque WHERE id_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao3':
        query = "SELECT * FROM tb_estoque WHERE nome_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao4':
        query = "SELECT * FROM tb_estoque WHERE descricao_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao5':
        query = "SELECT * FROM tb_estoque WHERE quantidade_estoque LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao6':
        query = "SELECT * FROM tb_estoque WHERE preco_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao7':
        query = "SELECT * FROM tb_estoque WHERE fornecedor LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao8':
        query = "SELECT * FROM tb_estoque WHERE status_produto LIKE '%{}%'".format(pesquisa)
    # Adicione mais opções de filtro conforme necessário

    cursor.execute(query)
    resultados = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    # Retornar os resultados para a página web
    return render_template('estoque.html', resultados=resultados)








# Configuração página de Relatórios
@app.route('/relatorios')
def relatoriosapp():
    return render_template('relatorios.html') 












#   _._     _,-'""`-._
# (,-.`._,'(       |\`-/|
#     `-.-' \ )-`( , o o)
#           `-    \`_`"'-

# Configuração Página de Vendas
@app.route('/vendas_page')
def vendas_page():
    # Realizar a inserção dos dados no MySQL
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()

    cursor.execute('SELECT numero_pedido, data_produto, produto, status_produto, nome_cliente, unidade, desconto, valor_final FROM tb_vendas')

    # Obtém os resultados da consulta
    resultados = cursor.fetchall()

    # Feche o cursor após todas as consultas
    cursor.close()
    # Feche a conexão ao final
    conexao.close()

    return render_template('vendas.html', resultados=resultados)

@app.route('/dec_baixando')
def pag_declaracao():
    return render_template('declaracaobaixar.html')

@app.route('/decl_baixar')
def pag_declaracao1():
    nome_arquivo = session.get('nome_arquivo')

    if nome_arquivo:
        return redirect(url_for('download_arquivo', nome_arquivo=nome_arquivo))
    else:
        return "Nome do arquivo não encontrado na sessão.", 400




@app.route('/vendas_adicao', methods=['POST'])
def funcao_addvendas():
    from decimal import Decimal, getcontext
    data = request.form['data']
    opcoes_label = request.form['produto']
    cliente = request.form['cliente']
    unidade1 = request.form['unidade']  # Converta para inteiro
    desc = request.form['desc']  # Converta para float

    # Realizar a inserção dos dados no MySQL
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()

    # Consulta nome e status do produto
    cursor.execute('SELECT nome_produto, status_produto FROM tb_estoque WHERE nome_produto = %s', (opcoes_label,))
    produto = cursor.fetchone()

    if produto:
        nome_produto, status_produto = produto

        nomecliente = "SELECT nome FROM tb_clientes WHERE cliente LIKE '%{}%'".format(cliente)

        cursor.execute('SELECT preco_produto FROM tb_estoque WHERE nome_produto = %s', (opcoes_label,))
        precoproduto_resultado = cursor.fetchone()

        if precoproduto_resultado:
            precoproduto = precoproduto_resultado[0]
        else:
            precoproduto = 0.0  # ou outro valor padrão

        # Crie o comando SQL
        comando_sql = "INSERT INTO tb_vendas (data_produto, produto, status_produto, nome_cliente, unidade, desconto, valor_final) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        valores = (data, nome_produto, status_produto, cliente, unidade1, desc, precoproduto)

        cursor.execute(comando_sql, valores)

        
        cursor.execute("SELECT quantidade_estoque FROM tb_estoque WHERE nome_produto = %s", (opcoes_label,))
        estoque_resultado = cursor.fetchone()

        if estoque_resultado:
            # Se a consulta retornar um resultado, pegue o valor do estoque
            estoque_atual = estoque_resultado[0]

            # Faça a subtração do valor do estoque atual com a quantidade informada em unidade1
            subtracao_valor = int(estoque_atual) - int(unidade1)

            # Atualize o valor do estoque na tabela tb_estoque
            cursor.execute("UPDATE tb_estoque SET quantidade_estoque = %s WHERE nome_produto = %s", (subtracao_valor, opcoes_label))

            # Commit para salvar a alteração no banco de dados
            conexao.commit()

        else:
            # Trate o caso em que o produto não foi encontrado no banco de dados
            # Pode exibir uma mensagem de erro ou redirecionar para outra página, por exemplo.
            pass

        # Confirmar a transação e fechar a conexão




        # Função do calculo de desconto
        # Recebe o atual valor do produto
        cursor.execute("SELECT preco_produto FROM tb_estoque WHERE nome_produto = %s", (opcoes_label,))
        preco_atual = cursor.fetchone()

        if preco_atual:
            # Vê o atual ID
            cursor.execute("SELECT numero_pedido FROM tb_vendas ORDER BY numero_pedido DESC LIMIT 1")
            ultimo_id_inserido = cursor.fetchone()[0]

            # Se resultar resultador, salva o valor na var
            real_preco = preco_atual[0]

            # Faz a subtração do preço da tb_estoque com o desconto
            subtracao_desc = real_preco - Decimal(desc)

            cursor.execute("UPDATE tb_vendas SET valor_final = %s WHERE numero_pedido = %s", (subtracao_desc, ultimo_id_inserido))

        else:
            pass
        

        conexao.commit()
        cursor.close()
        conexao.close()
    else:
        cursor.close()
        conexao.close()
    
    # Realizar a inserção dos dados na Declaração Fiscal
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()

    # Declaração de Conteudo
    # Parte 1 - Colocando os dados
    remetente = {
        'nome': 'Sampanature',
        'tipo': '539.815.908-99',
        'endereco': 'Rua José 12',
        'cidade': 'Embu das Artes',
        'uf': 'SP',
        'cep': '06814-020',
    }

    # Destinatario dados
    # Nome
    nomecliente = cliente # Var 

    # Consulta para obter o tipo do cliente (PJ ou PF)
    cursor.execute("SELECT tipo FROM tb_clientes WHERE nome = %s", (nomecliente,))
    tipo_cliente = cursor.fetchone() 

    if tipo_cliente:
        tipo = tipo_cliente[0]  # Obtém o tipo de cliente (PJ ou PF)

        # Consulta SQL com uma condicional CASE para selecionar cnpj ou cpf
        if tipo == 'PJ (Pessoa Juridica)':
            consulta_sql = "SELECT cnpj FROM tb_clientes WHERE nome = %s"
        else:
            consulta_sql = "SELECT cpf FROM tb_clientes WHERE nome = %s"

        # Executa a consulta
        cursor.execute(consulta_sql, (nomecliente,))
        documento_selecionado_result = cursor.fetchone()
        documento_selecionado = documento_selecionado_result[0] if documento_selecionado_result else None


    # Endereco
    # Pegar o ID_endereco
    cursor.execute("SELECT id_endereco FROM tb_clientes WHERE nome = %s", (nomecliente,))
    idend_result = cursor.fetchone()
    idend = idend_result[0] if idend_result else None

    # Pegar Endereço
    # Rua
    cursor.execute("SELECT rua FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    rua_result = cursor.fetchone()
    ruacliente = rua_result[0] if rua_result else None
    # Numero
    cursor.execute("SELECT numero FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    numerocliente_result = cursor.fetchone()
    numerocliente = numerocliente_result[0] if numerocliente_result else None


    # Cidade
    cursor.execute("SELECT cidade FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    cidade_result = cursor.fetchone()
    cidadecliente = cidade_result[0] if cidade_result else None 


    # UF
    cursor.execute("SELECT uf FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    uf_result = cursor.fetchone()
    ufcliente = uf_result[0] if uf_result else None 
    
    # CEP
    cursor.execute("SELECT cep FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    cep_result = cursor.fetchone()
    cepcliente = cep_result[0] if cep_result else None  

    # Complemento
    cursor.execute("SELECT complemento FROM tb_enderecos WHERE id_endereco = %s", (idend,))
    comp_result = cursor.fetchone()
    complemento = comp_result[0] if comp_result else None 
 
    # Peso
    cursor.execute("SELECT peso_produto FROM tb_estoque WHERE nome_produto = %s", (opcoes_label,))
    peso_result = cursor.fetchone()
    pesoproduto = peso_result[0] if peso_result else None 
    pesoproduto = int(pesoproduto) * int(unidade1)

    preco_atual = subtracao_desc * int(unidade1)
    destinatario = {
        'nome': nomecliente,
        'tipo': documento_selecionado,
        'rua': ruacliente,
        'numero': numerocliente,
        'cidade': cidadecliente,
        'complemento': '- ' + complemento,
        'uf': ufcliente,
        'cep': cepcliente,      
    }

    produto = {
        'nome': opcoes_label,
        'quantidade': unidade1,
        'peso': pesoproduto,
        'valor': preco_atual,
    }
    cursor.close()
    conexao.close()
        
    # Renderiza o template 'declaracao.html' com os dados
    rendered_template = render_template('declaracao.html', remetente=remetente, destinatario=destinatario, produto=produto)

    # Gera uma sequência de 10 números aleatórios
    numeros_aleatorios = ''.join(random.choices(digits, k=10))

    # Gera o nome de arquivo único com o número aleatório
    nome_arquivo = f"{nomecliente}_{numeros_aleatorios}.html"



    # Cria o arquivo HTML no diretório temporário
    caminho_arquivo = os.path.join(os.path.dirname(__file__), nome_arquivo)
    with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
        arquivo.write(rendered_template)

    
    # Aqui você pode definir o diretório onde deseja salvar os arquivos
    pasta_destino = 'C:/Users/Guilherme/Favorites/Links/Techouse Brasil/Perfil 1'
    
    # Move o arquivo para a pasta de destino
    novo_caminho = os.path.join(pasta_destino, nome_arquivo)
    os.rename(caminho_arquivo, novo_caminho)
    session['nome_arquivo'] = nome_arquivo

    # Redireciona o usuário para a rota '/vendas_page'
    return redirect(url_for('pag_declaracao'))

# Rota para servir o arquivo baixado
@app.route('/download/<nome_arquivo>')
def download_arquivo(nome_arquivo):
    # Abre o arquivo HTML
    pasta_destino = 'C:/Users/Guilherme/Favorites/Links/Techouse Brasil/Perfil 1'
    return send_from_directory(pasta_destino, nome_arquivo, as_attachment=True)



# Função de Exclusão
def delete_cliente3(numero_pedido):
    # Conecte-se ao banco de dados
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )

    # Crie um cursor
    cursor = conexao.cursor()

    # Execute a consulta SQL para excluir o cliente
    cursor.execute('DELETE FROM tb_vendas WHERE numero_pedido = %s', (numero_pedido,))

    # Commit a transação
    conexao.commit()

    # Feche o cursor e a conexão com o banco de dados
    cursor.close()
    conexao.close()

    return True

@app.route('/excluir3/<int:numero_pedido>', methods=['GET', 'POST'])
def exclusaovendas(numero_pedido):
    if request.method == 'POST':
        if delete_cliente3(numero_pedido):
            # Redirecione para a página de exibição da tabela
            return redirect(url_for('vendas_page'))
        else:
            # Mostre uma mensagem de erro
            return render_template('clientes.html', mensagem='Erro ao excluir o cliente.')
    else:
        # Aqui você pode lidar com a exibição da página normalmente para o método "GET"
        # Se necessário, você pode renderizar um formulário de confirmação antes da exclusão.
        pass  









#   _._     _,-'""`-._
# (,-.`._,'(       |\`-/|
#     `-.-' \ )-`( , o o)
#           `-    \`_`"'-






# Rota para obter os dados dos produtos
@app.route('/clientes_add_select', methods=['GET'])
def obter_addclientes():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    cursor = conexao.cursor()
    cursor.execute("SELECT nome FROM tb_clientes")
    cliente_app = [cliente[0] for cliente in cursor.fetchall()]

    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()

    return json.dumps(cliente_app)

@app.route('/vendas_clientes', methods=['GET'])
def vendas_addclientes():
    # Obtém a lista de produtos da rota /produtos usando a função que você definiu
    cliente_app = obter_addclientes()

    # Renderiza o template vendas.html e passa a lista de produtos como uma variável para o template
    return render_template('vendas.html', cliente_app=cliente_app)


@app.route('/buscar_vendas', methods=['POST'])
def buscar_vendas():
    conexao = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='sampanature',
    )
    
    pesquisa = request.form['pesquisa']
    filtro = request.form['filtro']
    
    # Conectar ao banco de dados
    cursor = conexao.cursor()
    
    # Executar consulta SQL baseada nos valores do formulário
    if filtro == 'opcao1':
        pesquisa = pesquisa.replace("'", "''")  # Lidar com apóstrofos
        pesquisa = pesquisa.replace("%", r"\%")  # Escapar caracteres curinga %
        query = "SELECT * FROM tb_vendas WHERE numero_pedido LIKE '%{}%' OR data_produto LIKE '%{}%' OR produto LIKE '%{}%' OR status_produto LIKE '%{}%' OR nome_cliente LIKE '%{}%' OR unidade LIKE '%{}%' OR desconto LIKE '%{}%' OR valor_final LIKE '%{}%' ".format(pesquisa, pesquisa, pesquisa, pesquisa, pesquisa, pesquisa, pesquisa, pesquisa)
    elif filtro == 'opcao2':
        query = "SELECT * FROM tb_vendas WHERE numero_pedido LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao3':
        query = "SELECT * FROM tb_vendas WHERE data_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao4':
        query = "SELECT * FROM tb_vendas WHERE produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao5':
        query = "SELECT * FROM tb_vendas WHERE status_produto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao6':
        query = "SELECT * FROM tb_vendas WHERE nome_cliente LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao7':
        query = "SELECT * FROM tb_vendas WHERE unidade LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao8':
        query = "SELECT * FROM tb_vendas WHERE desconto LIKE '%{}%'".format(pesquisa)
    elif filtro == 'opcao9':
        query = "SELECT * FROM tb_vendas WHERE valor_final LIKE '%{}%'".format(pesquisa)
    # Adicione mais opções de filtro conforme necessário
    
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    # Fechar a conexão com o banco de dados
    cursor.close()
    conexao.close()
    
    # Retornar os resultados para a página web
    return render_template('vendas.html', resultados=resultados)



































#   _._     _,-'""`-._
# (,-.`._,'(       |\`-/|
#     `-.-' \ )-`( , o o)
#           `-    \`_`"'-


if __name__ == '__main__':
    app.run(debug=True)

