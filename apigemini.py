import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import textwrap
import threading

app = Flask(__name__)

# Configuração da API Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def enviar_mensagem_gemini(mensagem):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resposta = model.generate_content(mensagem, timeout=10)  # Timeout para Gemini
        return resposta.text
    except Exception as e:
        print(f"Erro na API Gemini: {e}")
        return "Desculpe, houve um erro ao processar sua mensagem."

# Dividir em blocos menores
def dividir_em_blocos(texto, largura=1600):
    return textwrap.wrap(texto, width=largura)

@app.route('/mensagem', methods=['POST'])
def mensagem():
    incoming_msg = request.values.get('Body', '').strip()
    resposta = MessagingResponse()
    resposta.message("Recebemos sua mensagem! Processando...")  # Resposta inicial rápida

    # Thread para processar a resposta do Gemini em segundo plano
    threading.Thread(target=processar_resposta, args=(incoming_msg,)).start()

    return str(resposta)

def processar_resposta(mensagem):
    gemini_resposta = enviar_mensagem_gemini(mensagem)
    if gemini_resposta:
        blocos = dividir_em_blocos(gemini_resposta)
        for bloco in blocos:
            # Lógica para enviar cada bloco como uma nova mensagem pelo Twilio
            enviar_mensagem_twilio(bloco)
    else:
        enviar_mensagem_twilio("Desculpe, a resposta do Gemini está vazia.")

def enviar_mensagem_twilio(mensagem):
    # Implementação para enviar mensagem de volta ao usuário via Twilio
    print(f"Enviando resposta: {mensagem}")
    # Aqui você pode usar o Twilio API Client para enviar mensagens adicionais, se necessário

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
