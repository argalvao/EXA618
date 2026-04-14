import os
import sys
import json
import urllib.parse
from datetime import datetime

if hasattr(sys.stdin, 'reconfigure'):
    sys.stdin.reconfigure(encoding='utf-8')
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ARQUIVO_MENSAGENS = "../mensagens.json"

def carregar_mensagens():
    if os.path.exists(ARQUIVO_MENSAGENS):
        with open(ARQUIVO_MENSAGENS, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_mensagem(autor, texto):
    mensagens = carregar_mensagens()
    nova_mensagem = {
        "autor": autor,
        "mensagem": texto,
        "data": datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    }
    mensagens.insert(0, nova_mensagem) 
    
    with open(ARQUIVO_MENSAGENS, 'w', encoding='utf-8') as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=4)

def retornar_json(dados):
    print("Content-Type: application/json; charset=utf-8\n")
    print(json.dumps(dados, ensure_ascii=False, indent=4))


metodo_requisicao = os.environ.get("REQUEST_METHOD", "GET")

if metodo_requisicao == "GET":
    query_string = os.environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_string)
    
    if 'action' in params and params['action'][0] == 'listar':
        mensagens = carregar_mensagens()
        retornar_json(mensagens)
    else:
        retornar_json({"erro": "Ação não reconhecida"})

elif metodo_requisicao == "POST":
    tamanho_conteudo = int(os.environ.get("CONTENT_LENGTH", 0))
    
    if tamanho_conteudo > 0:
        dados_brutos = sys.stdin.read(tamanho_conteudo)
        dados_formulario = urllib.parse.parse_qs(dados_brutos)
        
        autor = dados_formulario.get('autor', [None])[0]
        mensagem_texto = dados_formulario.get('mensagem', [None])[0]
        
        if autor and mensagem_texto:
            if autor.strip() and mensagem_texto.strip():
                salvar_mensagem(autor.strip(), mensagem_texto.strip())
                retornar_json({"sucesso": True, "mensagem": "Mensagem publicada com sucesso!"})
            else:
                retornar_json({"sucesso": False, "erro": "Autor e mensagem não podem estar vazios."})
        else:
            retornar_json({"sucesso": False, "erro": "Faltam campos obrigatórios (autor, mensagem)."})
    else:
        retornar_json({"sucesso": False, "erro": "Nenhum dado foi enviado."})

else:
    retornar_json({"erro": "Método HTTP não suportado"})