import pandas as pd
import streamlit as st
import mysql.connector
import matplotlib.pyplot as plt
import dota


def main():
    main_page()

def main_page():
    st.set_page_config(page_title="Kursovaya", layout="wide")
    # Choose game
    st.text("Click to Analysis")
    if st.button('Dota2'):
        dota.dota_page()

if __name__ == "__main__":
    main()
