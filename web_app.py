import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mlxtend.frequent_patterns import association_rules, fpgrowth
from datetime import datetime
from PIL import Image
from mlxtend.preprocessing import TransactionEncoder
import warnings
import streamlit.components.v1 as components
warnings.filterwarnings("ignore")

st.image("logo_unp.png")
st.write(""" 
# Web App Recommendation
#### :books: Website Aplikasi Rekomendasi Buku Perpustakaan UNP :books:
"""
         )

# Define the sidebar or top menu
selected = option_menu(
    menu_title="Menu",
    options=["Home", "Eksplorasi Data",  "Cari Rekomendasi", "Rekomendasi Berdasarkan Fakultas"],
    menu_icon="columns-gap",
    icons=["house-fill","bar-chart-line-fill", "card-checklist", "collection-fill"],
    default_index=0,
    orientation="horizontal"
)

#Option Home
if selected == "Home":
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Home</title>
    </head>
    <body>
        <header>
            <nav>
                <a href="#">Home</a>
            </nav>
        </header>
        <section>
            <h2 class="u-align-center u-text u-text-body-alt-color u-text-default u-text-1">Perpustakaan UNP </h2>
            <p style="text-align: justify;">
    Perpustakaan UNP melakkan pengembangan pustakawan diarahkan keberbagai sektor strategis dalam rangka memasuki era informasi global, seperti penataan sistem manajemen perpustakaan, pemantapan basis teknologi informasi, pengembangan sumber daya manusia, pengoptimalan sumber daya finansial, dan kesejahteraan pustakawan. Pada masa ini Perpustakaan UNP mulai mengembangkan Student Service Center (SSC) yang menempati ruangan lantai dasar Perpustakaan UNP. SSC ini nantinya diharapkan mampu melayani berbagai kebutuhan mahasiswa, dosen, dan karyawan.</p>
    <body>
    </html>
    '''
    components.html(html_content, height=600)

# Load the dataset once to avoid reloading it multiple times
dataset = pd.read_excel('DATA PENELITIAN4.xlsx')
dataset = dataset[['Transaksi', 'Judul', 'Tahun Masuk', 'Fakultas', 'Hari']]
dataset.columns = ['Transaksi', 'Judul', 'Tahun_Masuk', 'Fakultas', 'Hari']
dataset['Tahun_Masuk'] = dataset['Tahun_Masuk'].astype(str)
rekomendasi= pd.read_excel('Hasilmerge2.xlsx')

# Option 1: Eksplorasi Data
if selected == "Eksplorasi Data":
    st.subheader('Explorasi Data')
    # Plot 1: Jumlah Peminjaman Buku menurut Tahun Masuk
    fig, ax = plt.subplots(figsize=(5, 3))
    dataset['Tahun_Masuk'].value_counts().plot(kind='bar', color='blue')
    ax.set_xlabel('Tahun Masuk')
    ax.set_ylabel('Jumlah')
    ax.set_title('Jumlah Peminjaman Buku menurut Tahun Masuk')
    st.pyplot(fig)

    # Plot 2: Jumlah Peminjaman menurut Fakultas
    fig1, ax1 = plt.subplots(figsize=(5, 3))
    dataset['Fakultas'].value_counts().plot(kind='bar', color='red')
    ax1.set_xlabel('Fakultas')
    ax1.set_ylabel('Jumlah')
    ax1.set_title('Jumlah Peminjaman menurut Fakultas')
    st.pyplot(fig1)
    st.subheader("Top 3 Rekomendasi Buku Perpustakaan UNP")
    rekomendasi[0:3]

# Option 2: Cari Rekomendasi
if selected == "Cari Rekomendasi":
    st.write("#### Cari Rekomendasi")
    
    # Load additional data
    RULE = pd.read_excel('Hasilmerge3.xlsx')
    rekomendasi = pd.read_excel('Hasilmerge2.xlsx')
    isi = pd.read_excel('JUDUL BUKU.xlsx')
    isi_item = isi['Judul'].values.tolist()

    # Input selectbox for Judul Buku
    Item = st.selectbox("Judul", isi_item)
    Item_set = frozenset([Item])

    def parse_list(x):
        if isinstance(x, frozenset):
            return ", ".join(map(str, x))
        else:
            return str(x)
    
    def return_item_judul(item_antecedents):
        DATASETS = RULE[["antecedents", "consequents"]].copy()
        DATASETS["antecedents"] = DATASETS["antecedents"].apply(parse_list)
        DATASETS["consequents"] = DATASETS["consequents"].apply(parse_list)

        item_antecedents_str = parse_list(item_antecedents)

        matches = DATASETS.loc[DATASETS["antecedents"] == item_antecedents_str]
        
        if not matches.empty:
            return matches.to_dict('records')
        else:
            return None

    # Show recommendations based on selected book
    result = return_item_judul(Item_set)

    if result:
        st.markdown("Rekomendasi Buku Perpustakaan: ")
        st.success(f"Jika meminjam **{Item}**, maka dapat meminjam : ")
        for match in result:
            st.write(f"- {match['consequents']}")
    else:
        st.error(f"Tidak ada rekomendasi untuk **{Item}**")

# Option 3: Rekomendasi Berdasarkan Fakultas
if selected == "Rekomendasi Berdasarkan Fakultas":
    st.write("#### Rekomendasi Berdasarkan Fakultas")

    rec_gabungan = pd.read_excel('HasilMerge.xlsx')

    def User_input_features():
        Fakultas = st.selectbox("Fakultas", ["FIP", "FBS", "FMIPA", "FIS", "FT", "FIK", "FPP", "FPK", "OTHERS"])
        return Fakultas 

    Fakultas = User_input_features()

    class FilterData:
        def __init__(self, data):
            self.data = data
        
        def filter_rec(self, column, value):
            filtered_data = self.data[self.data[column] == value]
            return filtered_data
        
        def plot_top_ten(self, filtered_data, top_ten=10):
            fig, ax = plt.subplots(figsize=(7, 3))
            filtered_data['consequents'].value_counts().head(top_ten).sort_values(ascending=True).plot(kind='barh')
            ax.set_xlabel('Jumlah')
            ax.set_ylabel(f"Fakultas: {Fakultas}")
            ax.set_title('10 Buku paling direkomendasikan Menurut Fakultas')
            plt.tight_layout()
            return fig

    filter_ins = FilterData(rec_gabungan)
    filtered_data = filter_ins.filter_rec('Fakultas', Fakultas)

    if not filtered_data.empty:
        fig = filter_ins.plot_top_ten(filtered_data, top_ten=10)
        st.pyplot(fig)
        st.success(f'**Rekomendasi** untuk Mahasiswa UNP Fakultas **{Fakultas}** dapat meminjam buku ini di Perpustakaan UNP')
    else:
        st.error("Tidak Ada Data yang Dipilih.")
