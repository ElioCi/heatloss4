import streamlit as st
import pandas as pd

import math
from math import log
import csv

st.markdown("---")
st.markdown("<h3 style='text-align: Left;'>Input data </h3>", unsafe_allow_html=True)
st.markdown('---')

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
#leggi dati di input da temDati.csv
#with open('files/tempDati.csv') as file_input:
#    dftemp = pd.read_csv(file_input)   # lettura file e creazione
#    dftemp.drop(dftemp.columns[dftemp.columns.str.contains('unnamed', case= False)], axis=1, inplace= True)
        
   
def diaSelected():
    return
def thkSelected():
    return

    
dv= False


st.write("***Fluid Data***")
col1, col2, col3, col4 = st.columns(4)
# Dati fluido
fluidTemp = col1.number_input("Fluid Temperature [°C]", value= 50, step= 1, key= 'fT', disabled= dv)
extTemp = col2.number_input("External Temperature [°C]", value= 20, step= 1, key= 'eT', disabled = dv)
flowRate = col3.number_input("Fluid flow rate [kg/h]", value = 50.1, step= 0.1, key= 'fR', disabled= dv)
specHeat = col4.number_input("Specific heat [kcal/kg°C]", value=0.500, step= 0.005, format="%0.3f", key= 'sH', disabled= dv)

st.markdown("---")


st.columns(1)
st.write("***Piping Data***")
# Piping Data
# Creazione di una lista per memorizzare i dati
if 'data' not in st.session_state:
    st.session_state['data'] = []

if 'contatore' not in st.session_state:
    st.session_state.contatore = 0

j = 0

#def insert_pipe_data(j):
if st.button("Add Section"):
    col1, col2, col3, col4, col5 = st.columns([1, 1.5, 2, 2, 2] )
    st.session_state.contatore = st.session_state.contatore + 1
    j = st.session_state.contatore

    print("j = ", j)
    sectId = "ID" + str(j)
    #col1.write(f"#. {numsection}")
    col1.number_input(f":red[ID # {j}]", value= j)
    sectDesc = col2.text_input(f"Sect desc.{j}")
    hi = col3.number_input(f"Int.coeff. hi [W/m^2°K] {j}", value= 1000, step=50, disabled=dv)
    he = col4.number_input(f"Ext. coeff. he [W/m^2°K] {j}", value= 20, step=5, disabled= dv)
    condPipe = col5.number_input(f"Pipe therm cond [W/m°K] {j}", value= 52, disabled= dv )   # valore tipico acciaio
    col1, col2, col3 = st.columns(3)
    option_dia = col1.selectbox (f"Pipe ND [inches] {j}", options=(diaList), on_change= diaSelected, disabled= dv)
    thkList = df[option_dia].dropna()
    option_thk = col2.selectbox(f"Pipe sect Thk [mm] {j}", options=(thkList), on_change= thkSelected, disabled = dv)
    externalDia = dfDia.loc[option_dia, 'Dia']
    # thk = float(option_thk)
    # intDia = extDia-2*thk
    thk = float(option_thk.replace(",","."))
    extDia = float(externalDia.replace(",","."))
    intDia = extDia-2*thk
    st.session_state['extDia']= extDia
    st.session_state['thk'] = thk
    st.session_state['intDia']= intDia
    PipeLength = col3.number_input(f"Pipe sect Length [m] {j}", value = 10,  disabled= dv) # lunghezza piping
    col1, col2, col3 = st.columns(3)
    numlayers = col1.number_input(f"no of insulation layers {j}", min_value=1, max_value=3, step= 1,  disabled = dv) # strati di isolamento
    condInsul =[]
    insulThk = []
    print("numlayers =", numlayers)
    for i in range(numlayers):
        condInsul1 = col2.number_input(f"Insul therm cond [W/m°K] {j}.{i+1}", value= 0.040, step= 0.005, format="%0.3f")
        insulThk1 = col3.number_input(f"Insulation Thk [mm] {j}.{i+1}", value= 20, step= 5)
        
        condInsul.append(condInsul1)
        insulThk.append(insulThk1)
    
    
    st.markdown(
        """
        <style>
        .stRadio > div {
            flex-direction: row;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    #memorizza_pipe_data(1)
    st.session_state['data'].append({
        "ID": [st.session_state.contatore],
        "Desc": [sectDesc],
        "DN": [option_dia],
        "thksel": [option_thk],
        "eDia": [extDia],
        "thk": [thk],
        "iDia": [intDia],
        "cP": [condPipe],
        "cI": [condInsul],
        "hi": [hi],
        "he": [he],
        "condInsul": [condInsul],
        "insulThk": [insulThk],
        "PLen": [PipeLength],
 
    })
    
    # -------------------------------------


#st.button("Add Section", on_click= insert_pipe_data(j))
st.button("--Delete All--")

# Visualizzazione dei dati inseriti
if st.session_state['data']:
    df = pd.DataFrame(st.session_state['data'])
    st.subheader('Dati dei Tratti di Condotta Inseriti')
    st.dataframe(df)




