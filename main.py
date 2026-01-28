import requests
import pandas as pd
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={mensagem}&parse_mode=Markdown"
    requests.get(url)

def executar():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get("https://www.praticagem.org.br/manobras-previstas.html", headers=headers, timeout=20)
        df = pd.read_html(res.text)[0]
        
        # Filtros para os berços do Pier 1
        sul = df[df['Berço'].str.contains('TUBP1S', na=False, case=False)]
        norte = df[df['Berço'].str.contains('TUBP1N', na=False, case=False)]

        def analisar_berco(dados, nome):
            # Se houver manobra do tipo 'Atracação' ou 'Permanência' agora, está ocupado
            atracado = dados[dados['Manobra'].str.contains('ATRACAR|PERMANECER', na=False, case=False)]
            programado = dados[~dados['Manobra'].str.contains('ATRACAR', na=False, case=False)]
            
            status = "🔴 *OCUPADO*" if not atracado.empty else "🟢 *LIVRE*"
            info = f"⚓ *Berço {nome}:* {status}\n"
            
            if not programado.empty:
                info += "📋 _Prog. Futura:_\n"
                for _, r in programado.head(2).iterrows(): # Mostra os 2 próximos
                    info += f"  • {r['Navio']} ({r['Manobra']})\n"
            else:
                info += "📋 _Sem programação futura._\n"
            return info

        report = "📋 *REPORT TÉCNICO - PIER 1*\n\n"
        report += analisar_berco(sul, "SUL (P1S)")
        report += "\n"
        report += analisar_berco(norte, "NORTE (P1N)")
        
        enviar_telegram(report)

    except Exception as e:
        enviar_telegram(f"⚠️ *Erro na extração:* {str(e)}")

if __name__ == "__main__":
    executar()