import requests
import pandas as pd
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': mensagem, 'parse_mode': 'Markdown'}
    requests.post(url, data=payload)

def executar():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        # 1. Consulta Navios Atracados (Confirmação de ocupação)
        res_atracados = requests.get("https://www.praticagem.org.br/navios-atracados.html", headers=headers, timeout=20)
        df_atracados = pd.read_html(res_atracados.text)[0]
        
        # 2. Consulta Manobras Previstas (Programação futura)
        res_previstas = requests.get("https://www.praticagem.org.br/manobras-previstas.html", headers=headers, timeout=20)
        df_previstas = pd.read_html(res_previstas.text)[0]
        
        report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

        for b_id, b_nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
            # Verifica se há navio atracado agora
            atracado = df_atracados[df_atracados['Berço'].str.contains(b_id, na=False, case=False)]
            
            if not atracado.empty:
                navio_atual = atracado.iloc[0]['Navio']
                status = f"🔴 *OCUPADO*\n🚢 *Navio:* {navio_atual}"
            else:
                status = "🟢 *LIVRE*"

            # Busca programação na tabela de manobras
            progs = df_previstas[df_previstas['Berço'].str.contains(b_id, na=False, case=False)]
            
            info = f"⚓ *Berço {b_nome}:* {status}\n"
            if not progs.empty:
                info += "📋 _Prog. Futura:_\n"
                for _, r in progs.head(3).iterrows():
                    manobra = str(r['Manobra']).upper()
                    tipo = "➡️ ENTRADA" if "ENTRAR" in manobra or "ENTRADA" in manobra else "⬅️ SAÍDA"
                    info += f"  • {r['Data/Hora']} | {tipo} | {r['Navio']}\n"
            else:
                info += "📋 _Sem programação futura._\n"
            
            report += info + "\n"

        enviar_telegram(report)

    except Exception as e:
        enviar_telegram("⚠️ *Erro técnico:* Os sites da Praticagem podem estar instáveis. Tente novamente em instantes.")

if __name__ == "__main__":
    executar()
