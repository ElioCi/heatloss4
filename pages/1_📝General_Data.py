import streamlit as st

import pandas as pd
import csv
import os

# inizializza session_state
if 'newFlag' not in st.session_state:
    st.session_state.newFlag = 'none'
if 'dataGen' not in st.session_state:
    st.session_state['dataGen'] = []
if 'JAccount' not in st.session_state:
    st.session_state.JAccount = ""
if 'Project' not in st.session_state:
    st.session_state.Project = ""
if 'Location' not in st.session_state:
    st.session_state.Location = ""
if 'Wind' not in st.session_state:
    st.session_state.Wind = 0.00
if 'Ta' not in st.session_state:
    st.session_state.Ta = 0.00    
if 'dataConfirmed' not in st.session_state:
    st.session_state.dataConfirmed = False  

if 'flagChanges' not in st.session_state:
    st.session_state.flagChanges = False  

# functions


#print ('newFlag = ', st.session_state.newFlag)
#---in caso non hai fatto alcuna scelta torna alla main page ---
if st.session_state.newFlag == "none":
    pagina = 'pages/🗂️Main.py'
    st.switch_page(pagina)
#---------------------------------------------

st.sidebar.info(st.session_state.newFlag)

if st.session_state.newFlag == "stored":
    # Titolo dell'applicazione
    st.title('📝 General Data - Stored project')
    st.session_state.flagChanges = False
    #st.subheader('Environmental data')

elif st.session_state.newFlag == "new":
    st.title('📝 General Data - New project')
    st.session_state.flagChanges = True


with st.expander("🆘 Help"):
    st.markdown("""
    - **What to do here?**  
      Input or change general data as: Job account, title and location, wind velocity, external temperature.
      These last two values will be used in the analysis.                
    - **Before to go on ...**  
      Be sure the introduced values are correct and confirm them by ticking checkbox ***Data confirmed***. 
      Note that until this checkbox is unticked, it is not possible to perform the analysis and move to ***pipe run data*** input section, included in ***Temperature Drop*** menu voice.
    - **further information:**  
      click on ℹ️ info button menu]
    """)

#leggi dati di input da DatiGenerali.csv
with open('files/DatiGenerali.csv') as file_input:
    dfgen = pd.read_csv(file_input)   # lettura file e creazione
    dfgen.drop(dfgen.columns[dfgen.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)

st.session_state.JAccount = dfgen.loc[0,'JAccount']
st.session_state.Project = dfgen.loc[0,'Project']
st.session_state.Location = dfgen.loc[0,'Location']
st.session_state.Wind = dfgen.loc[0,'Wind']
st.session_state.Ta = dfgen.loc[0,'Ta']
col1, col2 = st.columns([1,3])
JAccount = col1.text_input('Job Account', value = st.session_state.JAccount)
Project = col2.text_input('Project', value = st.session_state.Project)
Location = col2.text_input('Location', value = st.session_state.Location)
col1, col2 = st.columns([1,1])
Wind = col1.number_input('Wind velocity (m/s)', min_value=0.0, step=0.1, value= st.session_state.Wind )
Ta = col2.number_input('External temperature (°C)', min_value=-273.0, step=0.1,  value= st.session_state.Ta)

# Definisci il layout della colonna
#col1 = st.columns(1)[0]
# Pulsante per acquisire i dati


col1, col2, col3 = st.columns([1,1,1])
checkbox_state = col1.checkbox('Data confirmed', value=st.session_state.dataConfirmed)
#checkbox_state = col1.checkbox('Data confirmed')
# Pulsante per acquisire i dati
if checkbox_state:
    #os.remove("files/DatiGenerali.csv")
    st.session_state['dataGen'] = [{
        'JAccount': JAccount,
        'Project': Project,
        'Location': Location,
        'Wind': Wind,
        'Ta': Ta,
    }]
    st.session_state.dataConfirmed = True
    st.success('Data confirmed and stored successfully! Double click to untick checkbox.')
    df = pd.DataFrame(st.session_state['dataGen'])
    st.subheader('Summary of general data')
    st.dataframe(df, hide_index= True)
    df.to_csv("files/DatiGenerali.csv")   # salva dati su DatiPiping  
    if col1.button('Temperature Drop'):
        st.switch_page('pages/2_📉Temperature_Drop.py')
    

else:
    
    st.session_state.dataConfirmed = False
    st.warning('Data not confirmed! Double click to tick checkbox and confirm input data.')
    
    #df = pd.DataFrame(st.session_state['dataGen'])
    #st.subheader('Summary of general data')
    #st.dataframe(df, hide_index= True)
    #df.to_csv("files/DatiGenerali.csv")   # salva dati su DatiPiping      
# Ritorno a Main
if col3.button('Back to Main'):
    st.switch_page('pages/🗂️Main.py')
# Ritorno a Main




