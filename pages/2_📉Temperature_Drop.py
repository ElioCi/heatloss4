import streamlit as st
import pandas as pd
import csv
import os
import ast
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utility import indicePosizione
from utility import change_widget_style
from test2 import Esegui
from generaFileUnito import SalvaDati
from reportPDF import UpdateReportPdf

# Titolo dell'applicazione
st.set_page_config(page_title="Temperature_Drop")
st.title('📉Temperature drop')

text1 = """
    - **Case of new analysis**  
      Input or change pipe run data. The system can be divided in a series of segments arbitrarily named. 
      For each segment must be assigned the diameter, the thickness, the length, and the further number of subdivisions that will be automatically created by the software. 
      The operating conditions of pressure and temperature of the fluid and the number and type of insulation layers must also be assigned.  
      By unchecking the ***Temperature calculation mode*** checkbox, it is also possible to set a different temperature for some segments if necessary.
      This is necessary in the case of a piping circuit with fluid injections at different temperatures.    
      At the end of each segment insertion step, it is necessary to click the ***Add*** button to add and save it.  
    - **Changes** 
      Input data of each segment can be changed or eliminated by selecting the relative options.           
      After selecting ***modify row***, in the viewed table must be selected the row to be changed and clicked the ***Edit*** button. 
      The section ***pipe run data*** now will contain the data of the selected row that can be changed.
      Once completed the changes you need to click the ***Update*** button. In this way the new values are active and saved .                                        
    - **Ready to Run**  
      Once input data is completed and before to eecute the analysis you have to tick ***Ready to run*** in order to perform the data check. 
      You will receive a message that inform you wether it is possible to run the analysis.
      If the message is green the ***Run*** button will be activate and the analysis can be performed.
    - **Outcomes**  
      At the end of the analysis the results will be shown in terms of table and graph.   
      For each section you can see the fluid temperature, the metal surface temperature and the surface temperature of each insulation layer.
      At the end, on the sidebar, the ***Download Pdf Report*** button will appear.
    - **further information:**  
      click on ℹ️ info button menu]
    """

text2 = """
    - **Case of stored data analysis**  
      Input or change pipe run data. The system will contain the recalled stored data. 
      You will see them by ticking the checkbox ***Ready to run*** present on the sidebar.  
      If you want to change them you have to tick the checkbox ***Allow changes***.  
    - **Changes** 
      After clicking ***Allow changes***, input data of each segment can be changed or eliminated by selecting the relative options.           
      After selecting ***modify row***, in the viewed table must be selected the row to be changed and clicked the ***Edit*** button. 
      The section ***pipe run data*** now will contain the data of the selected row that can be changed.
      Once completed the changes you need to click the ***Update*** button. In this way the new values are active and saved .                                        
    - **Ready to Run**  
      Once input data is completed and before to eecute the analysis you have to tick ***Ready to run*** in order to perform the data check. 
      You will receive a message that inform you wether it is possible to run the analysis.
      If the message is green the ***Run*** button will be activate and the analysis can be performed.
    - **Outcomes**  
      At the end of the analysis the results will be shown in terms of table and graph.   
      For each section you can see the fluid temperature, the metal surface temperature and the surface temperature of each insulation layer.
      At the end, on the sidebar, the ***Download Pdf Report*** button will appear.
    - **further information:**  
      click on ℹ️ info button menu]
    """

placeholderHelp = st.empty()


st.subheader('Pipe run data')
# Creazione di una lista per memorizzare i dati
if 'data' not in st.session_state:
    st.session_state['data'] = []

if 'newFlag' not in st.session_state:
    st.session_state.newFlag = 'none'

if 'dataConfirmed' not in st.session_state:
    st.session_state.dataConfirmed = False 

if 'checkbox' not in st.session_state:
    st.session_state.checkbox = True    

if 'testo' not in st.session_state:
    st.session_state.testo = "auto-calculation of temperature at the section end"

if 'titoloRun' not in st.session_state:
    st.session_state.titoloRun = ""

if 'output' not in st.session_state:
    st.session_state.output = [] 

#print('dataConfirmed: ', st.session_state.dataConfirmed)
if st.session_state.dataConfirmed == False:
    pagina = 'pages/1_📝General_Data.py'
    st.switch_page(pagina)
   

#lettura dati da file
diaList = []
with open('files/diametri.csv', newline='') as diameters:
    diameters_data = csv.reader(diameters)
    next(diameters_data) #salta la riga di testa
    for row in diameters_data:
        diaList.append(row[0])
with open('files/Dia_thk.csv') as file_thk:
    df = pd.read_csv(file_thk, delimiter = ";")   # lettura file e creazione dataFrame
with open('files/ExtDia.csv') as file_extDia:
    dfDia = pd.read_csv(file_extDia, delimiter = ";", index_col= 1)   # lettura file e creazione dataFrame e indicizzazione secondo colonna 1 (DN)


dfmat = pd.read_csv('files/mat_list.csv', delimiter= ';')   # lettura file e creazione dataFrame e indicizzazione secondo colonna 1 (mat_tubo)
# Elimina eventuali spazi bianchi dai nomi delle colonne e dei valori
dfmat.columns = dfmat.columns.str.strip()
dfmat['matpipe'] = dfmat['matpipe'].str.strip()
dfmat['condpipe'] = pd.to_numeric(dfmat['condpipe'], errors='coerce')

# *** Funzioni ***
# Funzione per cancellare il file CSV
def delete_input(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        st.success(f"File {file_path} eliminato con successo.")
    else:
        st.error(f"File {file_path} non trovato.")

def reloadPage(pagina):
    st.switch_page(pagina)
    
# Widget di input per inserire i dati
def diaSelected():
    st.session_state.indiceThk = 0
    return
def thkSelected():
    return

# Funzione per svuotare il contenuto dei file mantenendo solo la prima riga
def reset_files(file_path):
    # Carica i dati da entrambi i file
    df_file = pd.read_csv(file_path)
    # Mantieni solo la prima riga
    df_file = df_file.iloc[:0, :]
    # Salva il file aggiornato
    df_file.to_csv(file_path, index=False)


def aggiorna_testo(temperatura):
    if st.session_state.checkbox:
        st.session_state.testo = f"📎 Temperature at the end of each segment calculated by software. For the first section the value you entered ({temperatura}°C) will be taken into account in every case. Untick if you want to impose a change of temperature for this segment." 
    else:
        st.session_state.testo = f"📎 Temperature imposed by user. The effective value at the start of the section will be calculated as the average between the input value ({temperatura}°C) and the final temperature calculated for the previous segment."       
    

# Funzione per richiamare il valore dal dataframe
def richiama_valore(index):
    st.session_state.temp_nome_tratto = st.session_state.df.iloc[index]["Name"]
    st.session_state.temp_lungh = st.session_state.df.iloc[index]["Length"]
    st.session_state.temp_subd = st.session_state.df.iloc[index]["numSubd"]
    st.session_state.temp_numitems = st.session_state.df.iloc[index]["numItems"]
    st.session_state.temp_press = st.session_state.df.iloc[index]["Pressure"]
    st.session_state.temp_temp = st.session_state.df.iloc[index]["Temperature"]
    st.session_state.temp_portata = st.session_state.df.iloc[index]["Flow"]
    st.session_state.temp_calspc = st.session_state.df.iloc[index]["cal_spc"]
    st.session_state.temp_autoTF = st.session_state.df.iloc[index]["autoTF"]

    

def list_to_string(lst):
    return ', '.join(lst)

# Funzione per il rendering della cella modificabile
def custom_cell_editor(value):
    # Split the values into a list
    values = value.split(', ')
    return values

options= ['add/view', 'modify row', 'delete row']

if (st.session_state.newFlag == 'none' or st.session_state.newFlag == "new"):
    st.sidebar.info(st.session_state.newFlag) 

    with placeholderHelp.expander("🆘 Help"):
        st.markdown(text1)


    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()
        pagina = 'pages/2_📉Temperature_Drop.py'
        reloadPage(pagina)
        
    #st.session_state['data'] = []
elif st.session_state.newFlag == 'stored':
    st.sidebar.info(st.session_state.newFlag)
    with placeholderHelp.expander("🆘 Help"):
        st.markdown(text2)

    
    st.session_state['data'] = []
    
    st.session_state.df = pd.read_csv('files/DatiPiping.csv')
    # Itera attraverso il DataFrame e aggiungi ogni riga nel dizionario
    for idx, row in st.session_state.df.iterrows():
        nome_tratto = row['Name']
        materiale_selezionato = row['Material']
        item = row['Type']
        condPipe = row['Conductivity']
        lunghezza = row['Length']
        numItems = row['numItems']
        numSubd = row['numSubd']
        diametro = row['Diameter']
        spessore = row['Thickness']
        numlayers = row['Layers']
        codeInsul = row['codeInsul']
        insulThk = row['insulThk']
        pressione = row['Pressure']
        temperatura = row['Temperature']
        portata = row['Flow']
        cal_spc = row['cal_spc']
        voce_finitura = row['finish']
        campo_emis = [row['Emissivity']]  # Assumendo che sia una lista
        campo_cond = [row['condFinish']]  # Assumendo che sia una lista
        campo_thk = [row['ThkFinish']]    # Assumendo che sia una lista
        autoTF = row['autoTF']
        # Aggiungi i dati al dizionario in session_state
        st.session_state['data'].append({
            'Name': nome_tratto,
            'Material': materiale_selezionato,
            'Type': item,
            'Conductivity': condPipe,
            'Length': lunghezza,
            'numItems': numItems,
            'numSubd': numSubd,
            'Diameter': diametro,
            'Thickness': float(spessore),
            'Layers': numlayers,
            'codeInsul': codeInsul,
            'insulThk': insulThk,
            'Pressure': pressione,
            'Temperature': temperatura,
            'Flow': portata,
            'cal_spc': cal_spc,
            'finish': voce_finitura,
            'Emissivity': campo_emis[0],
            'condFinish': campo_cond[0],
            'ThkFinish': campo_thk[0],
            'autoTF': autoTF
        })

    # Mostra i dati caricati
    # st.write(st.session_state['data'])    
   

if 'selected_option' not in st.session_state:
    st.session_state.selected_option = options[0]  # Imposta la prima opzione come selezionata

if 'temp_nome_tratto' not in st.session_state:
    st.session_state.temp_nome_tratto = "Start"      

if 'indice' not in st.session_state:
    st.session_state.indice = 0

if 'indType' not in st.session_state:
    st.session_state.indType = 0

if 'indSurface' not in st.session_state:
    st.session_state.indSurface = 0

if 'temp_lungh' not in st.session_state:
    st.session_state.temp_lungh = 0.002

if 'temp_subd' not in st.session_state:
    st.session_state.temp_subd = 1

if 'temp_numitems' not in st.session_state:
    st.session_state.temp_numitems = 0    

if 'indiceDia' not in st.session_state:
    st.session_state.indiceDia = 0

if 'indiceThk' not in st.session_state:
    st.session_state.indiceThk = 0

if 'temp_press' not in st.session_state:
    st.session_state.temp_press = 0.0

if 'temp_temp' not in st.session_state:
    st.session_state.temp_temp = 0.0

if 'temp_portata' not in st.session_state:
    st.session_state.temp_portata = 0.002

if 'temp_calspc' not in st.session_state:
    st.session_state.temp_calspc = 1.0

if 'temp_autoTF' not in st.session_state:
    st.session_state.temp_autoTF = True

if 'indlayers' not in st.session_state:
    st.session_state.indlayers = 0   
if 'ithk0' not in st.session_state:
    st.session_state.ithk0 = 0.0
if 'ithk1' not in st.session_state:
    st.session_state.ithk1 = 0.0           
if 'ithk2' not in st.session_state:
    st.session_state.ithk2 = 0.0
if 'ithk3' not in st.session_state:
    st.session_state.ithk3 = 0.0
if 'ithk4' not in st.session_state:
    st.session_state.ithk4 = 0.0
if 'ilay0' not in st.session_state:
    st.session_state.ilay0 = 0
if 'ilay1' not in st.session_state:
    st.session_state.ilay1 = 0   
if 'ilay2' not in st.session_state:
    st.session_state.ilay2 = 0 
if 'ilay3' not in st.session_state:
    st.session_state.ilay3 = 0 
if 'ilay4' not in st.session_state:
    st.session_state.ilay4 = 0 

if 'flagModify' not in st.session_state:
    st.session_state.flagModify =""

if 'mostraPulsante' not in st.session_state:
    st.session_state.mostraPulsante = True    

if 'flagDelete' not in st.session_state:
    st.session_state.flagActDelete = ""

if 'flagChanges' not in st.session_state:
    st.session_state.flagChanges = False



if st.session_state.flagModify == "Edit":
    #change_widget_style("#F09B59", '#FFFE91')  # Colore giallo
    flg = 'Edit' # solo per non cancellare if
elif st.session_state.flagModify == "Updated":
    #change_widget_style('#75F94D', '#A1FB8E' )  # colore verde
    flg = 'Updated' # solo per non cancellare if
elif (st.session_state.flagModify == "View" or st.session_state.flagModify == ""):
    #change_widget_style('#3282F6', '#03C1FD')  # colore azzurro chiaro
    st.session_state.selected_option = options[0]

# visualizza tabella con dati caricati in csv
#st.session_state.df
#st.rerun()
if st.session_state.newFlag == 'stored': 
    if st.checkbox('Allow changes'):
        st.session_state.flagChanges = True
        st.session_state.newFlag = 'new'
        #st.session_state.mostraPulsante = True
        st.rerun()
        
    else:
        st.session_state.flagChanges = False 
        st.session_state.mostraPulsante = False

    #st.session_state.mostraPulsante = False

else:
    #st.session_state.flagChanges == True
    st.session_state.mostraPulsante = True
    


if st.session_state.newFlag != 'stored': 
    nome_tratto = st.text_input('Section Name', value=st.session_state.temp_nome_tratto, key='nome_tratto')
    # Aggiorna il valore nel session_state quando il text_input cambia
    st.session_state.temp_nome_tratto = nome_tratto

    col1, col2, col3, col4 = st.columns([1,1,1,1])

    materiale_selezionato = col1.selectbox('select a material', options= dfmat['matpipe'], index= st.session_state.indice)
    # Trova la conducibilità termica corrispondente
    conducibilita_termica = dfmat[dfmat['matpipe'] == materiale_selezionato]['condpipe'].values[0]

    tipoitem = ['straigth pipe', 'valve', 'flange', 'special item']
    item = col2.selectbox('Type', options= tipoitem, index= st.session_state.indType)


    if (item == 'valve'):
        testo = 'valves no.'
        testoL = '1 Valve Length (m)'
        numItems = col4.number_input(testo, value= st.session_state.temp_numitems, min_value=0, step=1)
        st.session_state.temp_numitems = numItems
        numSubd = 1
    elif (item == 'special item'):
        testo= 'items no.'
        testoL = '1 item Length (m)'
        numItems = col4.number_input(testo, value=st.session_state.temp_numitems, min_value=0, step=1)
        st.session_state.temp_numitems = numItems
        numSubd = 1
    elif (item == 'flange'):
        testo= 'flanges no.'
        testoL = '1 flange Length (m)'
        numItems = col4.number_input(testo, value=st.session_state.temp_numitems, min_value=0, step=1)
        st.session_state.temp_numitems = numItems
        numSubd = 1
    else:
        testo = 'subdivisions no.'
        numItems = 0
        numSubd = col4.number_input(testo, value=st.session_state.temp_subd, min_value=1, step=1)
        st.session_state.temp_subd = numSubd
        testoL = 'Length (m)'

    lunghezza = col3.number_input(testoL, value=st.session_state.temp_lungh, min_value=0.001, step=0.1)
    st.session_state.temp_lungh = lunghezza

    col1, col2, col3 = st.columns(3)

    diametro = col1.selectbox ('Pipe ND [inches]', options=(diaList), on_change= diaSelected, index= st.session_state.indiceDia)
    thkList = df[diametro].dropna()
    spessore = col2.selectbox("Pipe sect. Thk [mm]", options=(thkList), on_change= thkSelected, index= st.session_state.indiceThk)
    spessore = spessore.replace(",", ".")

    # Visualizza la conducibilità termica in un campo number_input
    condPipe = col3.number_input("Pipe thermal conductivity [W/m°K]", value= conducibilita_termica, key= 'cP', step=0.01 )   # valore tipico acciaio

    col1, col2, col3, col4 = st.columns(4)
    pressione = col1.number_input('Pressure (bar)', value=st.session_state.temp_press, min_value=0.0, step=0.1)
    temperatura = col2.number_input('Temperature (°C)', value=st.session_state.temp_temp, min_value=-273.0, step=0.1)
    portata = col3.number_input('Flow (kg/h)', value=st.session_state.temp_portata, min_value=0.001, step=0.1)
    cal_spc = col4.number_input('Spc Heat (kcal/kg)', value=st.session_state.temp_calspc, min_value=0.0, step=0.1)


    # ---- FINITURA TUBO ------------------------------------------------------------------------
    col1, col2, col3, col4 = st.columns([2.5,1,1,1])

    listaFiniture =pd.read_csv('files/finiture.csv', delimiter= ";")

    colonna_scelta = 'TypeFinish'
    lista_finiture = listaFiniture[colonna_scelta].tolist()

    voce_finitura = col1.selectbox("Surface finish", options= lista_finiture, index= st.session_state.indSurface)
    st.session_state.indSurface = lista_finiture.index(voce_finitura)

    campo_emis = listaFiniture[listaFiniture['TypeFinish'] == voce_finitura]['Emissivity'].values
    col2.write('Emissivity')
    col2.markdown(f"<span style='color: white; background-color: green; padding: 5px 25px; border-radius: 5px;'>{campo_emis[0]}</span>", unsafe_allow_html=True)
    campo_cond = listaFiniture[listaFiniture['TypeFinish'] == voce_finitura]['CondFinish'].values
    col3.markdown('Cond. (W/m°K)')
    col3.markdown(f"<span style='color: white; background-color: green; padding: 5px 25px; border-radius: 5px;'>{campo_cond[0]}</span>", unsafe_allow_html=True)
    campo_thk = listaFiniture[listaFiniture['TypeFinish'] == voce_finitura]['ThkFinish'].values
    col4.write('Thk (mm)')
    col4.markdown(f"<span style='color: white; background-color: green; padding: 5px 25px; border-radius: 5px;'>{campo_thk[0]}</span>", unsafe_allow_html=True)



    # Checkbox che cambia lo stato di session_state.checkbox
    autoTF = st.checkbox(f"Temperature calculation mode at the end of the section '{nome_tratto}'.", key="checkbox", value= st.session_state.temp_autoTF, on_change= aggiorna_testo(temperatura))
    st.warning(st.session_state.testo)

    # ---- ISOLAMENTO TERMICO --------------------------------------------------------------------
    #numlayers = st.number_input("no of insulation layers", min_value=0, max_value=3, step= 1)
    # Custom CSS per allineare le opzioni su una riga
    st.markdown(
        """
        <style>
        .stRadio > div {
            flex-direction: row;
        }
        .col3Radio > div {
            flex-direction: row;
        }

        </style>
        """,
        unsafe_allow_html=True
        )

    numlayers_opzione  = st.radio("no of insulation layers", options= ['0', '1', '2', '3', '4', '5'], index= st.session_state.indlayers)
    numlayers= int(numlayers_opzione)
    listaInsul =pd.read_csv('files/isolanti.csv', delimiter= ";")

    colonna_scelta = 'Desc'
    lista_colonna = listaInsul[colonna_scelta].tolist()

    colonna_codice = listaInsul.columns[0]  # Nome della prima colonna (codice)
    colonna_voce = listaInsul.columns[1]    # Nome della seconda colonna (voce)

    condInsul =[]
    codeInsul = []
    insulThk = []
    col1, col2, col3, col4 = st.columns([0.6, 5.4, 0.9, 0.5])
    for i in range( numlayers):
        col1.write("Layer")
        col1.write(i+1)
        if i == 0: 
            ilay = st.session_state.ilay0
            ithk = st.session_state.ithk0
        if i == 1: 
            ilay = st.session_state.ilay1
            ithk = st.session_state.ithk1
        if i == 2: 
            ilay = st.session_state.ilay2
            ithk = st.session_state.ithk2
        if i == 3:
            ilay = st.session_state.ilay3
            ithk = st.session_state.ithk3
        if i == 4: 
            ilay = st.session_state.ilay4
            ithk = st.session_state.ithk4    

        voce_selezionata = col2.selectbox(f"therm insulation {i+1}", options= lista_colonna, index=ilay)
        #condInsul1 = col2.number_input(f"therm cond [W/m°K] {i+1}", value= 0.040, step= 0.005, format="%0.3f")


        insulThk1 = col3.number_input(f"Thk [mm] {i+1}", value=ithk, step= 5.5)
        # Trova il codice associato alla voce selezionata
        codice_correlato = listaInsul[listaInsul[colonna_voce] == voce_selezionata][colonna_codice].values
        col4.write('code')
        col4.write(codice_correlato[0])
        
        #condInsul.append(condInsul1)
        codeInsul.append(codice_correlato[0])
        insulThk.append(insulThk1)    

# Pulsante per aggiungere i dati
#col1,col2, col3, col4, col5  = st.columns(5) 

# Visualizzazione e salvataggio dei dati inseriti
file_path = 'files/DatiPiping.csv'
col1, col2, col3 = st.columns([1, 1, 3])
posmodifica = st.empty()
placeholder1 = st.empty()
placeholderTable = st.empty()
#st.session_state.mostraPulsante = True
if st.session_state.mostraPulsante == True:
    if col1.button('Add Section'):
        #st.session_state.num_tratto = st.session_state.num_tratto + 1 
        
        st.session_state['data'].append({
        #    'ID': st.session_state.num_tratto-1,
            'Name': nome_tratto,
            'Material': materiale_selezionato,
            'Type': item,
            'Conductivity': condPipe,
            'Length': lunghezza,
            'numItems': numItems,
            'numSubd': numSubd,
            'Diameter': diametro,
            'Thickness': float(spessore),
            'Layers' : numlayers,
            'codeInsul': codeInsul,
            'insulThk': insulThk,
            'Pressure': pressione,
            'Temperature': temperatura,
            'Flow': portata,
            'cal_spc': cal_spc,
            'finish': voce_finitura,
            'Emissivity': campo_emis[0],
            'condFinish': campo_cond[0],
            'ThkFinish': campo_thk[0],
            'autoTF': autoTF
        })
        
        st.success(f'Section # {st.session_state.df.shape[0]} added successfully!')
        

    if col2.button("Clear"):
        #delete_input(file_path)
        #st.session_state.clear()        
        #df = pd.DataFrame() comando per azzerare dataframe
        pagina = 'pages/2_📉Temperature_Drop.py'
        st.session_state.dataConfirmed = True
        reloadPage(pagina)
        #st.rerun()
        #st.switch_page("test1.py")



    if col3.button("Back to Main"):
        pagina = 'pages/🗂️Main.py'
        st.switch_page(pagina)

    #placeholder1 = st.empty()
    #placeholderTable = st.empty()
    
if st.sidebar.checkbox('Ready to run'):
    df_piping = pd.read_csv('files/DatiPiping.csv')
    if 'Unnamed: 0' in df_piping.columns:
        df_piping = df_piping.rename(columns={'Unnamed: 0': 'id'})
    
    if st.session_state.newFlag == 'new' or st.session_state.newFlag == 'stored':        
        placeholder1.write('Summary 1 of stored data')
        placeholderTable.dataframe(df_piping, hide_index= True)

    # Controlla se il DataFrame è vuoto
    if df_piping.empty:
        st.sidebar.warning("Warning: the Piping Data are missing!")
    else:
        st.sidebar.success("Ok: The Piping Data are present!")
        SalvaDati()    
        if st.sidebar.button('🔢 Run now!', help="🤓 I'm ready. Click here to run calculation!"):   # 🧮🔢
            #pagina = "pages/3_📉Calculation.py"
            #st.switch_page(pagina)
            #reset_files('files/Output.csv')
            st.session_state.titoloRun = "Calculation running ..."
            st.session_state.output = []
            Esegui()
            # Aggiungi pulsante di Genera Report.pdf
            UpdateReportPdf()
            #st.sidebar.info("Report created !")
            # Aggiungi pulsante di download report1.pdf
            pdfReport = "files/report1.pdf"
            with open(pdfReport, "rb") as pdf_file:
                pdf_data = pdf_file.read()
            st.sidebar.download_button(
                label="Download Pdf Report",
                data=pdf_data,
                file_name="ReportHL4.pdf",
                mime="application/pdf",
                help= '***Save Report in your local drive***'
            )
 

#col1, col2, col3 = st.columns([2, 1, 3.5])
if st.session_state['data']:
    st.session_state.df = pd.DataFrame(st.session_state['data'])
    #st.subheader('Data recap')
    
    placeholder1.markdown('## Summary of stored data')
    # placeholderTable.dataframe(st.session_state.df)
    
    if st.session_state.flagModify == "View":
        st.session_state.selected_option = options[0]
        #print ('opzione', st.session_state.selected_option)
        #print ('indice opzione' , options.index(st.session_state.selected_option))

    
    
    if st.session_state.flagChanges == True:
        
        scelta = posmodifica.radio("-", options= options, index=options.index(st.session_state.selected_option))
    
        st.session_state.df.to_csv(file_path)   # salva dati su DatiPiping
          

        if scelta == 'add/view':
            #st.session_state.newFlag = 'new'
            st.session_state.flagModify = "View"
            st.session_state.mostraPulsante = True
            placeholderTable.dataframe(st.session_state.df, hide_index= False)


        if scelta == 'modify row':
            #st.session_state.newFlag = 'new'
            st.session_state.mostraPulsante = False
            st.info('please select the row that you want to modify in the table below, then press "Edit row", make your changes and then press "Update"')        
            
            # Definisci le opzioni della griglia
            gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
            # Configura la larghezza per ogni colonna
            cols_to_configure = st.session_state.df.columns[2:19]  # Configura le prime 18 colonne
            #Configura la larghezza per le colonne selezionate
            gb.configure_columns(cols_to_configure, width=30)
        
            gb.configure_selection('single')
            gridOptions = gb.build()
            # Mostra la griglia
            # Visualizza la griglia con AgGrid
            
            selected = AgGrid(pd.DataFrame(st.session_state.df), gridOptions=gridOptions, height=300, fit_columns_on_grid_load=False)
            #grid_response = AgGrid(st.session_state.df, gridOptions=gridOptions, enable_enterprise=True, update_mode='MODEL_CHANGED')
            selRows = selected['selected_rows']

            if selRows is not None and len(selRows) > 0:
            
                #st.write("You selected the following row:", selected['selected_rows'])
        
                # Accedi alla prima riga selezionata
                selected_row = selected['selected_rows'].iloc[0]['Name']
                # Trova l'indice della riga selezionata in base alla colonna 'Name'
                indici = st.session_state.df.index[st.session_state.df['Name'] == selected_row].tolist() # solo il primo indice
                selected_index = indici[0] # solo il primo indice
                
            else:
                st.write("No row selected !")
            
            # Mostra la riga selezionata
            col1, col2, col3 = st.columns([2.5, 1, 1])
        
            if col2.button('edit row'):
                st.session_state.flagModify = "Edit"
                riga = st.session_state['data'][selected_index] 
                
                richiama_valore(selected_index)    # richiama valore dal dataframe e lo inserisce nella textinput iniziale

                matSelected = riga['Material']
                if matSelected == 'Carbon Steel': st.session_state.indice= 0
                elif matSelected == 'Stainless Steel': st.session_state.indice= 1
                elif matSelected == 'Cast Iron': st.session_state.indice= 2
                elif matSelected == 'Copper': st.session_state.indice= 3
                elif matSelected == 'Aluminum': st.session_state.indice= 4

                typeSelected = riga['Type']
                if typeSelected == 'straigth pipe': st.session_state.indType = 0
                elif typeSelected == 'valve': st.session_state.indType= 1
                elif typeSelected == 'flange': st.session_state.indType= 2
                elif typeSelected == 'special item': st.session_state.indType= 3


                diametro = riga['Diameter']   
                filecsv = 'files/diametri.csv'
                colonna = 'Diam'
                valore_cercato = diametro
                st.session_state.indiceDia = indicePosizione(filecsv, colonna, valore_cercato)
                print ('posDia = ', st.session_state.indiceDia)

                # spessore 
                spess = str(riga['Thickness'])
                # Controlla se la colonna '2 1/2' è presente e accedi ai dati
                colonna = diametro
                valore_cercato = spess.replace('.',',')  # gli spessori letti hanno il punto quelli in csv la virgola
                if colonna in df.columns:
                    indici = df.index[df[colonna] == valore_cercato].tolist()
                    indPos = indici[0] # solo il primo indice
                    st.session_state.indiceThk = indPos
                #    print(f"Indici trovati: {indici}")
                else:
                    print(f"Colonna '{colonna}' non trovata")

                finitura = riga['finish']
                
                filecsv = 'files/finiture.csv'
                colonna = 'TypeFinish'
                valore_cercato = finitura
                st.session_state.indSurface = indicePosizione(filecsv, colonna, valore_cercato)

                numLayers = riga['Layers']
                st.session_state.indlayers = numLayers
                # Recupera i valori dei vari strati
                codeinsul_str =  riga['codeInsul']
                if isinstance(codeinsul_str, list):
                    codeinsul_list = codeinsul_str
                else:
                    # Usa ast.literal_eval solo se è una stringa
                    codeinsul_list = ast.literal_eval(codeinsul_str)

                codeinsul_dict = {}
                insulThk_str = riga['insulThk']
                if isinstance(insulThk_str, list):
                    insulThk_list = insulThk_str
                else:
                    # Usa ast.literal_eval solo se è una stringa
                    insulThk_list = ast.literal_eval(insulThk_str)

                insulThk_dict = {}
                
                for i in range(numLayers):
                    codeinsul_dict[f'codeinsul_{i}'] = codeinsul_list[i]
                    insulThk_dict[f'insulThk_{i}'] = insulThk_list[i]
                    st.session_state[f'ithk{i}'] = insulThk_dict[f'insulThk_{i}']
                    
                    codice = codeinsul_dict[f'codeinsul_{i}']
                    filecsv = 'files/isolanti.csv'
                    colonna = 'code'
                    valore_cercato = codice
                    
                    st.session_state[f'ilay{i}'] = indicePosizione(filecsv, colonna, valore_cercato)


                pagina = 'pages/2_📉Temperature_Drop.py'
                st.rerun()
                            
        
            if col3.button('Update!'):

                st.session_state.flagModify = "Updated"
                
                if selected_index is not None:
                
                                
                    st.session_state['data'][selected_index]['Name'] = nome_tratto
                    st.session_state['data'][selected_index]['Material'] = materiale_selezionato 
                    st.session_state['data'][selected_index]['Diameter'] = diametro
                    st.session_state['data'][selected_index]['Type'] = item
                    st.session_state['data'][selected_index]['Conductivity'] = condPipe
                    st.session_state['data'][selected_index]['Length'] = lunghezza
                    st.session_state['data'][selected_index]['numItems'] = numItems
                    st.session_state['data'][selected_index]['numSubd'] = numSubd
                    st.session_state['data'][selected_index]['Thickness'] = float(spessore)
                    st.session_state['data'][selected_index]['Layers'] = numlayers
                    st.session_state['data'][selected_index]['codeInsul'] = codeInsul
                    st.session_state['data'][selected_index]['insulThk'] = insulThk
                    st.session_state['data'][selected_index]['Pressure'] = pressione
                    st.session_state['data'][selected_index]['Temperature'] = temperatura
                    st.session_state['data'][selected_index]['Flow'] = portata
                    st.session_state['data'][selected_index]['cal_spc'] = cal_spc
                    st.session_state['data'][selected_index]['finish'] = voce_finitura
                    st.session_state['data'][selected_index]['Emissivity'] = campo_emis[0]
                    st.session_state['data'][selected_index]['condFinish'] = campo_cond[0]
                    st.session_state['data'][selected_index]['ThkFinish'] = campo_thk[0]
                    st.session_state['data'][selected_index]['autoTF'] = autoTF

                    st.session_state.df = pd.DataFrame(st.session_state['data'])
                    #st.session_state.df = st.session_state.df.drop(selected_row)
                    #st.session_state.df.reset_index(drop=True, inplace=True)
                    #st.session_state.num_tratto = st.session_state.df.shape[0]
                    #df = df.drop(selected_row)
                    #df.reset_index(drop=True, inplace=True)
                    st.success("Row successfully updated !")
                    # st.write('dataframe aggiornato', st.session_state.df)
                    st.session_state.df.to_csv("files/DatiPiping.csv")   # sostituisci file DatiPiping
                    
                    st.session_state.output = []
                    #fileOut = 'files/Output.csv'
                    #os.remove(fileOut)  # Cancella il file di Output

                    pagina = 'pages/2_📉Temperature_Drop.py'
                    st.session_state.mostraPulsante = True
                    #reloadPage(pagina)
                    st.rerun()
                    #st.write('Dataframe updated', st.session_state.df)
                    
                else:
                    st.warning("No row selected !")    


        elif(scelta == 'delete row'):
            #selected_row = st.selectbox("Select row to delete", st.session_state.df.index, format_func=lambda x: f"Row {x}")
            st.session_state.flagModify = "Delete"
            st.session_state.mostraPulsante = False
            st.info('please select the row that you want to delete in the table below, then press "Confirm !" to delete it')
            #df_selezionato = st.session_state.df.iloc[:, [0, 1, 4, 7]]
            #opzioni = df_selezionato.apply(lambda row: ' \t | '.join(row.astype(str)), axis=1)

            # Definisci le opzioni della griglia
            gb = GridOptionsBuilder.from_dataframe(st.session_state.df)
            # Configura la larghezza per ogni colonna
            cols_to_configure = st.session_state.df.columns[2:19]  # Configura le prime 18 colonne
            gb.configure_columns(cols_to_configure, width=30)
            gb.configure_selection('single')
            gridOptions = gb.build()
            # Visualizza la griglia con AgGrid
            selected = AgGrid(pd.DataFrame(st.session_state.df), gridOptions=gridOptions, height=300, fit_columns_on_grid_load=False)
            selRows = selected['selected_rows']
            st.session_state.flagActDelete = "nonAzionareDelete"
            #col1, col2, col3 = st.columns([2.5, 1, 1])
            if selRows is not None and len(selRows) > 0:
            
                #st.write("You selected the following row:", selected['selected_rows'])
        
                # Accedi alla prima riga selezionata
                #selected_row = selected['selected_rows']['Name'][0]
                if not selected['selected_rows'].empty:
                    selected_row = selected['selected_rows'].iloc[0]['Name']  # Accedi alla prima riga selezionata e al valore della colonna 'Name'
                else:
                    selected_row = None  # Nessuna riga selezionata
                
                # Trova l'indice della riga selezionata in base alla colonna 'Name'
                #indici = st.session_state.df.index[st.session_state.df['Name'] == selected_row].tolist() # solo il primo indice
                indici = st.session_state.df.loc[st.session_state.df['Name'] == selected_row].index.tolist()
                selected_index = indici[0] # solo il primo indice
                st.session_state.flagActDelete = "puoiAzionareDelete"
                st.write(f'You selected the row referred to the section: {selected_row}.')
                
                st.markdown('<p style="color:red;">If You are sure want to delete it, please Confirm.</p>', unsafe_allow_html=True)

            else:
                st.write("No row selected !")


            if st.session_state.flagActDelete != "nonAzionareDelete":
                if st.button('Confirm !'):

                    st.write('selected index delete', selected_index)
                    
                    if selected_index is not None:
        
                        del st.session_state['data'][selected_index]
                        st.session_state.df = pd.DataFrame(st.session_state['data'])
                        st.success("Row deleted successfully !")
                        st.session_state.df.to_csv("files/DatiPiping.csv")   # sostituisci file DatiPiping
                        st.session_state.flagModify = "View"
                        #st.session_state.selected_option = options[1]
                        pagina = 'pages/2_📉Temperature_Drop.py'           
                        st.session_state.flagActDelete = "nonAzionareDelete"
                        st.session_state.mostraPulsante = True
                        st.rerun()
                        #reloadPage(pagina)
                        #st.write('Dataframe updated', st.session_state.df)

                    else:
                        st.warning("No row selected.")





   

    


        



