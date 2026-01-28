import requests
import pandas as pd
import os
import random
import time

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=15)
    except:
        pass

def buscar_dados_com_retry(url):
    # Lista de identidades reais para enganar o bloqueio
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    
    for i in range(3): # Tenta 3 vezes
        try:
            headers = {
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            session = requests.Session()
            res = session.get(url, headers=headers, timeout=30)
            res.raise_for_status()
            
            # Tenta ler a tabela
            tabelas = pd.read_html(res.text, flavor='html5lib')
            if tabelas:
                return tabelas[0]
        except Exception as e:
            print(f"Tentativa {i+1} falhou para {url}: {e}")
            time.sleep(5) # Espera 5 segundos antes de tentar de novo
            
    return pd.DataFrame()

def executar():
    df_atracados = buscar_dados_com_retry("https://www.praticagem.org.br/navios-atracados.html")
    df_previstas = buscar_dados_com_retry("https://www.praticagem.org.br/manobras-previstas.html")
    
    if df_atracados.empty and df_previstas.empty:
        enviar_telegram("⚠️ *Aviso:* O site da Praticagem bloqueou o acesso automático. Verifique manualmente: [Clique aqui](https://www.praticagem.org.br/manobras-previstas.html)")
        return

    report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

    for b_id, b_nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
        # 1. Verificação de Atracação
        status = "🟢 *LIVRE*"
        if not df_atracados.empty:
            # Busca o berço em qualquer coluna da tabela
            mask = df_atracados.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)
            atracado = df_atracados[mask]
            if not atracado.empty:
                navio_atual = atracado.iloc[0]['Navio']
                status = f"🔴 *OCUPADO*\n🚢 *Navio:* {navio_atual}"

        # 2. Programação Futura
        prog_texto = "📋 _Sem programação futura._\n"
        if not df_previstas.empty:
            mask_p = df_previstas.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)
            progs = df_previstas[mask_p]
            if not progs.empty:
                prog_texto = "📋 _Prog. Futura:_\n"
                for _, r in progs.head(3).iterrows():
                    m = str(r['Manobra']).upper()
                    tipo = "➡️ ENTRADA" if any(x in m for x in ["ENTRADA", "ENTRAR"]) else "⬅️ SAÍDA"
                    prog_texto += f"  • {r['Data/Hora']} | {tipo} | {r['Navio']}\n"
        
        report += f"⚓ *Berço {b_nome}:* {status}\n{prog_texto}\n"

    enviar_telegram(report)

if __name__ == "__main__":
    executar()