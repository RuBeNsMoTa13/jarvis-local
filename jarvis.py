import time
import ollama
from tools import TODAS_AS_FERRAMENTAS, executar_ferramenta
from voice import falar, aguardar_chamado

MODELO = "gemma4"

def executar_jarvis():
    print("🤖 Inicializando Jarvis (Híbrido: Voz + F12 + Conversa Contínua)...", flush=True)

    mensagens = [
        {
            "role": "system",
            "content": (
                "Você é o JARVIS, um assistente pessoal inteligente. "
                "Responda sempre em português brasileiro de forma direta, concisa e natural para fala."
            )
        }
    ]

    falar("Sistemas online. Estou pronto, senhor.")
    
    # Inicia com o modo conversa desligado (esperando o nome)
    modo_conversa = False

    try:
        while True:
            # Passa para o microfone qual o estado atual
            comando = aguardar_chamado(modo_continuo=modo_conversa)
            
            # Se a função retornou vazio, significa que os 8s passaram e você não falou nada.
            if not comando:
                modo_conversa = False  # Desliga o modo conversa
                continue

            if comando in ["sair", "desligar", "encerrar"]:
                falar("Desligando sistemas. Até logo, senhor.")
                break

            print(f"\n⏳ Processando: '{comando}'...", flush=True)
            mensagens.append({"role": "user", "content": comando})

            tempo_inicio = time.time()

            try:
                resposta = ollama.chat(
                    model=MODELO,
                    messages=mensagens,
                    tools=TODAS_AS_FERRAMENTAS
                )
            except Exception as e:
                print(f"⚠️ Erro ao consultar o modelo: {e}")
                modo_conversa = False
                continue

            mensagens.append(resposta["message"])

            if resposta["message"].get("tool_calls"):
                for chamada in resposta["message"]["tool_calls"]:
                    nome_funcao = chamada["function"]["name"]
                    argumentos = chamada["function"].get("arguments", {})

                    print(f"🔧 Executando ferramenta: {nome_funcao}")
                    falar(f"Executando {nome_funcao.replace('_', ' ')}.")

                    resultado = executar_ferramenta(nome_funcao, argumentos)
                    mensagens.append({
                        "role": "tool",
                        "content": resultado
                    })

                resposta_final = ollama.chat(
                    model=MODELO,
                    messages=mensagens
                )
                conteudo = resposta_final["message"]["content"]
                mensagens.append(resposta_final["message"])
                
                tempo_decorrido = time.time() - tempo_inicio
                print(f"⏱️ [Tempo de raciocínio: {tempo_decorrido:.2f} segundos]", flush=True)
                
                falar(conteudo)
                
            else:
                conteudo = resposta["message"]["content"]
                tempo_decorrido = time.time() - tempo_inicio
                print(f"⏱️ [Tempo de raciocínio: {tempo_decorrido:.2f} segundos]", flush=True)
                
                falar(conteudo)

            # Depois de falar, ele abre a janela de 8 segundos para você continuar o papo!
            modo_conversa = True

    except KeyboardInterrupt:
        print("\nFinalizando Jarvis...", flush=True)


if __name__ == "__main__":
    executar_jarvis()