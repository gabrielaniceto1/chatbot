import sqlite3
from datetime import datetime
import uuid

DB_NAME = "atendimentos.db"

def iniciar_banco():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            prefeitura TEXT,
            hospital TEXT,
            setor TEXT,
            nome TEXT,
            identificacao TEXT,
            problema TEXT,
            descricao TEXT,
            resposta TEXT,
            protocolo TEXT,
            encaminhado BOOLEAN,
            data_hora TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_etapa(numero, dados, resposta, protocolo, encaminhado):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO atendimentos (
            numero, prefeitura, hospital, setor, nome, identificacao,
            problema, descricao, resposta, protocolo, encaminhado, data_hora
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        numero,
        dados.get("prefeitura"),
        dados.get("hospital"),
        dados.get("setor"),
        dados.get("nome"),
        dados.get("identificacao"),
        dados.get("problema"),
        dados.get("descricao"),
        resposta,
        protocolo,
        encaminhado,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def atualizar_atendimento(numero, novo_protocolo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE atendimentos
        SET encaminhado = 1, protocolo = ?
        WHERE numero = ?
        ORDER BY id DESC
        LIMIT 1
    ''', (novo_protocolo, numero))
    conn.commit()
    conn.close()

def gerar_protocolo():
    return str(uuid.uuid4())[:8].upper()
