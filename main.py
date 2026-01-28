import requests
import pandas as pd
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown"
    requests.get(url)

def executar():
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        # 1. Verificar quem está REALMENTE atracado agora
        res_atracados = requests.get("https://www.praticagem.org.br/navios-atracados.html", headers=headers, timeout=20)
        df_atracados = pd.read_html(res_atracados.text)[0]
        atracados_p1 = df_atracados[df_atracados['Berço'].str.contains('TUBP1S|TUBP1N', na=False, case=False)]

        # 2. Verificar a programação futura
        res_previstas = requests.get("https://www.praticagem.org.br/manobras-previstas.html", headers=headers, timeout=20)
        df_previstas = pd.read_html(res_previstas.text)[0]
        
        report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"

        for berço_id, nome in [('TUBP1S', 'SUL (P1S)'), ('TUBP1N', 'NORTE (P1N)')]:
            # Checa se há navio atracado neste berço específico
            atracado_agora = atracados_p1[atracados_p1['Berço'].str.contains(berço_id, na=False, case=False)]
            
            if not atracado_agora.empty:
                navio = atracado_agora.iloc[0]['Navio']
                status = f"🔴 *OCUPADO* \n🚢 *Navio:* {navio}"
            else:
                status = "🟢 *LIVRE*"

            # Filtra programação futura para este berço
            futuro = df_previstas[df_previstas['Berço'].str.contains(berço_id, na=False, case=False)]
            
            info = f"⚓ *Berço {nome}:* {status}\n"
            if not futuro.empty:
                info += "📋 _Prog. Futura:_\n"
                # Pega as 2 próximas manobras
                for _, r in futuro.head(2).iterrows():
                    info += f"  • {r['Data/Hora']} - {r['Navio']} ({r['Manobra']})\n"
            else:
                info += "📋 _Sem programação futura._\n"
            
            report += info + "\n"

        enviar_telegram(report)

    except Exception as e:
        enviar_telegram(f"⚠️ *Erro técnico:* {str(e)}")

if __name__ == "__main__":
    executar()
