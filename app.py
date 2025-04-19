from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'sua_chave_secreta_aqui')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///clientes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    endereco = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)

# Middleware para verificar autenticação
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'usuario' not in session:
        return redirect(url_for('login'))

# Rotas
@app.route('/')
def index():
    total_clientes = Cliente.query.count()
    clientes_ativos = Cliente.query.filter_by(ativo=True).count()
    novos_clientes = Cliente.query.order_by(Cliente.id.desc()).limit(5).all()
    return render_template('index.html', 
                         total_clientes=total_clientes,
                         clientes_ativos=clientes_ativos,
                         novos_clientes=novos_clientes)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login'].replace('.', '').replace('-', '')  # Remove formatação do CPF
        senha = request.form['senha']
        
        usuario = Usuario.query.filter_by(login=login).first()
        
        if usuario and usuario.senha == senha:
            session['usuario'] = login
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        flash('CPF ou senha inválidos. Por favor, tente novamente.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    flash('Você foi desconectado com sucesso!', 'success')
    return redirect(url_for('login'))

@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/cliente/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        try:
            cliente = Cliente(
                nome=request.form['nome'],
                cpf=request.form['cpf'].replace('.', '').replace('-', ''),
                telefone=request.form['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', ''),
                email=request.form['email'],
                endereco=request.form['endereco']
            )
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao cadastrar cliente. Verifique se o CPF já está cadastrado.', 'error')
    
    return render_template('form_cliente.html', cliente=None)

@app.route('/cliente/<int:id>/editar', methods=['GET', 'POST'])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            cliente.nome = request.form['nome']
            cliente.cpf = request.form['cpf'].replace('.', '').replace('-', '')
            cliente.telefone = request.form['telefone'].replace('(', '').replace(')', '').replace(' ', '').replace('-', '')
            cliente.email = request.form['email']
            cliente.endereco = request.form['endereco']
            cliente.ativo = 'ativo' in request.form
            
            db.session.commit()
            flash('Cliente atualizado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar cliente. Verifique se o CPF já está cadastrado.', 'error')
    
    return render_template('form_cliente.html', cliente=cliente)

@app.route('/cliente/<int:id>/excluir', methods=['POST'])
def excluir_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao excluir cliente.', 'error')
    
    return redirect(url_for('listar_clientes'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Criar usuário padrão se não existir
        if not Usuario.query.filter_by(login='01099080150').first():
            usuario = Usuario(login='01099080150', senha='123456')
            db.session.add(usuario)
            db.session.commit()
    app.run(host='0.0.0.0', port=8080) 