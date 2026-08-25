import os
import time
import asyncio
import edge_tts
import pygame
import speech_recognition as sr
import pyaudio
import keyboard
import winsound
from rapidfuzz import fuzz

# -------------------------------------------------------------
# Configurações de Voz e Gatilho
# -------------------------------------------------------------
VOZ_JARVIS = "pt-BR-AntonioNeural"
ARQUIVO_AUDIO_TEMP = os.path.abspath("fala_temp.mp3")

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.6  

GATILHOS_EXATOS = [
    "jarvis", "jarbas", "iarvis", "jarves", "charvis", 
    "jarbis", "jervis", "iervis", "jabes", "chaves",
    "jarve", "jarvi", "djarvis", "darvis"
]

INDICE_MICROFONE = None
_ignorar_gatilho_uma_vez = False
_quer_digitar = False


def _acionar_por_teclado_voz():
    """F12: Ativa escuta direta sem precisar falar o nome."""
    global _ignorar_gatilho_uma_vez
    _ignorar_gatilho_uma_vez = True
    try:
        winsound.Beep(440, 60)
        winsound.Beep(587, 80)
    except:
        pass


def _acionar_modo_texto():
    """F11: Pausa o microfone e permite digitar o comando."""
    global _quer_digitar
    _quer_digitar = True
    try:
        # Bip duplo agudo para confirmar que abriu a caixa de texto
        winsound.Beep(800, 70)
        winsound.Beep(1000, 90)
    except:
        pass


# Registra os atalhos globalmente
keyboard.add_hotkey('f12', _acionar_por_teclado_voz)
keyboard.add_hotkey('f11', _acionar_modo_texto)


def selecionar_microfone():
    global INDICE_MICROFONE

    p = pyaudio.PyAudio()
    mics_validos = []
    nomes_vistos = set()

    print("\n" + "=" * 55)
    print("🎤 MICROFONES DISPONÍVEIS:")
    print("=" * 55)

    for i in range(p.get_device_count()):
        dev_info = p.get_device_info_by_index(i)
        canais_entrada = dev_info.get("maxInputChannels", 0)
        host_api = dev_info.get("hostApi", -1)
        nome = dev_info.get("name", "").strip()

        if canais_entrada > 0 and host_api == 0 and len(nome) > 3 and "()" not in nome:
            if nome not in nomes_vistos:
                nomes_vistos.add(nome)
                mics_validos.append((i, nome))

    p.terminate()

    for opcao_idx, (real_index, nome) in enumerate(mics_validos):
        print(f"  [{opcao_idx}] {nome}")

    print("=" * 55)

    if not mics_validos:
        print("⚠️ Nenhum microfone detectado, usando padrão.")
        INDICE_MICROFONE = None
        return None

    while True:
        escolha = input(f"Selecione o microfone (0 a {len(mics_validos) - 1}) [Enter para 0]: ").strip()
        if escolha == "":
            INDICE_MICROFONE = mics_validos[0][0]
            nome_escolhido = mics_validos[0][1]
            break
        if escolha.isdigit() and 0 <= int(escolha) < len(mics_validos):
            opcao = int(escolha)
            INDICE_MICROFONE = mics_validos[opcao][0]
            nome_escolhido = mics_validos[opcao][1]
            break
        print("⚠️ Opção inválida. Tente novamente.")

    print(f"✅ Microfone ativo: {nome_escolhido} (Device ID: {INDICE_MICROFONE})\n")
    return INDICE_MICROFONE


async def _gerar_audio_neural(texto: str, caminho_arquivo: str):
    comunicador = edge_tts.Communicate(
        texto,
        VOZ_JARVIS,
        rate="+8%",
        pitch="-3Hz"
    )
    await comunicador.save(caminho_arquivo)


def falar(texto: str):
    print(f"\n🔊 [Jarvis Falando]: {texto}")

    if not texto or not texto.strip():
        return

    try:
        asyncio.run(_gerar_audio_neural(texto, ARQUIVO_AUDIO_TEMP))

        pygame.mixer.init()
        pygame.mixer.music.load(ARQUIVO_AUDIO_TEMP)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.quit()

        if os.path.exists(ARQUIVO_AUDIO_TEMP):
            os.remove(ARQUIVO_AUDIO_TEMP)
    except Exception as e:
        print(f"⚠️ Erro ao sintetizar áudio: {e}")


def _detectar_gatilho_no_texto(texto: str) -> tuple[bool, str]:
    palavras = texto.split()

    for gatilho in GATILHOS_EXATOS:
        if gatilho in texto:
            comando = texto.replace(gatilho, "").strip()
            return True, comando if comando else "oi"

    for palavra in palavras:
        score_jarvis = fuzz.ratio(palavra, "jarvis")
        score_jarbas = fuzz.ratio(palavra, "jarbas")
        if score_jarvis >= 75 or score_jarbas >= 75:
            comando = texto.replace(palavra, "").strip()
            return True, comando if comando else "oi"

    return False, ""


def aguardar_chamado(modo_continuo=False) -> str:
    global INDICE_MICROFONE, _ignorar_gatilho_uma_vez, _quer_digitar

    if INDICE_MICROFONE is None:
        selecionar_microfone()

    with sr.Microphone(device_index=INDICE_MICROFONE) as source:
        
        if not modo_continuo:
            print("⚙️  Calibrando ruído ambiente...")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            print("👂 Em espera... [Voz: 'Jarvis'] | [F12: Falar agora] | [F11: Digitar]")
        else:
            print("🔄 [Modo Conversa] Pode responder diretamente por voz (8s)...")

        _ignorar_gatilho_uma_vez = False
        _quer_digitar = False
        inicio_escuta = time.time()

        while True:
            # 1. Checa primeiro se o usuário apertou F11 para digitar
            if _quer_digitar:
                _quer_digitar = False
                print("\n" + "=" * 40)
                comando_digitado = input("⌨️  [Modo Texto] Digite seu comando:\n> ").strip()
                print("=" * 40)
                
                if comando_digitado:
                    return comando_digitado
                else:
                    print("🔙 Comando vazio. Voltando a escutar o microfone...")
                    continue

            try:
                # 2. Controla o tempo do modo contínuo
                if modo_continuo:
                    if time.time() - inicio_escuta > 8.0:
                        print("💤 [Silêncio detectado. Jarvis voltou a dormir]")
                        return ""

                # Ouve o microfone em blocos curtos (0.5s) para não travar o teclado (F11)
                audio = recognizer.listen(source, timeout=0.5, phrase_time_limit=6)
                texto = recognizer.recognize_google(audio, language="pt-BR").lower()
                print(f"🎙️  [Ouvido]: '{texto}'")

                # Se o usuário apertou F12
                if _ignorar_gatilho_uma_vez:
                    _ignorar_gatilho_uma_vez = False
                    print(f"✨ [Ativado por F12 | Comando: '{texto}']")
                    return texto

                # Se está na janela de 8s contínuos
                if modo_continuo:
                    print(f"✨ [Continuando a conversa | Comando: '{texto}']")
                    return texto

                # Se falou "Jarvis" do zero
                ativou, comando = _detectar_gatilho_no_texto(texto)
                if ativou:
                    print(f"✨ [Ativado por Voz | Comando: '{comando}']")
                    return comando

            except sr.WaitTimeoutError:
                # Se passou 0.5s e ninguém falou, o loop reinicia e ele checa se o F11 foi apertado.
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"⚠️ Erro no serviço de voz: {e}")
                return ""