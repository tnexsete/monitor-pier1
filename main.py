import requests
import pandas as pd
import os
import time
import random

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=20)
    except:
        pass

def buscar_dados_blindado(url):
    # Lista de identidades para confundir o bloqueio do site
    identidades = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
    ]
    
    for tentativa in range(3):
        try:
            headers = {
                'User-Agent': random.choice(identidades),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Connection': 'keep-alive',
                'Referer': 'https://www.google.com/'
            }
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Forçamos o uso do 'html5lib' que é mais robusto para capturar tabelas protegidas
            tabelas = pd.read_html(response.text, flavor='html5lib')
            return tabelas[0]
        except Exception as e:
            print(f"Tentativa {tentativa + 1} falhou: {e}")
            time.sleep(random.uniform(5, 10)) # Espera aleatória entre 5 a 10 segundos
            
    return pd.DataFrame()

def executar():
    # Sem mapas, foco total nas tabelas técnicas
    df_atracados = buscar_dados_blindado("https://www.praticagem.org.br/navios-atracados.html")
    df_previstas = buscar_dados_blindado("https://www.praticagem.org.br/manobras-previstas.html")
    
    if df_atracados.empty and df_previstas.empty:
        enviar_telegram("⚠️ *Alerta Técnico:* Bloqueio persistente no site da Praticagem. Tentarei nova rota na próxima hora.")
        return

    report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

    for b_id, b_nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
        # 1. ANALISAR OCUPAÇÃO (NAVIO ATUAL)
        status = "🟢 *LIVRE*"
        if not df_atracados.empty:
            atracado = df_atracados[df_atracados.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)]
            if not atracado.empty:
                navio = atracado.iloc[0]['Navio']
                status = f"🔴 *OCUPADO*\n🚢 *Navio:* {navio}"

        # 2. ANALISAR PROGRAMAÇÃO (ENTRADA/SAÍDA)
        prog_txt = "📋 _Sem programação próxima._\n"
        if not df_previstas.empty:
            manobras = df_previstas[df_previstas.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)]
            if not manobras.empty:
                prog_txt = "📋 _Prog. Futura:_\n"
                for _, r in manobras.head(3).iterrows():
                    m_tipo = str(r['Manobra']).upper()
                    # Identifica Entrada ou Saída conforme você solicitou
                    seta = "➡️ ENTRADA" if any(x in m_tipo for x in ["ENTRADA", "ENTRAR"]) else "⬅️ SAÍDA"
                    prog_txt += f"  • {r['Data/Hora']} | {seta} | {r['Navio']}\n"
        
        report += f"⚓ *Berço {b_nome}:* {status}\n{prog_txt}\n"

    enviar_telegram(report)

if __name__ == "__main__":
    executar()
