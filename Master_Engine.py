import yfinance as yf
import numpy as np
import requests
import datetime

# VERSIONE DEL SISTEMA: APEX V8 (SCUDO PULITO)
# ==========================================
TOKEN_TELEGRAM = '8762905583:AAEivBbsZPIXwaBYqQ3krdq8STpCMYqUgIk'
CHAT_ID = '8353806939'

portafoglio_attivo = {
    "BAH": {"PMC": 69.65, "Data_Acquisto": "2026-03-23", "SL_Price": 64.07},
    "BTCE.DE": {"PMC": 5.82, "Data_Acquisto": "2026-03-09", "SL_Price": 5.35},
    "DFND.AS": {"PMC": 58.45, "Data_Acquisto": "2026-03-23", "SL_Price": 53.77},
    "URNU.MI": {"PMC": 26.20, "Data_Acquisto": "2026-03-16", "SL_Price": 24.10}
}

watchlist_ingressi = {
    "DFND.AS": 400, "ALB": 400, "QCOM": 400, "AMBA": 400, "FCX": 400, 
    "REMX.MI": 400, "QCLN.MI": 400, "ETN": 400, "COPG.MI": 400, "LDO.MI": 400, 
    "ADBE": 400, "NOW": 400, "U-UN.TO": 400, "YCA.L": 400, "WBIT.DE": 400, 
    "URNM.DE": 400, "UEC": 400, "SWMR": 400
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': messaggio, 'parse_mode': 'HTML'})

def MASTER_START():
    macro = "ROSSO"
    try:
        vix = yf.download("^VIX", period="1d", progress=False)['Close'].iloc[-1].item()
        macro = "ROSSO" if vix > 30 else "GIALLO" if vix > 22 else "VERDE"
    except: pass

    report_p = ""
    for ticker, dati in portafoglio_attivo.items():
        try:
            p_att = yf.download(ticker, period="1d", progress=False)['Close'].iloc[-1].item()
            p_lordo = ((p_att / dati["PMC"]) - 1) * 100
            report_p += f"🔹 <b>{ticker}</b>: {p_lordo:.2f}% (P: {p_att:.2f})\n"
        except: report_p += f"⚠️ Errore dati per {ticker}\n"

    msg = f"📊 <b>APEX V8: SISTEMA OPERATIVO</b> 📊\n"
    msg += f"🌍 MACRO STATUS: {macro}\n\n"
    msg += "🛡️ <b>PORTAFOGLIO ATTIVO:</b>\n" + (report_p if report_p else "Vuoto")
    invia_telegram(msg)

if __name__ == "__main__":
    MASTER_START()
