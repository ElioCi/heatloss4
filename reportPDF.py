import streamlit as st
import pandas as pd
import csv
from fpdf import FPDF
from create_table_fpdf2 import PDF
import re
#from table_function import create_table

def UpdateReportPdf():
    # create FPDF object
    # layout ('P', 'L')
    # unit ('mm', 'cm', 'in')
    # format ('A3', 'A4 (default), 'A5', 'Letter', (100, 150))

    #title = 'Pipe heat loss analysis report'

    '''
    class PDF(FPDF):
        def header(self):
            #logo
            self.image('assets/rep.jpg', 15,5,12 )
            self.set_font('helvetica', 'B', 15)
            # padding
            #self.cell(80)
            # Title
            
            title_w = self.get_string_width(title)
            doc_w = self.w
            
            self.set_x((doc_w - title_w)/2)

            self.cell(10,10, title, border=False, new_y= 'NEXT', align='L')
            # line breack
            self.set_draw_color(255,0,0)
            self.line(10,5,200,5)
            self.line(10,25,200,25)

        # page footer
        def footer(self):
            # set position of the footer 
            doc_w = self.w 
            self.set_xy(doc_w/2,-15)
            self.set_font('helvetica', 'I', 10)
            # page number
            self.cell(10, 10, f'Page {self.page_no()}/{{nb}}')  

    '''
    pdf = PDF('L', 'mm', 'A3')

    #get total pages
    pdf.alias_nb_pages()

    # Add a page
    pdf.add_page()
    # specify font ('times', 'courier', 'helvetica', symbol', zpfdingbats')
    # 'B'(bold), 'U'(underlined), 'I'(italic), ''(regular), combination(i.e.,('BU'))
    #pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(0,0,0)

    # add text
    # w= width
    # h= height
    # txt = your text
    # ln (0 False; 1 True - move cursor down to next line)
    # border (0 False; 1 True - add border around cell)
    pdf.set_xy(10, 30)
    #pdf.cell(120, 100, 'Hello World', new_y= 'NEXT', border=True)
    pdf.set_font('times', '', 12)
    #text = 'Pipe heat loss analysis'
    #pdf.cell(80,10, text)

    #leggi Units da Units
    with open('files/units.csv', newline='') as file_units:
        readerUnits = csv.reader(file_units)
        #dfUnits = [rowUn for rowUn in readerUnits]
    
        # Ottieni le intestazioni (prima riga)
        headerUnits = next(readerUnits)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        headerUnits[0] = re.sub(r'[^A-Za-z0-9]+', '_', headerUnits[0])
    
        # Leggi i dati rimanenti
        dfUnits = [rowUn for rowUn in readerUnits]
        
    # Aggiungi la nuova intestazione ai dati
    dfUnits.insert(0, headerUnits)
    

    #leggi dati di input da DatiGenerali.csv
    with open('files/DatiGenerali.csv') as file_input:
        reader = csv.reader(file_input)
        data = [row for row in reader]

    #leggi dati di input da DatiPiping.csv
    #with open('files/DatiPiping.csv') as pip_input:
    #    readerpip = csv.reader(pip_input)
    #    datapip = [rowpip for rowpip in readerpip]


    # Leggi i dati di input da 'DatiPiping.csv'
    with open('files/DatiPiping.csv', newline='') as pip_input:
        readerpip = csv.reader(pip_input)
        
        # Ottieni le intestazioni (prima riga)
        header = next(readerpip)
        
        # Modifica la prima colonna se il nome è 'Unnamed: 0.1'
        if header[0] == 'Unnamed: 0.1':
            header[0] = 'id'  # Rinomina la prima colonna
        
        # Leggi i dati rimanenti
        datapip = [rowpip for rowpip in readerpip]

    # Aggiungi la nuova intestazione ai dati
    datapip.insert(0, header)






    #leggi risultati da Output.csv
    with open('files/Output.csv') as output:
        readerout = csv.reader(output)

        # Leggi la prima riga e memorizzala
        first_line = ', '.join(next(readerout))
        
        # Leggi la seconda riga e memorizzala
        second_line = ', '.join(next(readerout))
        
        # Salta la terza riga
        next(readerout)

    #    # Ignora le prime tre righe
    #    for _ in range(3):
    #        next(readerout)
        # Leggi le righe successive e formattale
        out = []
        for rowout in readerout:
            formatted_row = []
            for value in rowout:
                try:
                    # Prova a convertire in float e formattare
                    formatted_value = f"{float(value):.3f}"
                except ValueError:
                    # Se non è un numero, lascia il valore originale
                    formatted_value = value
                formatted_row.append(formatted_value)
            out.append(formatted_row)

    # Ora `out` contiene i valori con tre cifre decimali per i numeri.


    pdf.cell(100,10, first_line, border=False , new_y= 'NEXT', align='L')
    pdf.set_x(10)
    pdf.cell(100,10, second_line, border=False, new_y= 'NEXT', align='L')
    pdf.ln()


    #pdf.create_table(table_data = data,title='I\'m the first title', cell_width='even')
    pdf.create_table(table_data = dfUnits, title='Units of measurement', cell_width='uneven')
    pdf.ln()
    pdf.ln()

    #pdf.create_table(table_data = data,title='I\'m the first title', cell_width='even')
    pdf.create_table(table_data = data, title='General Data', cell_width='uneven')
    pdf.ln()
    pdf.ln()

    #pdf.create_table(Piping data)
    pdf.create_table(table_data = datapip, title='Piping Data', cell_width='uneven')
    pdf.ln()
    pdf.ln()


    #pdf.create_table(Piping data)
    pdf.create_table(table_data = out, title='Output', cell_width='uneven')
    pdf.ln()
    pdf.ln()

    pdf.add_page()
    pdf.set_font('times', 'BU', 12)
    pdf.cell(80,10, 'Symbols Legend', ln=1, border=False)

    pdf.set_font('times', '', 12)
    # Definizione delle larghezze per le colonne
    column1_width = 50
    column2_width = 100

    # Aggiunta delle righe con tabulazioni
    pdf.cell(column1_width, 10, 'Section:', border=0)
    pdf.cell(column2_width, 10, 'pipe section', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Segment:', border=0)
    pdf.cell(column2_width, 10, 'segment of pipe into which the pipe section is divided', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Length:', border=0)
    pdf.cell(column2_width, 10, 'segment length', ln=1, border=0)

    pdf.cell(column1_width, 10, 'L_Progr:', border=0)
    pdf.cell(column2_width, 10, 'progressive length', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Qcd:', border=0)
    pdf.cell(column2_width, 10, 'Heat transfer quantity', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Qcd_segment:', border=0)
    pdf.cell(column2_width, 10, 'Heat transfer quantity of the segment', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Tf:', border=0)
    pdf.cell(column2_width, 10, 'Fluid temperature', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Tmetal:', border=0)
    pdf.cell(column2_width, 10, 'Pipe metal surface temperature', ln=1, border=0)

    pdf.cell(column1_width, 10, 'Ti-n:', border=0)
    pdf.cell(column2_width, 10, 'n-layer insulation surface temperature', ln=1, border=0)   

    pdf.cell(column1_width, 10, 'Ts:', border=0)
    pdf.cell(column2_width, 10, 'External pipe surface temperature', ln=1, border=0)   

    pdf.add_page()
    pdf.image('files/grafico.png', x=30, y=50, w=300) 

    pdf.output('files/report1.pdf')

    

