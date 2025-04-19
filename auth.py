import sqlite3

def login(login, senha):
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE login = ?", (login,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado and resultado[0] == senha

def alterar_senha(login, senha_atual, nova_senha):
    conn = sqlite3.connect('clientes.db')
    cursor = conn.cursor()
    
    # Verifica senha atual
    cursor.execute("SELECT senha FROM usuarios WHERE login = ?", (login,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] == senha_atual:
        cursor.execute("UPDATE usuarios SET senha = ? WHERE login = ?", 
                       (nova_senha, login))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False