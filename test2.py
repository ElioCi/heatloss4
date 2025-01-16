import streamlit as st
import pandas as pd
import csv
import ast
import altair as alt
import numpy as np
import os
from datetime import datetime

from calcoli import Irraggiamento, Convezione, Conduzione, Dispersione
from altair_saver import save
from PIL import Image

import asyncio
from pyppeteer import launch

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

async def save_chart(chart_html, output_file):
    browser = await launch(headless=True, args=["--no-sandbox","--disable-setuid-sandbox"])
    page = await browser.newPage()
    await page.setContent(chart_html)
    await page.screenshot(path=output_file)
    await browser.close()

# Salva il grafico come immagine
def save_chart_as_image(chart, filename='files/grafico.png'):
    # Configurazione del driver Selenium per il rendering
    options = Options()
    #options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Esegui in modalità headless
    #options.add_argument("--no-sandbox")  # Necessario per ambienti cloud
    #options.add_argument("--disable-dev-shm-usage")  # Risolve problemi di memoria
    #options.add_argument("--disable-gpu")  # Migliora compatibilità
    # Imposta il percorso del driver usando ChromeDriverManager
    service = Service(ChromeDriverManager().install())
    # Inizializza il driver con le opzioni e il servizio
    driver = webdriver.Chrome(service=service, options=options)
    
    #driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    # Usa Streamlit per renderizzare il grafico in un file HTML temporaneo
    chart.save('files/grafico.html')
    
    # Usa Selenium per prendere uno screenshot del file HTML
    driver.get('file://' + os.path.abspath('files/grafico.html'))
    driver.save_screenshot(filename)
    driver.quit()
    
def Esegui():
    
    
    st.title('Calculation')
    
    placeholder = st.empty()
    tempoIniziale = datetime.now()
    placeholder.write(f"Execution started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ... ***running, please be patient I'm working for you*** ...")
    progress1_bar = st.progress(0)
    progress1_text = st.empty()
    st.session_state.dataConfirmed = True
    #Lettura dati generali
    with open('files/DatiGenerali.csv') as file_gen:
        dfgen = pd.read_csv(file_gen, index_col=False)   # lettura file e creazione
        dfgen.drop(dfgen.columns[dfgen.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)


    Ta = dfgen['Ta'][0]
    W = dfgen['Wind'][0]

    #st.write ('Ta e wind', Ta, W)

    st.write(dfgen)


    #Lettura dati Piping
    with open('files/DatiPiping.csv') as file_input:
        df_pip = pd.read_csv(file_input)   # lettura file e creazione
        df_pip.drop(df_pip.columns[df_pip.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)
        somma_subd = df_pip['numSubd'].sum()

    # lettura tabella di conversione diametri inches/mm
    with open('files/ExtDia.csv') as file_extDia:
        dfDia = pd.read_csv(file_extDia, delimiter = ";", index_col= 1)   # lettura file e creazione dataFrame e indicizzazione secondo colonna 1 (DN)

    rows = df_pip.shape[0]
    #print('numero di righe', rows)

    if 'lprog' not in st.session_state:
        st.session_state.lprog = 0.00   

    variabili = {}
    for i, row in df_pip.iterrows():
        variabili[f'riga_{i}'] = row.to_dict()

    # Visualizza le variabili in Streamlit
    #st.write("I record del DataFrame salvati in variabili:")
    #for key, value in variabili.items():
    #    st.write(f"{key}: {value}")
        
    st.session_state.lprog = 0.00
    percent_complete = 0

    for r in range (0, rows):          # ciclo su tutte le righe del dataframe da 0 a rows

        # Calcola la percentuale di completamento
        if rows == 0:
            percent_complete = int(((r+1)/ (rows)) * 100)
            
        elif rows != 0:
            percent_complete = int(((r+1)/ (rows)) * 100)
            
        # Aggiorna la progress bar
        progress1_bar.progress(percent_complete)
        progress1_text.text(f"Total Progress: {r+1}/{rows} ({percent_complete}%)")
        
        if r == rows-1:
            progress1_text.text(f"Total Progress: {r+1}/{rows} ({percent_complete}%) - Almost finished ... Preparing results for display ...")
    

        section = r
        # leggi una riga per volta captando le variabili ed esegui i calcoli
        st.write('reading data of **section**', r)
        rigacorrente = variabili[f'riga_{r}']
        name = rigacorrente['Name']
        material = rigacorrente['Material']
        tipo = rigacorrente['Type']
        condTubo = rigacorrente['Conductivity']
        length = rigacorrente['Length']
        numItems = rigacorrente['numItems']
        numSubd = rigacorrente['numSubd']
        diameter = str(rigacorrente['Diameter'])
        thickness = rigacorrente['Thickness']
        #print('diamter = ', diameter)
        externalDia = dfDia.loc[diameter, 'Dia']
        #print('extDia =' , externalDia)    
        thk = thickness /1000  # metri
        OD = float(externalDia.replace(",","."))/1000   # Diametro OD in metri
        ID = OD-2*thk  # Diametro ID in metri
        pressure = rigacorrente['Pressure']
        Tr = rigacorrente['Temperature']
        P = rigacorrente['Flow']
        cal_spc = rigacorrente['cal_spc']
        finish = rigacorrente['finish']
        emissivity = rigacorrente['Emissivity']
        condFinish = rigacorrente['condFinish']
        thkFinish = rigacorrente['ThkFinish']/1000
        autoTF = rigacorrente['autoTF']
        numLayers = rigacorrente['Layers']
        # Recupera i valori dei vari strati
        codeinsul_str =  rigacorrente['codeInsul']
        codeinsul_list = ast.literal_eval(codeinsul_str)
        codeinsul_dict = {}
        insulThk_str = rigacorrente['insulThk']
        insulThk_list = ast.literal_eval(insulThk_str)
        insulThk_dict = {}
       
        for i in range(numLayers):
            #f'condinsul_{i}' = condinsul_list[i-1]
            codeinsul_dict[f'codeinsul_{i}'] = codeinsul_list[i]
            insulThk_dict[f'insulThk_{i}'] = insulThk_list[i]

        #st.write("numLayers = ", numLayers)

        if  (numLayers == 0 ):
            thki1 = 1.0/1000
            thki2 = 0.0
            thki3 = 0.0
            thki4 = 0.0
            thki5 = 0.0
            d1 = OD + 2*thki1     # metri
            d2 = 0.0
            d3 = 0.0
            d4 = 0.0
            d5 = 0.0
            codei1 = ""
            codei2 = ""
            codei3 = ""
            codei4 = ""
            codei5 = ""
            DFinish = d1 + 2*thkFinish    # metri

        elif  (numLayers == 1 ):
            thki1 = insulThk_dict['insulThk_0']/1000
            thki2 = 0.0
            thki3 = 0.0
            thki4 = 0.0
            thki5 = 0.0
            d1 = OD + 2*thki1      # metri
            d2 = 0.0
            d3 = 0.0
            d4 = 0.0
            d5 = 0.0
            codei1 = codeinsul_dict['codeinsul_0']
            codei2 = ""
            codei3 = ""
            codei4 = ""
            codei5 = ""
            DFinish = d1 + 2*thkFinish    # metri

        elif (numLayers == 2 ):
            thki1 = insulThk_dict['insulThk_0']/1000
            thki2 = insulThk_dict['insulThk_1']/1000
            thki3 = 0.0
            thki4 = 0.0
            thki5 = 0.0
            d1 = OD + 2*thki1
            d2 = OD + 2*thki1  + 2*thki2
            d3 = 0.0
            d4 = 0.0
            d5 = 0.0
            codei1 = codeinsul_dict['codeinsul_0']
            codei2 = codeinsul_dict['codeinsul_1']
            codei3 = ""
            codei4 = ""
            codei5 = ""
            DFinish = d2 + 2*thkFinish    # metri

        elif (numLayers == 3):
            thki1 = insulThk_dict['insulThk_0']/1000
            thki2 = insulThk_dict['insulThk_1']/1000
            thki3 = insulThk_dict['insulThk_2']/1000  
            thki4 = 0.0
            thki5 = 0.0    
            d1 = OD + 2*thki1
            d2 = OD + 2*thki1 + 2*thki2
            d3 = OD + 2*thki1 + 2*thki2 + 2*thki3
            d4 = 0.0
            d5 = 0.0
            codei1 = codeinsul_dict['codeinsul_0']
            codei2 = codeinsul_dict['codeinsul_1']
            codei3 = codeinsul_dict['codeinsul_2']
            codei4 = ""
            codei5 = ""
            DFinish = d3 + 2*thkFinish

        elif (numLayers == 4):
            thki1 = insulThk_dict['insulThk_0']/1000
            thki2 = insulThk_dict['insulThk_1']/1000
            thki3 = insulThk_dict['insulThk_2']/1000        
            thki4 = insulThk_dict['insulThk_3']/1000
            thki5 = 0.0            
            d1 = OD + 2*thki1/1
            d2 = OD + 2*thki1  + 2*thki2
            d3 = OD + 2*thki1  + 2*thki2 + 2*thki3
            d4 = OD + 2*thki1  + 2*thki2 + 2*thki3 + 2*thki4
            d5 = 0.0
            codei1 = codeinsul_dict['codeinsul_0']
            codei2 = codeinsul_dict['codeinsul_1']
            codei3 = codeinsul_dict['codeinsul_2']
            codei4 = codeinsul_dict['codeinsul_3']
            codei5 = ""
            DFinish = d4 + 2*thkFinish

        elif (numLayers == 5):
            thki1 = insulThk_dict['insulThk_0']/1000
            thki2 = insulThk_dict['insulThk_1']/1000
            thki3 = insulThk_dict['insulThk_2']/1000        
            thki4 = insulThk_dict['insulThk_3']/1000 
            thki5 = insulThk_dict['insulThk_4']/1000                    
            d1 = OD + 2*thki1
            d2 = OD + 2*thki1  + 2*thki2
            d3 = OD + 2*thki1  + 2*thki2 + 2*thki3
            d4 = OD + 2*thki1  + 2*thki2 + 2*thki3 + 2*thki4   
            d5 = OD + 2*thki1  + 2*thki2 + 2*thki3 + 2*thki4 + 2*thki5
            codei1 = codeinsul_dict['codeinsul_0']
            codei2 = codeinsul_dict['codeinsul_1']
            codei3 = codeinsul_dict['codeinsul_2']
            codei4 = codeinsul_dict['codeinsul_3']
            codei5 = codeinsul_dict['codeinsul_4']
            DFinish = d5 + 2*thkFinish

        if numSubd != 0:
            LTratto = length/numSubd
            numTratti = numSubd
        elif numSubd == 0:
            LTratto= length
            numTratti = 1


        Qcd_Tratto = Dispersione(section, W, numTratti, LTratto, numLayers, Tr, Ta, condTubo, OD, ID, thk, codei1, codei2, codei3, codei4, codei5, thki1, thki2, thki3, thki4, thki5, d1, d2, d3, d4, d5, condFinish, thkFinish, DFinish, emissivity, P, cal_spc, autoTF)
        #st.write('Qcd_row = ', Qcd_Tratto)
        st.session_state.dfOut = pd.DataFrame(st.session_state['output'])
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Specifica del file CSV di output
        output_file = 'files/Output.csv'

        # Scrivi l'intestazione personalizzata con la data e la versione    
        with open(output_file, 'w', newline = '') as f:
            f.write(f"Data di esecuzione: {now}\n")
            f.write("Versione: heatloss4\n\n")  # Aggiungi una riga vuota per separare l'intestazione dai dati
            st.session_state.dfOut.to_csv(f, index=False)  # Scrivi i dati calcolati nel file CSV



    #Lettura risultati
    #with open('files/Output.csv') as out:
    #Lettura dati generali

    with open('files/Output.csv') as file_out:
        df = pd.read_csv(file_out, index_col=False, skiprows = 3)   # lettura file e creazione dataframe saltando le prime tre righe di intestazione
        df.drop(df.columns[df.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)

        # Lista colonne da verificare
        colonne_da_verificare = ['Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ti5']
        # Filtra solo le colonne effettivamente presenti nel DataFrame
        colonne_presenti = [col for col in colonne_da_verificare if col in df.columns]

        # Condizioni per la presenza delle colonne
        if len(colonne_presenti) == 1 and 'Ti1' in colonne_presenti:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ti1', 'Ts']
            print("È presente solo Ti1.")
        elif len(colonne_presenti) == 2 and set(colonne_presenti) == {'Ti1', 'Ti2'}:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ti1', 'Ti2', 'Ts']
            print("Sono presenti Ti1 e Ti2.")
        elif len(colonne_presenti) == 3 and set(colonne_presenti) == {'Ti1', 'Ti2', 'Ti3'}:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ti1', 'Ti2', 'Ti3', 'Ts']
            print("Sono presenti Ti1, Ti2 e Ti3.")
        elif len(colonne_presenti) == 4 and set(colonne_presenti) == {'Ti1', 'Ti2', 'Ti3', 'Ti4'}:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ts']
            print("Sono presenti Ti1, Ti2, Ti3 e Ti4.")
        elif len(colonne_presenti) == 5 and set(colonne_presenti) == {'Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ti5'}:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ti5', 'Ts']
            print("Sono presenti tutte le colonne Ti1, Ti2, Ti3, Ti4 e Ti5.")
        else:
            desired_order = ['Section', 'Segment', 'Length', 'L_Progr', 'Qcd', 'Qcd_segment', 'Tf', 'Tmetal', 'Ts']
            print(f"Le colonne presenti sono: {colonne_presenti}")
        
        
        # Riorganizzare il DataFrame
        df_reordered = df[desired_order]

        st.dataframe(df_reordered, hide_index= False)

        # grafico risultati
        # Assumendo che i dati siano già nel session state
        #df = st.session_state.dfOut
        
        # Controlla che le colonne esistano nel dataframe
        '''
        if {'L_Progr', 'Qcd', 'Tf', 'Ti1', 'Ts'}.issubset(df.columns):

            # Verifica se ci sono valori mancanti nelle colonne
            if df[['L_Progr', 'Qcd', 'Tf', 'Ti1', 'Ts']].isnull().values.any():
                st.write("Attenzione: Ci sono valori mancanti nelle colonne selezionate. Li rimuoviamo.")
                df = df.dropna(subset=['L_Progr', 'Qcd', 'Tf', 'Ti1', 'Ts'])
            # Trasforma il DataFrame in formato long per Altair
            df_melted = df.melt(id_vars='L_Progr', 
                                value_vars=['Qcd', 'Tf', 'Ti1', 'Ts'], 
                                var_name='Type', 
                                value_name='Temperature')
            # Definisci una scala di colori personalizzata
            color_scale = alt.Scale(domain=['Qcd', 'Tf', 'Ti1', 'Ts'], 
                                    range=['blue', 'red', 'green', 'orange'])  # Usa colori distinti
            # Definisci una scala per lo stile di linea

            # Crea il grafico con Altair
            chart = alt.Chart(df_melted).mark_line(point=True, opacity=0.7).encode(
                x=alt.X('L_Progr', title='Progressive Distance (L_Progr)'),
                y=alt.Y('Temperature', title='Temperature (°C)'),
                #color='Tipo:N',  # Colore diverso per ogni linea
                color=alt.Color('Type:N', scale=color_scale),  # Applica la scala di colori personalizzata
                #strokeDash='Tipo:N',  # Diversi stili di linea (es. tratteggiato o continuo
                tooltip=['L_Progr', 'Temperature', 'Type']  # Tooltip interattivo
            ).properties(
                title="Temperature in funzione della distanza progressiva",
                width=700,
                height=400
            ).interactive()  # Aggiunge interattività (zoom, pan)
            # Visualizza il grafico
            st.altair_chart(chart)
        else:
            st.write("Errore: Il dataframe non contiene le colonne richieste.")
        '''

        # Verifica che le colonne principali esistano nel dataframe
        
        required_columns = {'L_Progr', 'Qcd', 'Tf', 'Ts'}
        optional_columns = {'Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ti5'}

        # Controlla la presenza delle colonne opzionali e aggiungile se disponibili
        available_columns = required_columns.union(optional_columns.intersection(df.columns))

        if available_columns.issubset(df.columns):
            # Rimuovi eventuali valori mancanti nelle colonne selezionate
            #if df[list(available_columns)].isnull().values.any():
            #    st.write("Attenzione: Ci sono valori mancanti nelle colonne selezionate. Li rimuoviamo.")
            #    df = df.dropna(subset=list(available_columns))

            # Sostituisci i valori NaN con np.nan per le colonne di temperatura
            df_filled = df.fillna({'Ti1': np.nan, 'Ti2': np.nan, 'Ti3': np.nan, 'Ti4': np.nan, 'Ti5': np.nan})

            # Assicurati che L_Progr sia numerico e ordina i dati
            df_filled['L_Progr'] = pd.to_numeric(df_filled['L_Progr'], errors='coerce')
            #df_filled = df_filled.sort_values('L_Progr')
            df_filled = df_filled.sort_index(ascending=True)


            # Trasformazione del DataFrame in formato long (mantieni tutte le righe)
            melt_columns = list(required_columns.union(optional_columns))
            df_melted = df_filled.melt(id_vars='L_Progr', 
                                        value_vars=[col for col in melt_columns if col in df_filled.columns], 
                                        var_name='Type', 
                                        value_name='Value', 
                                        ignore_index=False)

            # Ordina i dati per 'L_Progr'
            #df_melted = df_melted.sort_values('L_Progr')
            df_melted = df_melted.sort_index(ascending=True)
            # Definisci una scala di colori personalizzata
            color_range = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'brown', 'magenta']
            num_types = len(df_melted['Type'].unique())
            color_scale = alt.Scale(
                domain=[col for col in ['Qcd', 'Tf', 'Ti1', 'Ti2', 'Ti3', 'Ti4', 'Ti5', 'Ts'] if col in df_filled.columns],
                range=color_range[:num_types]
            )

            # Grafico per le temperature (asse Y sinistra)
            temp_chart = alt.Chart(df_melted[df_melted['Type'] != 'Qcd']).mark_line(point=True, opacity=0.7).encode(
                x=alt.X('L_Progr', title='Progressive Distance (L_Progr)', sort='ascending'),
                y=alt.Y('Value:Q', title='Temperature (°C)', scale=alt.Scale(zero=False)),
                color=alt.Color('Type:N', scale=color_scale),
                tooltip=['L_Progr', 'Value', 'Type']
            )

            # Grafico per Qcd (asse Y destra)
            qcd_chart = alt.Chart(df_filled[df_filled['Qcd'].notnull()]).mark_line(point=True, opacity=0.7).encode(
                x=alt.X('L_Progr', title='Progressive Distance (L_Progr)', sort='ascending'),
                y=alt.Y('Qcd:Q', title='Heat Flow (W/h)', axis=alt.Axis(titleColor='blue')),
                color=alt.value('blue'),
                tooltip=['L_Progr', 'Qcd']
            )

            # Combina i due grafici
            combined_chart = alt.layer(temp_chart, qcd_chart).resolve_scale(
                y='independent'  # Risolve i due assi Y indipendentemente
            ).properties(
                title="Temperature and Heat Flow in Function of Progressive Distance",
                width=700,
                height=400
            ).interactive()

            # Visualizza il grafico
            st.altair_chart(combined_chart)
            # Salva il grafico come immagine PNG
            #save(combined_chart, "files/grafico.png")
            chart_html = combined_chart.to_html()
            asyncio.run(save_chart(chart_html, "files/grafico.png"))
        
            #save_chart_as_image(combined_chart)
            #combined_chart.save("files/grafico.png", scale_factor=2)  
            #save(combined_chart, "files/grafico.png", method="png")
        else:
            st.write("Errore: Il dataframe non contiene le colonne richieste.")


    progress1_text.text(f"Total Progress: {r+1}/{rows} ({percent_complete}%) - End. The results are displayed below on scroll.")
    deltaTempo = datetime.now() - tempoIniziale
    placeholder.write(f"Execution completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!  * **Time taken {deltaTempo}** *")
      
    # Aggiungi il pulsante di download Output.csv
    #with open(output_file, 'rb') as f:
    #    csv_data = f.read()
    
    #st.download_button(
    #    label="💾 Download file Output.csv",
    #    data=csv_data,
    #    file_name="Output.csv",
    #    mime='text/csv',
    #    key="download_button_output",  # Aggiungi un key unico per il pulsante
    #    help= '***click here to save output in your personal drive***'
    #)


    #T = 500
    #Ta = 20
    #Ts = 200
    #e = 1

    #Irrag1 = Irraggiamento(T, Ta, Ts, e)
    #print ("Qr = ", Irrag1)
