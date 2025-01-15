import streamlit as st


st.title('ℹ️ \u2003info ')
st.write('---')
st.markdown('### Application for heat loss analysis in a piping system')
st.write('')
st.write('**Scope**')
st.write('The scope of the software is to calculate thermal heat loss and consequently the fluid temperature drop in a piping system troughout several layers of insulation.')
st.write('')
st.write('**Program Flow**')

st.write('**Main**: select new or stored project and press ***start*** ... ➡️ **General Data**: input data and tick the checkbox to confirm ... ➡️ **Temperature Drop**: describe the piping circuit, tick the checkbox ***Ready to run*** and then click on ***Run*** button to perform the analysis. At the end of analysis, the button ***Dowload PDF Report*** will appear in the sidebar 🏁')
st.write('')

st.write('**Analysis method**')
st.write('The analysis method is iterative. For each section of pipe, the program calculates the amount of heat exchanged by radiation, convection and conduction and performs a balancing to find the equilibrium state step by step. ')
st.write('Once equilibrium is reached, the temperature values ​​of the fluid and the temperature reached by the surface of the various insulation layers are obtained. ')
st.write('The results will be reported in a table and displayed in a graph showing the temperature drop along the path of the pipe. ')
st.markdown('')

st.markdown('')
st.markdown('')
st.info("-- ©️ App developed by ing. Pasquale Aurelio Cirillo - Release 1.0 2025 --")

#st.markdown('<p style="color:red;">ℹ️ Questo è un messaggio di informazione in rosso</p>', unsafe_allow_html=True)
