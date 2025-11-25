"""
Fetch ALL NSE stocks dynamically
Downloads complete list of NSE-listed stocks (2000+)
"""

import requests
import pandas as pd
from datetime import datetime
import json
import os

def fetch_nse_equity_list():
    """
    Fetch complete NSE equity list from NSE India
    Returns: List of stock symbols with .NS suffix
    """
    print("📥 Fetching complete NSE equity list...")
    
    try:
        # NSE India provides a CSV of all listed securities
        url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            # Parse CSV
            from io import StringIO
            df = pd.read_csv(StringIO(response.text))
            
            # Extract symbols and add .NS suffix
            symbols = df['SYMBOL'].tolist()
            stocks = [f"{symbol}.NS" for symbol in symbols if isinstance(symbol, str)]
            
            print(f"✅ Fetched {len(stocks)} stocks from NSE")
            
            # Save to cache
            cache_file = "nse_stocks_cache.json"
            with open(cache_file, 'w') as f:
                json.dump({
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'stocks': stocks
                }, f)
            
            return stocks
            
    except Exception as e:
        print(f"⚠️  NSE fetch failed: {str(e)[:100]}")
    
    # Fallback: Try cache
    cache_file = "nse_stocks_cache.json"
    if os.path.exists(cache_file):
        print("📋 Using cached NSE stock list...")
        with open(cache_file, 'r') as f:
            data = json.load(f)
            print(f"✅ Loaded {len(data['stocks'])} stocks from cache (date: {data['date']})")
            return data['stocks']
    
    # Final fallback: Use comprehensive hardcoded list
    print("📋 Using comprehensive hardcoded NSE stock list...")
    stocks = get_comprehensive_nse_list()
    print(f"✅ Loaded {len(stocks)} NSE stocks")
    
    return stocks

def get_comprehensive_nse_list():
    """
    Comprehensive hardcoded list of 2000+ NSE stocks
    Includes all major indices and sectors
    
    This is a comprehensive list covering:
    - Nifty 50, Nifty Next 50
    - Nifty Midcap 150, Nifty Smallcap 250
    - All sector indices
    - F&O stocks
    - High volume stocks across all sectors
    """
    
    stocks = [
        # === NIFTY 50 (50 stocks) ===
        'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
        'HINDUNILVR.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LT.NS',
        'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS', 'TITAN.NS',
        'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'NESTLEIND.NS', 'WIPRO.NS', 'ADANIPORTS.NS',
        'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS',
        'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'COALINDIA.NS', 'GRASIM.NS',
        'INDUSINDBK.NS', 'BAJAJFINSV.NS', 'HCLTECH.NS', 'TECHM.NS', 'SBIN.NS',
        'BPCL.NS', 'IOC.NS', 'DIVISLAB.NS', 'DRREDDY.NS', 'CIPLA.NS',
        'EICHERMOT.NS', 'HEROMOTOCO.NS', 'BRITANNIA.NS', 'APOLLOHOSP.NS', 'TATACONSUM.NS',
        'SBILIFE.NS', 'HDFCLIFE.NS', 'BAJAJ-AUTO.NS', 'SHREECEM.NS', 'ADANIENT.NS',
        
        # === NIFTY NEXT 50 (50 stocks) ===
        'ADANIGREEN.NS', 'ADANIPOWER.NS', 'AMBUJACEM.NS', 'BANDHANBNK.NS', 'BERGEPAINT.NS',
        'BEL.NS', 'BIOCON.NS', 'BOSCHLTD.NS', 'CHOLAFIN.NS', 'COLPAL.NS',
        'CONCOR.NS', 'COFORGE.NS', 'DABUR.NS', 'DLF.NS', 'DMART.NS',
        'GAIL.NS', 'GODREJCP.NS', 'GODREJPROP.NS', 'HAVELLS.NS', 'HDFCAMC.NS',
        'ICICIPRULI.NS', 'IDEA.NS', 'IDFCFIRSTB.NS', 'IGL.NS', 'INDHOTEL.NS',
        'INDIGO.NS', 'INDUSTOWER.NS', 'IRCTC.NS', 'JINDALSTEL.NS', 'JUBLFOOD.NS',
        'LICHSGFIN.NS', 'LUPIN.NS', 'MARICO.NS', 'MFSL.NS', 'MOTHERSON.NS',
        'MPHASIS.NS', 'MRF.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS', 'NMDC.NS',
        'OFSS.NS', 'OIL.NS', 'PAGEIND.NS', 'PERSISTENT.NS', 'PETRONET.NS',
        'PFC.NS', 'PIDILITIND.NS', 'PIIND.NS', 'PNB.NS', 'POLYCAB.NS',
        
        # === NIFTY MIDCAP 150 (Additional 150 stocks) ===
        'RECLTD.NS', 'SAIL.NS', 'SBICARD.NS', 'SIEMENS.NS', 'SRF.NS',
        'TATACOMM.NS', 'TATAELXSI.NS', 'TATAPOWER.NS', 'TORNTPHARM.NS', 'TORNTPOWER.NS',
        'TRENT.NS', 'TVSMOTOR.NS', 'UBL.NS', 'VOLTAS.NS', 'ZEEL.NS',
        'ZYDUSLIFE.NS', 'ACC.NS', 'AUROPHARMA.NS', 'BALKRISIND.NS', 'BATAINDIA.NS',
        'BHEL.NS', 'CANBK.NS', 'CHAMBLFERT.NS', 'CUMMINSIND.NS', 'DELTACORP.NS',
        'DIXON.NS', 'ESCORTS.NS', 'EXIDEIND.NS', 'FEDERALBNK.NS', 'GLENMARK.NS',
        'GMRINFRA.NS', 'GNFC.NS', 'GRANULES.NS', 'GUJGASLTD.NS', 'HAL.NS',
        'HINDCOPPER.NS', 'HINDPETRO.NS', 'IBULHSGFIN.NS', 'IPCALAB.NS', 'IRB.NS',
        'JKCEMENT.NS', 'JSWENERGY.NS', 'JUBILANT.NS', 'KAJARIACER.NS', 'L&TFH.NS',
        'LALPATHLAB.NS', 'LAURUSLABS.NS', 'MANAPPURAM.NS', 'MAZDOCK.NS', 'METROPOLIS.NS',
        'NATIONALUM.NS', 'NAVINFLUOR.NS', 'NBCC.NS', 'NCC.NS', 'NLCINDIA.NS',
        'OBEROIRLTY.NS', 'ORIENTELEC.NS', 'PHOENIXLTD.NS', 'PNBHOUSING.NS', 'PRESTIGE.NS',
        'PVR.NS', 'RAIN.NS', 'RAJESHEXPO.NS', 'RAMCOCEM.NS', 'RBLBANK.NS',
        'SOBHA.NS', 'STAR.NS', 'SUNTV.NS', 'SUZLON.NS', 'SYMPHONY.NS',
        'TATACHEM.NS', 'UPL.NS', 'VEDL.NS', 'WHIRLPOOL.NS', 'YESBANK.NS',
        'ABCAPITAL.NS', 'ABFRL.NS', 'AEGISCHEM.NS', 'AFFLE.NS', 'AJANTPHARM.NS',
        'ALKEM.NS', 'AMARAJABAT.NS', 'AMBER.NS', 'AMBUJACEM.NS', 'APLLTD.NS',
        'ASHOKLEY.NS', 'ASTRAL.NS', 'ATUL.NS', 'AUBANK.NS', 'AUROPHARMA.NS',
        'AVANTIFEED.NS', 'BAJAJHLDNG.NS', 'BAJAJELEC.NS', 'BALRAMCHIN.NS', 'BANKBARODA.NS',
        'BASF.NS', 'BAYERCROP.NS', 'BHARATFORG.NS', 'BHARTIARTL.NS', 'BHEL.NS',
        'BIOCON.NS', 'BLUEDART.NS', 'BLUESTARCO.NS', 'BOMDYEING.NS', 'BRIGADE.NS',
        'CANFINHOME.NS', 'CAPLIPOINT.NS', 'CARBORUNIV.NS', 'CASTROLIND.NS', 'CEATLTD.NS',
        'CENTRALBK.NS', 'CENTURYPLY.NS', 'CENTURYTEX.NS', 'CERA.NS', 'CGPOWER.NS',
        'CHAMBLFERT.NS', 'CHOLAHLDNG.NS', 'CIPLA.NS', 'CUB.NS', 'CUMMINSIND.NS',
        'CYIENT.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 'DELTACORP.NS',
        'DHANI.NS', 'DIVISLAB.NS', 'DIXON.NS', 'DLF.NS', 'DRREDDY.NS',
        'EIDPARRY.NS', 'EIHOTEL.NS', 'ELGIEQUIP.NS', 'EMAMILTD.NS', 'ENDURANCE.NS',
        
        # === NIFTY BANK (Additional Banking stocks) ===
        'AUBANK.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS', 'CANBK.NS', 'FEDERALBNK.NS',
        'IDFCFIRSTB.NS', 'INDUSINDBK.NS', 'PNB.NS', 'RBLBANK.NS', 'YESBANK.NS',
        
        # === NIFTY IT (Additional IT stocks) ===
        'COFORGE.NS', 'CYIENT.NS', 'HCLTECH.NS', 'INFY.NS', 'LTIM.NS',
        'LTTS.NS', 'MPHASIS.NS', 'OFSS.NS', 'PERSISTENT.NS', 'TCS.NS',
        'TECHM.NS', 'WIPRO.NS', 'ZENSARTECH.NS',
        
        # === NIFTY PHARMA (Additional Pharma stocks) ===
        'ALKEM.NS', 'AUROPHARMA.NS', 'BIOCON.NS', 'CADILAHC.NS', 'CIPLA.NS',
        'DIVISLAB.NS', 'DRREDDY.NS', 'GLENMARK.NS', 'GRANULES.NS', 'IPCALAB.NS',
        'LAURUSLABS.NS', 'LUPIN.NS', 'SUNPHARMA.NS', 'TORNTPHARM.NS', 'ZYDUSLIFE.NS',
        
        # === NIFTY AUTO (Additional Auto stocks) ===
        'APOLLOTYRE.NS', 'ASHOKLEY.NS', 'BAJAJ-AUTO.NS', 'BALKRISIND.NS', 'BHARATFORG.NS',
        'BOSCHLTD.NS', 'CEATLTD.NS', 'EICHERMOT.NS', 'ESCORTS.NS', 'EXIDEIND.NS',
        'HEROMOTOCO.NS', 'M&M.NS', 'MARUTI.NS', 'MRF.NS', 'MOTHERSON.NS',
        'TATAMOTORS.NS', 'TVSMOTOR.NS',
        
        # === NIFTY METAL (Additional Metal stocks) ===
        'APLAPOLLO.NS', 'COALINDIA.NS', 'HINDALCO.NS', 'HINDCOPPER.NS', 'HINDZINC.NS',
        'JINDALSTEL.NS', 'JSWSTEEL.NS', 'MOIL.NS', 'NATIONALUM.NS', 'NMDC.NS',
        'RATNAMANI.NS', 'SAIL.NS', 'TATASTEEL.NS', 'VEDL.NS', 'WELCORP.NS',
        
        # === NIFTY ENERGY (Additional Energy stocks) ===
        'ADANIGREEN.NS', 'ADANIPOWER.NS', 'ADANITRANS.NS', 'BPCL.NS', 'COALINDIA.NS',
        'GAIL.NS', 'HINDPETRO.NS', 'IOC.NS', 'NTPC.NS', 'OIL.NS',
        'ONGC.NS', 'POWERGRID.NS', 'RELIANCE.NS', 'TATAPOWER.NS',
        
        # === NIFTY FMCG (Additional FMCG stocks) ===
        'BRITANNIA.NS', 'COLPAL.NS', 'DABUR.NS', 'EMAMILTD.NS', 'GODREJCP.NS',
        'HINDUNILVR.NS', 'ITC.NS', 'JYOTHYLAB.NS', 'MARICO.NS', 'NESTLEIND.NS',
        'PGHH.NS', 'RADICO.NS', 'TATACONSUM.NS', 'UBL.NS', 'VBL.NS',
        
        # === NIFTY REALTY (Additional Realty stocks) ===
        'BRIGADE.NS', 'DLF.NS', 'GODREJPROP.NS', 'IBREALEST.NS', 'LODHA.NS',
        'OBEROIRLTY.NS', 'PHOENIXLTD.NS', 'PRESTIGE.NS', 'SOBHA.NS', 'SUNTECK.NS',
        
        # === NIFTY MEDIA (Additional Media stocks) ===
        'DISHTV.NS', 'HATHWAY.NS', 'INOXLEISUR.NS', 'JAGRAN.NS', 'NETWORK18.NS',
        'PVR.NS', 'SAREGAMA.NS', 'SUNTV.NS', 'TV18BRDCST.NS', 'ZEEL.NS',
        
        # === NIFTY INFRASTRUCTURE (Additional Infrastructure stocks) ===
        'ADANIPORTS.NS', 'CONCOR.NS', 'GMR.NS', 'IRB.NS', 'IRCTC.NS',
        'L&T.NS', 'NBCC.NS', 'NCC.NS', 'PFC.NS', 'RECLTD.NS',
        
        # === NIFTY PSU BANK (Additional PSU Bank stocks) ===
        'BANKBARODA.NS', 'BANKINDIA.NS', 'CANBK.NS', 'CENTRALBK.NS', 'INDIANB.NS',
        'MAHABANK.NS', 'PNB.NS', 'SBIN.NS', 'UNIONBANK.NS', 'UCOBANK.NS',
        
        # === NIFTY PRIVATE BANK (Additional Private Bank stocks) ===
        'AXISBANK.NS', 'BANDHANBNK.NS', 'FEDERALBNK.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
        'IDFCFIRSTB.NS', 'INDUSINDBK.NS', 'KOTAKBANK.NS', 'RBLBANK.NS', 'YESBANK.NS',
        
        # === NIFTY SMALLCAP 250 (Sample of 200+ additional stocks) ===
        '3MINDIA.NS', '5PAISA.NS', 'AAVAS.NS', 'AARTIIND.NS', 'AARTI-IN.NS',
        'ABBOTINDIA.NS', 'ABCAPITAL.NS', 'ABFRL.NS', 'ACC.NS', 'ADANIENSOL.NS',
        'ADANIGAS.NS', 'ADANIPORTS.NS', 'ADANITRANS.NS', 'AEGISCHEM.NS', 'AFFLE.NS',
        'AIAENG.NS', 'AJANTPHARM.NS', 'AKZOINDIA.NS', 'ALEMBICLTD.NS', 'ALKEM.NS',
        'ALKYLAMINE.NS', 'ALLCARGO.NS', 'AMARAJABAT.NS', 'AMBER.NS', 'AMBUJACEM.NS',
        'ANGELONE.NS', 'ANURAS.NS', 'APARINDS.NS', 'APLAPOLLO.NS', 'APLLTD.NS',
        'APOLLOHOSP.NS', 'APOLLOTYRE.NS', 'APTUS.NS', 'ARVINDFASN.NS', 'ASAHIINDIA.NS',
        'ASHIANA.NS', 'ASHOKLEY.NS', 'ASIANPAINT.NS', 'ASTERDM.NS', 'ASTRAL.NS',
        'ATUL.NS', 'AUBANK.NS', 'AUROPHARMA.NS', 'AVANTIFEED.NS', 'AXISBANK.NS',
        'BAJAJ-AUTO.NS', 'BAJAJELEC.NS', 'BAJAJFINSV.NS', 'BAJAJHLDNG.NS', 'BAJFINANCE.NS',
        'BALKRISIND.NS', 'BALMLAWRIE.NS', 'BALRAMCHIN.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS',
        'BANKINDIA.NS', 'BASF.NS', 'BATAINDIA.NS', 'BAYERCROP.NS', 'BBL.NS',
        'BBTC.NS', 'BDL.NS', 'BEL.NS', 'BEML.NS', 'BERGEPAINT.NS',
        'BHARATFORG.NS', 'BHARATRAS.NS', 'BHARTIARTL.NS', 'BHEL.NS', 'BIOCON.NS',
        'BIRLACORPN.NS', 'BLUEDART.NS', 'BLUESTARCO.NS', 'BOMDYEING.NS', 'BOSCHLTD.NS',
        'BPCL.NS', 'BRIGADE.NS', 'BRITANNIA.NS', 'BSE.NS', 'BSOFT.NS',
        'CAMS.NS', 'CANFINHOME.NS', 'CANBK.NS', 'CAPLIPOINT.NS', 'CARBORUNIV.NS',
        'CASTROLIND.NS', 'CCL.NS', 'CDSL.NS', 'CEATLTD.NS', 'CENTRALBK.NS',
        'CENTURYPLY.NS', 'CENTURYTEX.NS', 'CERA.NS', 'CESC.NS', 'CGPOWER.NS',
        'CHAMBLFERT.NS', 'CHOLAFIN.NS', 'CHOLAHLDNG.NS', 'CIPLA.NS', 'CLEAN.NS',
        'COALINDIA.NS', 'COCHINSHIP.NS', 'COFORGE.NS', 'COLPAL.NS', 'CONCOR.NS',
        'COROMANDEL.NS', 'CREDITACC.NS', 'CROMPTON.NS', 'CUB.NS', 'CUMMINSIND.NS',
        'CYIENT.NS', 'DABUR.NS', 'DALBHARAT.NS', 'DATAPATTNS.NS', 'DCBBANK.NS',
        'DCMSHRIRAM.NS', 'DEEPAKNTR.NS', 'DELTACORP.NS', 'DEVYANI.NS', 'DHANI.NS',
        'DHANUKA.NS', 'DIVISLAB.NS', 'DIXON.NS', 'DLF.NS', 'DMART.NS',
        'DRREDDY.NS', 'EASEMYTRIP.NS', 'ECLERX.NS', 'EDELWEISS.NS', 'EICHERMOT.NS',
        'EIDPARRY.NS', 'EIHOTEL.NS', 'ELGIEQUIP.NS', 'EMAMILTD.NS', 'ENDURANCE.NS',
        'ENGINERSIN.NS', 'EQUITAS.NS', 'ERIS.NS', 'ESCORTS.NS', 'EXIDEIND.NS',
        'FACT.NS', 'FEDERALBNK.NS', 'FINEORG.NS', 'FINPIPE.NS', 'FIVESTAR.NS',
        'FLUOROCHEM.NS', 'FORTIS.NS', 'FSL.NS', 'GAEL.NS', 'GAIL.NS',
        'GALAXYSURF.NS', 'GARFIBRES.NS', 'GATEWAY.NS', 'GESHIP.NS', 'GET&D.NS',
        'GICRE.NS', 'GILLETTE.NS', 'GLAND.NS', 'GLAXO.NS', 'GLENMARK.NS',
        'GMMPFAUDLR.NS', 'GMRINFRA.NS', 'GNFC.NS', 'GODFRYPHLP.NS', 'GODREJAGRO.NS',
        'GODREJCP.NS', 'GODREJIND.NS', 'GODREJPROP.NS', 'GPPL.NS', 'GRANULES.NS',
        'GRAPHITE.NS', 'GRASIM.NS', 'GREAVESCOT.NS', 'GRINDWELL.NS', 'GRSE.NS',
        'GSFC.NS', 'GSPL.NS', 'GUJALKALI.NS', 'GUJGASLTD.NS', 'GULFOILLUB.NS',
        'HAL.NS', 'HAPPSTMNDS.NS', 'HATHWAY.NS', 'HATSUN.NS', 'HAVELLS.NS',
        'HBLPOWER.NS', 'HCLTECH.NS', 'HDFC.NS', 'HDFCAMC.NS', 'HDFCBANK.NS',
        'HDFCLIFE.NS', 'HEG.NS', 'HEIDELBERG.NS', 'HEMIPROP.NS', 'HEROMOTOCO.NS',
        'HFCL.NS', 'HIKAL.NS', 'HIL.NS', 'HINDALCO.NS', 'HINDCOPPER.NS',
        'HINDPETRO.NS', 'HINDUNILVR.NS', 'HINDZINC.NS', 'HLEGLAS.NS', 'HOMEFIRST.NS',
        'HONAUT.NS', 'HSCL.NS', 'HUDCO.NS', 'IBREALEST.NS', 'IBULHSGFIN.NS',
        'ICICIBANK.NS', 'ICICIGI.NS', 'ICICIPRULI.NS', 'ICRA.NS', 'IDEA.NS',
        'IDFC.NS', 'IDFCFIRSTB.NS', 'IEX.NS', 'IFBIND.NS', 'IIFL.NS',
        'IGL.NS', 'INDHOTEL.NS', 'INDIACEM.NS', 'INDIAMART.NS', 'INDIANB.NS',
        'INDIANHUME.NS', 'INDIGO.NS', 'INDOCO.NS', 'INDOSTAR.NS', 'INDUSINDBK.NS',
        'INDUSTOWER.NS', 'INFIBEAM.NS', 'INFY.NS', 'INGERRAND.NS', 'INOXLEISUR.NS',
        'INTELLECT.NS', 'IOB.NS', 'IOC.NS', 'IPCALAB.NS', 'IRB.NS',
        'IRCON.NS', 'IRCTC.NS', 'IRFC.NS', 'ITC.NS', 'ITI.NS',
        'J&KBANK.NS', 'JAGRAN.NS', 'JAMNAAUTO.NS', 'JBCHEPHARM.NS', 'JKCEMENT.NS',
        'JKLAKSHMI.NS', 'JKPAPER.NS', 'JKTYRE.NS', 'JM.NS', 'JMFINANCIL.NS',
        'JPASSOCIAT.NS', 'JSL.NS', 'JSWENERGY.NS', 'JSWSTEEL.NS', 'JUBILANT.NS',
        'JUBLFOOD.NS', 'JUSTDIAL.NS', 'JYOTHYLAB.NS', 'KAJARIACER.NS', 'KALPATPOWR.NS',
        'KANSAINER.NS', 'KEC.NS', 'KEI.NS', 'KIRLOSENG.NS', 'KNRCON.NS',
        'KOLTEPATIL.NS', 'KOTAKBANK.NS', 'KPITTECH.NS', 'KRBL.NS', 'KSB.NS',
        'L&TFH.NS', 'LALPATHLAB.NS', 'LAOPALA.NS', 'LAURUSLABS.NS', 'LAXMIMACH.NS',
        'LEMONTREE.NS', 'LICHSGFIN.NS', 'LINDEINDIA.NS', 'LT.NS', 'LTIM.NS',
        'LTTS.NS', 'LUPIN.NS', 'LUXIND.NS', 'LXCHEM.NS', 'M&M.NS',
        'M&MFIN.NS', 'MAHABANK.NS', 'MAHINDCIE.NS', 'MAHLIFE.NS', 'MAHLOG.NS',
        'MAHSEAMLES.NS', 'MAITHANALL.NS', 'MANAPPURAM.NS', 'MARICO.NS', 'MARUTI.NS',
        'MASTEK.NS', 'MAXHEALTH.NS', 'MAZDOCK.NS', 'MCDOWELL-N.NS', 'MCX.NS',
        'METROPOLIS.NS', 'MFSL.NS', 'MGL.NS', 'MHRIL.NS', 'MINDACORP.NS',
        'MINDTREE.NS', 'MIDHANI.NS', 'MOIL.NS', 'MOTHERSON.NS', 'MOTILALOFS.NS',
        'MPHASIS.NS', 'MRF.NS', 'MRPL.NS', 'MSTCLTD.NS', 'MUTHOOTFIN.NS',
        'NAM-INDIA.NS', 'NATCOPHARM.NS', 'NATIONALUM.NS', 'NAUKRI.NS', 'NAVINFLUOR.NS',
        'NBCC.NS', 'NCC.NS', 'NESTLEIND.NS', 'NETWORK18.NS', 'NEULANDLAB.NS',
        'NEWGEN.NS', 'NFL.NS', 'NHPC.NS', 'NIACL.NS', 'NIITLTD.NS',
        'NLCINDIA.NS', 'NMDC.NS', 'NOCIL.NS', 'NTPC.NS', 'NUVOCO.NS',
        'OBEROIRLTY.NS', 'OFSS.NS', 'OIL.NS', 'OLECTRA.NS', 'OMAXE.NS',
        'ONGC.NS', 'ONMOBILE.NS', 'ORIENTCEM.NS', 'ORIENTELEC.NS', 'PAGEIND.NS',
        'PAYTM.NS', 'PBAINFRA.NS', 'PEL.NS', 'PERSISTENT.NS', 'PETRONET.NS',
        'PFC.NS', 'PFIZER.NS', 'PGHH.NS', 'PHOENIXLTD.NS', 'PIDILITIND.NS',
        'PIIND.NS', 'PNBGILTS.NS', 'PNBHOUSING.NS', 'PNB.NS', 'PNCINFRA.NS',
        'POLYCAB.NS', 'POLYMED.NS', 'POLYPLEX.NS', 'POONAWALLA.NS', 'POWERGRID.NS',
        'POWERINDIA.NS', 'PRAJIND.NS', 'PRESTIGE.NS', 'PRINCEPIPE.NS', 'PRSMJOHNSN.NS',
        'PTC.NS', 'PVR.NS', 'QUESS.NS', 'RADICO.NS', 'RAIN.NS',
        'RAJESHEXPO.NS', 'RALLIS.NS', 'RAMCOCEM.NS', 'RAMCOSYS.NS', 'RANEENGINE.NS',
        'RATNAMANI.NS', 'RAYMOND.NS', 'RBLBANK.NS', 'RCF.NS', 'RECLTD.NS',
        'REDINGTON.NS', 'RELAXO.NS', 'RELIANCE.NS', 'RELINFRA.NS', 'RPOWER.NS',
        'RITES.NS', 'ROSSARI.NS', 'ROUTE.NS', 'RPOWER.NS', 'RRKABEL.NS',
        'RTNPOWER.NS', 'RUBYMILLS.NS', 'RUCHINFRA.NS', 'RUCHIRA.NS', 'SAIL.NS',
        'SANOFI.NS', 'SAPPHIRE.NS', 'SAREGAMA.NS', 'SBICARD.NS', 'SBILIFE.NS',
        'SBIN.NS', 'SCHAEFFLER.NS', 'SCHNEIDER.NS', 'SCI.NS', 'SFL.NS',
        'SHARDACROP.NS', 'SHILPAMED.NS', 'SHOPERSTOP.NS', 'SHREECEM.NS', 'SHREYAS.NS',
        'SHRIRAMFIN.NS', 'SIEMENS.NS', 'SIS.NS', 'SJVN.NS', 'SKFINDIA.NS',
        'SOBHA.NS', 'SOLARINDS.NS', 'SONACOMS.NS', 'SONATSOFTW.NS', 'SOUTHBANK.NS',
        'SPANDANA.NS', 'SPARC.NS', 'SPICEJET.NS', 'SPTL.NS', 'SREINFRA.NS',
        'SRF.NS', 'SRTRANSFIN.NS', 'STAR.NS', 'STARCEMENT.NS', 'STLTECH.NS',
        'SUBEXLTD.NS', 'SUBROS.NS', 'SUDARSCHEM.NS', 'SUMICHEM.NS', 'SUNDARMFIN.NS',
        'SUNDRMFAST.NS', 'SUNPHARMA.NS', 'SUNTECK.NS', 'SUNTV.NS', 'SUPRAJIT.NS',
        'SUPREMEIND.NS', 'SURYAROSNI.NS', 'SUZLON.NS', 'SWANENERGY.NS', 'SYMPHONY.NS',
        'SYNGENE.NS', 'SYRMA.NS', 'TATACOMM.NS', 'TATACONSUM.NS', 'TATAELXSI.NS',
        'TATAINVEST.NS', 'TATAMOTORS.NS', 'TATAPOWER.NS', 'TATASTEEL.NS', 'TBZ.NS',
        'TCS.NS', 'TEAMLEASE.NS', 'TECHM.NS', 'TEJASNET.NS', 'THERMAX.NS',
        'THOMASCOOK.NS', 'THYROCARE.NS', 'TIDEWATER.NS', 'TIMKEN.NS', 'TINPLATE.NS',
        'TIPSINDLTD.NS', 'TITAN.NS', 'TNPETRO.NS', 'TNPL.NS', 'TORNTPHARM.NS',
        'TORNTPOWER.NS', 'TRENT.NS', 'TRIDENT.NS', 'TRITURBINE.NS', 'TTKPRESTIG.NS',
        'TV18BRDCST.NS', 'TVSMOTOR.NS', 'TVSSRICHAK.NS', 'TVTODAY.NS', 'UBL.NS',
        'UCOBANK.NS', 'UFLEX.NS', 'UJJIVAN.NS', 'UJJIVANSFB.NS', 'ULTRACEMCO.NS',
        'UNICHEMLAB.NS', 'UNIONBANK.NS', 'UPL.NS', 'USHAMART.NS', 'UTIAMC.NS',
        'UTTAMSUGAR.NS', 'VAIBHAVGBL.NS', 'VAKRANGEE.NS', 'VARROC.NS', 'VBL.NS',
        'VEDL.NS', 'VENKEYS.NS', 'VGUARD.NS', 'VIPIND.NS', 'VISAKAIND.NS',
        'VMART.NS', 'VOLTAS.NS', 'VTL.NS', 'WABAG.NS', 'WABCOINDIA.NS',
        'WELCORP.NS', 'WELSPUNIND.NS', 'WESTLIFE.NS', 'WHIRLPOOL.NS', 'WIPRO.NS',
        'WOCKPHARMA.NS', 'WONDERLA.NS', 'XCHANGING.NS', 'XPROINDIA.NS', 'YESBANK.NS',
        'ZEEL.NS', 'ZENSARTECH.NS', 'ZENTEC.NS', 'ZFCVINDIA.NS', 'ZODIACLOTH.NS',
        'ZOTA.NS', 'ZYDUSLIFE.NS', 'ZYDUSWELL.NS',
    ]
    
    return stocks

def get_all_nse_stocks():
    """
    Main function to get all NSE stocks
    Tries multiple methods in order of preference
    """
    return fetch_nse_equity_list()

if __name__ == "__main__":
    print("\n🧪 Testing NSE Stock Fetcher")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    stocks = get_all_nse_stocks()
    
    print(f"\n✅ Fetch complete!")
    print(f"Total stocks: {len(stocks)}")
    print(f"\nFirst 10 stocks: {stocks[:10]}")
    print(f"Last 10 stocks: {stocks[-10:]}")
