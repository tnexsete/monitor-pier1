import requests
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem, foto=None):
    url = f"https://api.telegram.org/bot{TOKEN}"
    if foto:
        with open(foto, 'rb') as f:
            requests.post(f"{url}/sendPhoto?chat_id={CHAT_ID}", files={'photo': f}, data={'caption': mensagem, 'parse_mode': 'Markdown'})
    else:
        requests.get(f"{url}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown")

def executar():
    # Identidade de navegador real para enganar o bloqueio
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    
    # 1. Tentativa simplificada na Praticagem
    navios = "Consultar site manualmente: praticagem.org.br" # Backup caso o bloqueio persista
    try:
        session = requests.Session()
        session.headers.update({'User-Agent': user_agent})
        # Tentando acessar a versão mobile que costuma ter menos trava
        res = session.get("https://www.praticagem.org.br/manobras-previstas.html", timeout=20)
        if "TUBP1" in res.text:
            navios = "🚢 Existem manobras para o Pier 1 na lista!"
        else:
            navios = "P1: Sem manobras listadas agora."
    except:
        pass

    # 2. Print do Mapa (Mudamos para o link de 'Embed' que bloqueia menos)
    try:
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument(f'user-agent={user_agent}')
        driver = webdriver.Chrome(options=opts)
        
        # Link de visualização direta (menos scripts de bloqueio)
        driver.get("https://www.marinetraffic.com/en/ais/embed/zoom:14/centerx:-40.247/centery:-20.289/maptype:4")
        time.sleep(30) # Tempo maior para carregar o mapa
        driver.save_screenshot('mapa.png')
        driver.quit()
        tem_foto = True
    except:
        tem_foto = False

    # 3. Envio
    txt = f"📊 *MONITORAMENTO PIER 1*\n\n{navios}"
    if tem_foto:
        enviar_telegram(txt, 'mapa.png')
    else:
        enviar_telegram(txt + "\n\n❌ Mapa bloqueado pelo site.")

if __name__ == "__main__":
    executar()