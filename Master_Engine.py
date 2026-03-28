import yfinance as yf
import numpy as np
import requests

# VERSIONE DEL SISTEMA: APEX V8.1 (FULL ENGINE + FX LIVE)
# ==========================================
TOKEN_TELEGRAM = '8762905583:AAEivBbsZPIXwaBYqQ3krdq8STpCMYqUgIk'
CHAT_ID = '8353806939'

portafoglio_attivo = {
    "BAH": {"PMC": 69.65, "Data_Acquisto": "2026-03-23", "SL_Price": 64.07},
    "IBTC.DE": {"PMC": 5.82, "Data_Acquisto": "2026-03-09", "SL_Price": 5.35},
    "DFND.DE": {"PMC": 58.45, "Data_Acquisto": "2026-03-23", "SL_Price": 53.77},
    "URNU.MI": {"PMC": 26.20, "Data_Acquisto": "2026-03-16", "SL_Price": 24.10}
}

watchlist_ingressi = {
    "DFND.DE": 400, "ALB": 400, "QCOM": 400, "AMBA": 400, "FCX": 400, 
    "REMX.MI": 400, "QCLN.MI": 400, "ETN": 400, "COPG.MI": 400, "LDO.MI": 400, 
    "ADBE": 400, "NOW": 400, "U-UN.TO": 400, "YCA.L": 400, "IBTC.DE": 400, 
    "URNM.DE": 400, "UEC": 400, "SWMR": 400
}

def invia_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TOKEN_TELEGRAM}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': messaggio, 'parse_mode': 'HTML'})

def get_fx(ticker):
    try:
        return yf.download(ticker, period="1d", progress=False)['Close'].iloc[-1].item()
    except:
        return 1.17 # Paracadute di sicurezza se i server FX sono offline

def MASTER_START():
    # 1. GATEKEEPER MACRO
    macro = "VERDE"
    try:
        vix = yf.download("^VIX", period="1d", progress=False)['Close'].iloc[-1].item()
        macro = "ROSSO" if vix > 30 else "GIALLO" if vix > 22 else "VERDE"
    except: pass

    # 2. MONITOR USCITE E PORTAFOGLIO
    report_p = ""
    for ticker, dati in portafoglio_attivo.items():
        try:
            p_att = yf.download(ticker, period="1d", progress=False)['Close'].iloc[-1].item()
            p_lordo = ((p_att / dati["PMC"]) - 1) * 100
            report_p += f"🔹 <b>{ticker}</b>: {p_lordo:+.2f}% (Prezzo: {p_att:.2f})\n"
        except: report_p += f"⚠️ Errore lettura dati per {ticker}\n"

    # 3. RADAR INGRESSI CON MOTORE VALUTARIO
    report_w = ""
    fx_gbp_eur = get_fx("GBPEUR=X")
    fx_cad_eur = get_fx("CADEUR=X")
    fx_usd_eur = get_fx("USDEUR=X")

    if macro == "ROSSO":
        report_w = "🚨 <b>VETO ROSSO:</b> Mercato volatile. Cash is King. Nessun ingresso.\n"
    else:
        for ticker, budget in watchlist_ingressi.items():
            try:
                df = yf.download(ticker, period="1y", progress=False)
                if df.empty: continue
                p_att = df['Close'].iloc[-1].item()
                
                # Motore di Conversione Valutaria per Budget in Euro
                tasso_cambio = 1.0
                if ticker.endswith(".L"): tasso_cambio = fx_gbp_eur / 100 
                elif ticker.endswith(".TO"): tasso_cambio = fx_cad_eur
                elif not ticker.endswith(".MI") and not ticker.endswith(".DE") and not ticker.endswith(".AS"): 
                    tasso_cambio = fx_usd_eur

                counts, bins = np.histogram(df.tail(252)['Close'], bins=50, weights=df.tail(252)['Volume'])
                poc = (bins[np.argmax(counts)] + bins[np.argmax(counts)+1]) / 2
                target_in = poc * 1.02
                dist = ((p_att / target_in) - 1) * 100
                
                if dist <= 3.0:
                    quote = int(budget / (target_in * tasso_cambio))
                    valore_euro = quote * target_in * tasso_cambio
                    report_w += f"🎯 <b>BUY LIMIT:</b> {ticker} | Distanza: {dist:.1f}%\n"
                    report_w += f"▪️ In: {target_in:.2f} | Ordine: {quote} quote ({valore_euro:.2f}€)\n\n"
            except: continue

    if not report_w and macro != "ROSSO":
        report_w = "<i>Nessun asset della watchlist in zona di acquisto (POC).</i>\n"

    # 4. ASSEMBLAGGIO REPORT E INVIO
    msg = f"📊 <b>APEX V8.1: FULL ENGINE</b> 📊\n"
    msg += f"🌍 MACRO STATUS: {macro}\n\n"
    msg += "🛡️ <b>PORTAFOGLIO ATTIVO:</b>\n" + (report_p if report_p else "Vuoto\n")
    msg += "\n🔭 <b>RADAR INGRESSI:</b>\n" + report_w
    invia_telegram(msg)

if __name__ == "__main__":
    MASTER_START()
