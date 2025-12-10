import streamlit as st

# CONFIGURAZIONE PAGINA

def configura_pagina():
        st.set_page_config(
        page_title="Assistente Raccolta Differenziata", # Titolo della pagina
        page_icon="♻️", # Icona della pagina
        layout="centered" # Layout centrato, moderno
) 


def mostra_legenda_bidoni():            
        st.write("#### Legenda Bidoni") 

        # Lista dei tuoi bidoni con nomi e immagini
        bidoni = [
        {"nome": "Carta",     "img": "./icons/blue.png"},
        {"nome": "Plastica",  "img": "./icons/yellow.png"},
        {"nome": "Vetro",     "img": "./icons/green.png"},
        {"nome": "Umido",     "img": "./icons/brown.png"},
        {"nome": "Secco",     "img": "./icons/grey.png"}
        ]

        # Crea tante colonne quanti sono i bidoni nella lista
        cols = st.columns(len(bidoni))

        # Riempie le colonne
        for col, bidone in zip(cols, bidoni):  #zip per iterare su due liste contemporaneamente... crea delle coppie (Carta, colonna1), (Plastica, colonna2), ...
                with col:
                        # width=50 o 60 li tiene piccoli e ordinati, tipo icone
                        st.image(bidone["img"], width=60) 
                        st.caption(bidone["nome"])
