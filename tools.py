import os
import webbrowser
import subprocess
from datetime import datetime

# Diretório seguro para manipulação de arquivos
WORKSPACE_DIR = os.path.abspath("./workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)


# -------------------------------------------------------------
# Definição das Ferramentas
# -------------------------------------------------------------

def abrir_chrome_pesquisa(termo: str) -> str:
    """Abre o navegador e realiza uma pesquisa no Google sobre o termo fornecido."""
    url = f"https://www.google.com/search?q={termo}"
    webbrowser.open(url)
    return f"Pesquisa por '{termo}' aberta no navegador."


def abrir_link_navegador(url_ou_site: str) -> str:
    """
    Abre diretamente um site ou URL no navegador.
    Aceita nomes diretos (ex: 'youtube', 'github') ou URLs completas.
    """
    alvo = url_ou_site.strip().lower()

    # Atalhos para sites comuns caso o usuário fale apenas o nome
    atalhos = {
        "youtube": "https://www.youtube.com",
        "github": "https://www.github.com",
        "chatgpt": "https://chat.openai.com",
        "gmail": "https://mail.google.com",
        "whatsapp": "https://web.whatsapp.com",
        "reddit": "https://www.reddit.com"
    }

    if alvo in atalhos:
        url_final = atalhos[alvo]
    elif not alvo.startswith("http://") and not alvo.startswith("https://"):
        # Se for um domínio simples como 'exemplo.com' ou 'campopago.com.br'
        if "." in alvo:
            url_final = f"https://{alvo}"
        else:
            url_final = f"https://www.{alvo}.com"
    else:
        url_final = url_ou_site.strip()

    webbrowser.open(url_final)
    return f"Site '{url_final}' aberto no navegador com sucesso."


def criar_arquivo(nome_arquivo: str, conteudo: str) -> str:
    """Cria ou sobrescreve um arquivo de texto no workspace com o conteúdo fornecido."""
    caminho = os.path.join(WORKSPACE_DIR, nome_arquivo)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return f"Arquivo '{nome_arquivo}' salvo no workspace com sucesso."


def ler_arquivo(nome_arquivo: str) -> str:
    """Lê o conteúdo de um arquivo salvo dentro do workspace."""
    caminho = os.path.join(WORKSPACE_DIR, nome_arquivo)
    if not os.path.exists(caminho):
        return f"Erro: o arquivo '{nome_arquivo}' não existe no workspace."
    with open(caminho, "r", encoding="utf-8") as f:
        conteudo = f.read()
    return f"Conteúdo de '{nome_arquivo}':\n{conteudo}"


def listar_arquivos_workspace() -> str:
    """Lista todos os arquivos presentes no diretório workspace."""
    arquivos = os.listdir(WORKSPACE_DIR)
    if not arquivos:
        return "O workspace está vazio no momento."
    return "Arquivos no workspace:\n" + "\n".join(f"- {arq}" for arq in arquivos)


def abrir_aplicativo(nome_app: str) -> str:
    """Abre um aplicativo local do sistema (opções: 'vscode', 'calculadora', 'notepad')."""
    app = nome_app.strip().lower()

    comandos = {
        "vscode": "code",
        "code": "code",
        "calculadora": "calc",
        "calc": "calc",
        "notepad": "notepad",
        "bloco de notas": "notepad"
    }

    if app in comandos:
        subprocess.Popen(comandos[app], shell=True)
        return f"Aplicativo '{nome_app}' aberto com sucesso."
    return f"Aplicativo '{nome_app}' não reconhecido na lista de permitidos."


def obter_data_hora_atual() -> str:
    """Retorna o dia da semana, data e hora exatas do sistema."""
    agora = datetime.now()
    dias_semana = [
        "segunda-feira", "terça-feira", "quarta-feira",
        "quinta-feira", "sexta-feira", "sábado", "domingo"
    ]
    dia_str = dias_semana[agora.weekday()]
    data_formatada = agora.strftime("%d/%m/%Y às %H:%M")
    return f"Hoje é {dia_str}, {data_formatada}."


# -------------------------------------------------------------
# Mapeamento Centralizado de Ferramentas
# -------------------------------------------------------------

FERRAMENTAS_MAPA = {
    "abrir_chrome_pesquisa": abrir_chrome_pesquisa,
    "abrir_link_navegador": abrir_link_navegador,
    "criar_arquivo": criar_arquivo,
    "ler_arquivo": ler_arquivo,
    "listar_arquivos_workspace": listar_arquivos_workspace,
    "abrir_aplicativo": abrir_aplicativo,
    "obter_data_hora_atual": obter_data_hora_atual,
}

TODAS_AS_FERRAMENTAS = list(FERRAMENTAS_MAPA.values())


def executar_ferramenta(nome_funcao: str, argumentos: dict) -> str:
    """Executa a ferramenta com base no nome e argumentos enviados pelo modelo."""
    if nome_funcao not in FERRAMENTAS_MAPA:
        return f"Erro: ferramenta '{nome_funcao}' não existe."

    try:
        funcao = FERRAMENTAS_MAPA[nome_funcao]
        return str(funcao(**argumentos))
    except Exception as erro:
        return f"Erro ao executar '{nome_funcao}': {str(erro)}"