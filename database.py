import sqlite3

def criar_banco():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    
    # Tabela de usuários (login)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        login TEXT PRIMARY KEY,
        senha TEXT NOT NULL
    )
    ''')
    
    # Tabela de profissionais
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS profissionais (
        id INTEGER PRIMARY KEY,
        nome_completo TEXT NOT NULL,
        funcao TEXT NOT NULL,
        telefone TEXT,
        municipio TEXT NOT NULL,
        escola TEXT NOT NULL
    )
    ''')
    
    # Tabela de horários de planejamento
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios_planejamento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profissional_id INTEGER,
        dia_semana TEXT NOT NULL,
        hora TEXT NOT NULL,
        FOREIGN KEY (profissional_id) REFERENCES profissionais(id)
    )
    ''')
    
    # Insere usuário padrão (se não existir)
    cursor.execute("SELECT * FROM usuarios WHERE login = '01099080150'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios VALUES (?, ?)", 
                      ('01099080150', '123456'))
    
    conn.commit()
    conn.close()

def alterar_senha(login, senha_atual, nova_senha):
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    
    try:
        # Verificar senha atual
        cursor.execute("SELECT * FROM usuarios WHERE login = ? AND senha = ?", (login, senha_atual))
        if cursor.fetchone():
            # Atualizar senha
            cursor.execute("UPDATE usuarios SET senha = ? WHERE login = ?", (nova_senha, login))
            conn.commit()
            return True
        else:
            return False
    finally:
        conn.close()

def reordenar_ids():
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Pegar todos os dados em ordem
        cursor.execute('''
        SELECT nome_completo, funcao, telefone, municipio, escola,
               GROUP_CONCAT(dia_semana || ' ' || hora, ', ') as horarios
        FROM profissionais p
        LEFT JOIN horarios_planejamento h ON p.id = h.profissional_id
        GROUP BY p.id
        ORDER BY nome_completo
        ''')
        dados = cursor.fetchall()
        
        # Limpar todas as tabelas
        cursor.execute("DELETE FROM horarios_planejamento")
        cursor.execute("DELETE FROM profissionais")
        
        # Reinserir dados com IDs sequenciais
        for i, (nome, funcao, telefone, municipio, escola, horarios) in enumerate(dados, 1):
            # Inserir profissional com ID específico
            cursor.execute('''
            INSERT INTO profissionais (id, nome_completo, funcao, telefone, municipio, escola)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (i, nome, funcao, telefone, municipio, escola))
            
            # Inserir horários se existirem
            if horarios:
                for horario in horarios.split(', '):
                    if horario:
                        dia_semana, hora = horario.rsplit(' ', 1)
                        cursor.execute('''
                        INSERT INTO horarios_planejamento (profissional_id, dia_semana, hora)
                        VALUES (?, ?, ?)
                        ''', (i, dia_semana, hora))
        
        cursor.execute("COMMIT")
        return True
        
    except Exception as e:
        cursor.execute("ROLLBACK")
        raise e
    
    finally:
        conn.close()