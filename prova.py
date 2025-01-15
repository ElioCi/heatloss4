import streamlit as st
import pandas as pd
import numpy as np

# Prima sezione (Nome e Età)
df1 = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Ciccio', 'Pasquale'],
    'Age': [25, 30, 50, 60]
})

# Seconda sezione (Città e Popolazione)
df2 = pd.DataFrame({
    'City': ['New York', 'Los Angeles'],
    'Population': [8000000, 4000000]
})

# Aggiungi una singola colonna vuota tra le due sezioni
df_colonna_vuota = pd.DataFrame({'Separator': [np.nan] * len(df2)})

# Concatenare le sezioni in termini di colonne (colonne aggiunte accanto)
df_concat = pd.concat([df1, df_colonna_vuota, df2], axis=1)

# Scrivi il DataFrame concatenato in un CSV
df_concat.to_csv('files/prova1.csv', index=False)




# Leggi il CSV
df = pd.read_csv('files/prova1.csv')
# Visualizza il DataFrame completo per capire la struttura
st.write("DataFrame completo:")
st.write(df)
# Verifica i tipi di dati per capire se ci sono problemi
st.write("Tipi di dati:")
st.write(df.dtypes)
# Usa un selettore per scegliere quale sezione mostrare
sezione = st.selectbox("Scegli la sezione da visualizzare", ['Tutte', 'Sezione 1: Name/Age', 'Sezione 2: City/Population'])
# Visualizza la tabella in base alla sezione scelta
if sezione == 'Tutte':
    st.write(df)
elif sezione == 'Sezione 1: Name/Age':
    st.write("Sezione 1 (Name/Age):")
    st.write(df[['Name', 'Age']].dropna())
elif sezione == 'Sezione 2: City/Population':
    st.write("Sezione 2 (City/Population):")
    st.write(df[['City', 'Population']].dropna())