import streamlit as st
import pandas as pd
from datetime import datetime

def SalvaDati():
    # Carica i file CSV
    dati_generali = pd.read_csv("files/DatiGenerali.csv")
    dati_piping = pd.read_csv("files/DatiPiping.csv")

    # Crea una colonna vuota
    #colonna_vuota = pd.DataFrame(['' for _ in range(max(len(dati_generali), len(dati_piping)))], columns=[''])
    colonna_vuota = pd.DataFrame({'': [None] * max(len(dati_generali), len(dati_piping))})
    # Inserisci l'intestazione personalizzata nella colonna vuota
    colonna_vuota.columns = [f"HeatLoss4 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"]
        
    # Allinea le righe dei due file in modo che abbiano la stessa lunghezza
    dati_generali = dati_generali.reindex(range(max(len(dati_generali), len(dati_piping))))
    dati_piping = dati_piping.reindex(range(max(len(dati_generali), len(dati_piping))))

    # Unisci i due DataFrame con la colonna vuota tra di loro
    dati_uniti = pd.concat([dati_generali, colonna_vuota, dati_piping], axis=1)

    # Permetti all'utente di scaricare il file
    csv = dati_uniti.to_csv(index=False)
    st.download_button(label="💾 Download file hl4_dati.CSV", data=csv, file_name="hl4_dati.csv", mime="text/csv", help= '***click here to save data in your personal drive***')
