import requests
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def executar():
    try:
        # Navios no Pier 1
        df = pd.read_html("https://www.praticagem.org.br/manobras-previstas.html")[0]
        p1 = df[df['Berço'].str.contains('TUBP1S|TUBP1N', na=False)]
        navios = "\n".join([f"• {r['Navio']} ({r['Berço']}): {r['Manobra']}" for _, r in p1.iterrows()]) or "Sem manobras."

        # Clima
        res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-20.28&longitude=-40.24&hourly=temperature_2m,windspeed_10m&forecast_days=1").json()
        clima = f"{res['hourly']['temperature_2m'][0]}°C | Vento: {res['hourly']['windspeed_10m'][0]}km/h"

        # Relatório
        msg = f"📊 *REPORT PIER 1*\n\n🚢 *NAVIO:*\n{navios}\n\n☁️ *CLIMA:* {clima}"
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={msg}&parse_mode=Markdown")
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    executar()
