import requests
import pandas as pd
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=10)
    except:
        pass

def buscar_dados(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
    try:
        res = requests.get(url, headers=headers, timeout=25)
        # Força o pandas a usar o motor básico para evitar erros de biblioteca
        tabelas = pd.read_html(res.text, flavor='html5lib')
        return tabelas[0]
    except:
        return pd.DataFrame()

def executar():
    df_atracados = buscar_dados("https://www.praticagem.org.br/navios-atracados.html")
    df_previstas = buscar_dados("https://www.praticagem.org.br/manobras-previstas.html")
    
    if df_atracados.empty and df_previstas.empty:
        enviar_telegram("⚠️ *Aviso:* Não foi possível carregar os dados da Praticagem agora. Tentarei novamente na próxima hora.")
        return

    report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

    for b_id, b_nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
        # 1. Verifica Atracação
        status = "🟢 *LIVRE*"
        if not df_atracados.empty and 'Berço' in df_atracados.columns:
            atracado = df_atracados[df_atracados['Berço'].str.contains(b_id, na=False, case=False)]
            if not atracado.empty:
                navio_atual = atracado.iloc[0]['Navio']
                status = f"🔴 *OCUPADO*\n🚢 *Navio:* {navio_atual}"

        # 2. Verifica Programação
        prog_texto = "📋 _Sem programação futura._\n"
        if not df_previstas.empty and 'Berço' in df_previstas.columns:
            progs = df_previstas[df_previstas['Berço'].str.contains(b_id, na=False, case=False)]
            if not progs.empty:
                prog_texto = "📋 _Prog. Futura:_\n"
                for _, r in progs.head(3).iterrows():
                    m = str(r['Manobra']).upper()
                    tipo = "➡️ ENTRADA" if "ENTRADA" in m or "ENTRAR" in m else "⬅️ SAÍDA"
                    prog_texto += f"  • {r['Data/Hora']} | {tipo} | {r['Navio']}\n"
        
        report += f"⚓ *Berço {b_nome}:* {status}\n{prog_texto}\n"

    enviar_telegram(report)

if __name__ == "__main__":
    executar()