import requests
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem, foto=None):
    url_base = f"https://api.telegram.org/bot{TOKEN}"
    if foto:
        with open(foto, 'rb') as f:
            requests.post(f"{url_base}/sendPhoto?chat_id={CHAT_ID}", files={'photo': f}, data={'caption': mensagem, 'parse_mode': 'Markdown'})
    else:
        requests.get(f"{url_base}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown")

def executar():
    try:
        # 1. Tentar ler os navios
        try:
            df = pd.read_html("https://www.praticagem.org.br/manobras-previstas.html")[0]
            p1 = df[df['Berço'].str.contains('TUBP1S|TUBP1N', na=False, case=False)]
            navios = "\n".join([f"• {r['Navio']} ({r['Berço']}): {r['Manobra']}" for _, r in p1.iterrows()])
        except:
            navios = "⚠️ Erro ao acessar site da Praticagem."

        if not navios: navios = "P1: Sem manobras listadas agora."

        # 2. Tentar tirar o print
        try:
            opts = Options()
            opts.add_argument('--headless')
            opts.add_argument('--no-sandbox')
            opts.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=opts)
            driver.get("https://www.marinetraffic.com/en/ais/home/centerx:-40.247/centery:-20.289/zoom:16")
            time.sleep(30) # Aumentei o tempo para 30s
            driver.save_screenshot('mapa.png')
            driver.quit()
            tem_foto = True
        except:
            tem_foto = False

        # 3. Enviar
        report = f"📊 *TESTE PIER 1*\n\n🚢 *NAVIO:*\n{navios}"
        if tem_foto:
            enviar_telegram(report, 'mapa.png')
        else:
            enviar_telegram(report + "\n\n❌ Erro ao capturar mapa.")

    except Exception as e:
        # Se tudo falhar, tenta enviar o erro
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text=Erro crítico: {str(e)}")

if __name__ == "__main__":
    executar()
