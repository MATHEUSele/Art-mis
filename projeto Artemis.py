import pyaudio
import wave
import speech_recognition as sr
import openai
import requests
from bs4 import BeautifulSoup
import pyttsx3

#variaves importantes e suas atribuições
# WAVE_OUTPUT_FILENAME e a variavel que armazena o nome do arquivo de audio gravado 
# tempoDGravacao e a variavel que armazena o tempo de gravação em SEGUNDOS
# CHUNK, FORMAT, CHANNELS, RATE e RECORD_SECONDS são parâmetros de gravação de áudio
# a transcrição de áudio é feita usando a biblioteca SpeechRecognition


#Configurando voz
engine = pyttsx3.init()
rate = engine.getProperty('rate')
engine.setProperty('rate', rate-200)
#volume da Artemis
volume = engine.getProperty('volume')
engine.setProperty('volume', volume+10000)

#testando as funçoes do selenio  

#def relacionadas a saida formatação do texto
def titulo(msg):
    print("-" * 30)
    print(msg)
    print("-" * 30)


def falarmsg(msg):
    print(msg)
    engine.say(msg)  # Faz o pyttsx3 falar a mensagem
    engine.runAndWait()


def mensagem_verde(msg):
    print(f"\033[32m {msg} \033[0m")  # Exibe a mensagem no terminal
    engine.say(msg)  # Faz o pyttsx3 falar a mensagem
    engine.runAndWait()


def mensagem_amarelo(msg):
    print(f"\033[33m {msg} \033[0m")  # Exibe a mensagem no terminal
    engine.say(msg)  # Faz o pyttsx3 falar a mensagem
    engine.runAndWait()


def mensagem_azul(msg):
    print(f"\033[34m {msg} \033[0m")  # Exibe a mensagem no terminal
    engine.say(msg)  # Faz o pyttsx3 falar a mensagem
    engine.runAndWait()


# Configuração da API do OpenAI
openai.api_key = "your_openai_api_key_here"


titulo("Bem-vindo à Artemis 0.01")
falarmsg("Olá, eu sou a Artemis, sua assistente virtual.")
falarmsg("oque deseja saber hoje, basta apenas me perguntar e eu irei te ajudar")
tempoDGravacao = 5  # Tempo de gravação em segundos
# Parâmetros de gravação


CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = tempoDGravacao
WAVE_OUTPUT_FILENAME = "output.wav"

# Função para gravar áudio
def gravar_audio():
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)

    mensagem_verde("escutando...")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    mensagem_verde("procurando resultados...")

    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

# Função para transcrever áudio usando SpeechRecognition api do Google
def transcrever_audio():
    r = sr.Recognizer()

    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio_data = r.record(source)  # Ler o arquivo de áudio
        try:
            titulo("Transcrevendo audio...")
            texto = r.recognize_google(audio_data, language="pt-BR")  # Usar Google Speech Recognition
            mensagem_amarelo("você dissse: " + texto)
            return texto
        except sr.UnknownValueError:
            print("Google Speech Recognition não conseguiu entender o áudio")
        except sr.RequestError as e:
            print(f"Erro ao requisitar resultados do serviço de reconhecimento de fala: {e}")
    return None

# Função para consultar a API do GPT usando openai==0.28
def consultar_chatgpt(pergunta):
    print("Consultando a API do ChatGPT...")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use um engine compatível com a versão 0.28
            prompt=pergunta,
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7,
        )
        resposta = response['choices'][0]['text'].strip()
        print("Resposta do ChatGPT:")
        print(resposta)
    except Exception as e:
        print(f"Erro ao consultar a API do ChatGPT: {e}")
# Chamar funções
#gravar_audio()
#texto_transcrito = transcrever_audio()

#if texto_transcrito:
    #consultar_chatgpt(texto_transcrito)
#===============================================================================================================================

def pesquisar_na_internet(texto):
    """
    Realiza uma pesquisa na internet com o texto fornecido e retorna uma descrição do que foi encontrado.

    :param texto: Texto para realizar a pesquisa
    :return: Resumo dos resultados da pesquisa
    """
    try:
        titulo("Pesquisando na internet...")

        # Realizando a pesquisa no Google
        query = texto.replace(" ", "+")  # Formatar para URL
        url = f"https://www.google.com/search?q={query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Extraindo os resultados da página
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("h3")  # Seleciona os títulos das páginas

        if results:
            print("")
            mensagem_verde("pesquisas relacionadas:")
            resumo = "\n".join([result.get_text() for result in results[:3]])  # Limitar a 3 resultados
            mensagem_amarelo(resumo)
            return resumo
        else:
            print("")
            mensagem_amarelo("Nenhum resultado relevante foi encontrado.")
            return "Nenhum resultado encontrado."

    except Exception as e:
        print("")
        mensagem_amarelo(f" ao realizar a pesquisa: {e}")
        return None
    
#==================================================================================================================================================
# Gravação e transcrição do áudio
gravar_audio()
texto = transcrever_audio()

if texto:
    # Pesquisa na internet com o texto transcrito
    resposta_pesquisa = pesquisar_na_internet(texto)
else:
    print("")
    mensagem_amarelo("Não foi possível transcrever o áudio para realizar a pesquisa.")
engine.runAndWait()
#fazer uma pregunta para saber se o usuario quer fazer uma nova pesquisa ou encerrar o programa


#================================================================================================================================
# Loop para verificar a resposta do usuário
falarmsg("Você gostaria de fazer outra pesquisa?")
gravar_audio()
mensagem_verde("escutando...")
resposta_verifica = transcrever_audio(WAVE_OUTPUT_FILENAME).lower().strip()

# Converte pra minúsculo e remove espaços extras
if resposta_verifica:
    resposta_verifica = resposta_verifica.lower().strip()
else:
    resposta_verifica = ""

respostas_possiveis = ["sim", "quero", "claro", "com certeza", "talvez", "pode ser", "simplesmente sim", "sim sim", "sim sim sim"]

if any(palavra in resposta_verifica for palavra in respostas_possiveis):
    while any(palavra in resposta_verifica for palavra in respostas_possiveis):
        gravar_audio()
        resposta = transcrever_audio().lower().strip()
        mensagem_amarelo(resposta)
        pesquisar_na_internet(resposta)
        falarmsg("Você gostaria de fazer outra pesquisa ,ou, encerrar o programa?")
        gravar_audio()
        mensagem_verde("escutando...")
        resposta_verifica = transcrever_audio().lower().strip()
        if resposta_verifica:
            resposta_verifica = resposta_verifica.lower().strip()
        else:
            resposta_verifica = ""
else:     
    mensagem_azul("Encerrando o programa...")  
    engine.say("até logo, espero ter te ajudado")
