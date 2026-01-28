import requests
import pandas as pd
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=15)
    except:
        pass

def buscar_dados(url):
    # Cabeçalho completo de navegador real para evitar o bloqueio "Cloudflare"
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9'
    }
    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=30)
        # O flavor html5lib é mais lento porém muito mais difícil de ser bloqueado
        tabelas = pd.read_html(res.text, flavor='html5lib')
        return tabelas[0]
    except Exception as e:
        print(f"Erro na URL {url}: {e}")
        return pd.DataFrame()

def executar():
    df_atracados = buscar_dados("https://www.praticagem.org.br/navios-atracados.html")
    df_previstas = buscar_dados("https://www.praticagem.org.br/manobras-previstas.html")
    
    if df_atracados.empty and df_previstas.empty:
        enviar_telegram("⚠️ *Aviso:* O site da Praticagem está recusando a conexão do servidor agora. Nova tentativa em 1 hora.")
        return

    report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

    for b_id, b_nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
        # 1. Status de Atracação
        status = "🟢 *LIVRE*"
        if not df_atracados.empty:
            atracado = df_atracados[df_atracados.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)]
            if not atracado.empty:
                navio_atual = atracado.iloc[0]['Navio']
                status = f"🔴 *OCUPADO*\n🚢 *Navio:* {navio_atual}"

        # 2. Programação de Manobras
        prog_texto = "📋 _Sem programação futura._\n"
        if not df_previstas.empty:
            progs = df_previstas[df_previstas.astype(str).apply(lambda x: x.str.contains(b_id, case=False)).any(axis=1)]
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