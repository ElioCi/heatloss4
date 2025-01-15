import streamlit as st
import pandas as pd
import numpy as np
from scipy import interpolate

def conducibilita_termica_interpolata(file_csv, codice_mat, temp_media):
    # Legge il file CSV
    

    df = pd.read_csv(file_csv, delimiter = ';')
    df['cond_Iso'] = df['cond_Iso'].str.replace(',', '.').astype(float)
    # Filtra il DataFrame per il materiale desiderato
    df_materiale = df[df['Code'] == codice_mat]
    
    if df_materiale.empty:
        return f"Materiale {codice_mat} non trovato nel file."
    
    # Estrai temperature e conducibilità
    temperature = df_materiale['Temp'].values
    conducibilita = df_materiale['cond_Iso'].values
# Verifica se la temperatura è fuori dal range
   
    if temp_media < temperature.min() or temp_media > temperature.max():
        messaggio = f"La temperatura {temp_media} è fuori dal range di valori disponibili."
        return messaggio
    
    # Interpolazione lineare
    interpolazione = interpolate.interp1d(temperature, conducibilita)
   
    # Calcola la conducibilità termica interpolata
    conducibilita_interpolata = interpolazione(temp_media)

    return conducibilita_interpolata

# Esempio d'uso
file_csv = "files/Cond_Isolanti.csv"
codice_mat = 'i10'
temp_media= 130


conducibilita = conducibilita_termica_interpolata(file_csv, codice_mat, temp_media)


if isinstance(conducibilita, str):
    print("La variabile è una stringa.")
    print(conducibilita)
else:
    print(f"La conducibilità termica per {codice_mat} a {temp_media}°C è {conducibilita:.4f}")


