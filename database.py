from app import db
from app import Usuario, Cliente  # Importe suas classes Model corretamente

def criar_banco():
    db.create_all()

    # Inserir usuário padrão se não existir
    if not Usuario.query.filter_by(login='01099080150').first():
        usuario_padrao = Usuario(login='01099080150', senha='123456')
        db.session.add(usuario_padrao)
        db.session.commit()


def alterar_senha(login, senha_atual, nova_senha):
    usuario = Usuario.query.filter_by(login=login, senha=senha_atual).first()
    if usuario:
        usuario.senha = nova_senha
        db.session.commit()
        return True
    return False


def reordenar_ids():
    try:
        # Busca e ordena os dados
        dados = db.session.execute('''
            SELECT p.id, p.nome_completo, p.funcao, p.telefone, p.municipio, p.escola,
                   GROUP_CONCAT(h.dia_semana || ' ' || h.hora, ', ') AS horarios
            FROM profissionais p
            LEFT JOIN horarios_planejamento h ON p.id = h.profissional_id
            GROUP BY p.id
            ORDER BY p.nome_completo
        ''').fetchall()

        # Limpa os dados
        db.session.execute('DELETE FROM horarios_planejamento')
        db.session.execute('DELETE FROM profissionais')
        db.session.commit()

        # Reinserção com IDs sequenciais
        novo_id = 1
        for linha in dados:
            nome, funcao, telefone, municipio, escola, horarios = linha[1:]
            db.session.execute('''
                INSERT INTO profissionais (id, nome_completo, funcao, telefone, municipio, escola)
                VALUES (:id, :nome, :funcao, :telefone, :municipio, :escola)
            ''', {
                'id': novo_id, 'nome': nome, 'funcao': funcao, 'telefone': telefone,
                'municipio': municipio, 'escola': escola
            })

            if horarios:
                for h in horarios.split(', '):
                    if h:
                        dia_semana, hora = h.rsplit(' ', 1)
                        db.session.execute('''
                            INSERT INTO horarios_planejamento (profissional_id, dia_semana, hora)
                            VALUES (:prof_id, :dia, :hora)
                        ''', {
                            'prof_id': novo_id,
                            'dia': dia_semana,
                            'hora': hora
                        })

            novo_id += 1

        db.session.commit()
        return True

    except Exception as e:
        db.session.rollback()
        raise e
