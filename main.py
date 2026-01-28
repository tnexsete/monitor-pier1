import requests
import pandas as pd
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
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    
    # 1. Tentar ler Praticagem com identidade humana
    try:
        res = requests.get("https://www.praticagem.org.br/manobras-previstas.html", headers=headers, timeout=15)
        df = pd.read_html(res.text)[0]
        p1 = df[df['Berço'].str.contains('TUBP1S|TUBP1N', na=False, case=False)]
        navios = "\n".join([f"• {r['Navio']} ({r['Berço']}): {r['Manobra']}" for _, r in p1.iterrows()])
        if not navios: navios = "P1: Sem manobras agora."
    except Exception as e:
        navios = f"⚠️ Erro Praticagem: Site em manutenção ou bloqueado."

    # 2. Tentar print do Mapa com disfarce
    try:
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument(f'user-agent={headers["User-Agent"]}')
        driver = webdriver.Chrome(options=opts)
        
        # Link direto para o Pier 1
        driver.get("https://www.marinetraffic.com/en/ais/home/centerx:-40.247/centery:-20.289/zoom:16")
        time.sleep(25) # Espera carregar os navios no mapa
        driver.save_screenshot('mapa.png')
        driver.quit()
        tem_foto = True
    except:
        tem_foto = False

    # 3. Enviar Report
    report = f"📊 *MONITORAMENTO PIER 1*\n\n🚢 *NAVIO:*\n{navios}"
    if tem_foto:
        enviar_telegram(report, 'mapa.png')
    else:
        enviar_telegram(report + "\n\n❌ Erro ao capturar mapa (Bloqueio MarineTraffic).")

if __name__ == "__main__":
    executar()