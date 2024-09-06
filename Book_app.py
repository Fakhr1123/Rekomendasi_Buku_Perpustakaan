import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from mlxtend.frequent_patterns import association_rules, fpgrowth
from datetime import datetime
from PIL import Image
from mlxtend.preprocessing import TransactionEncoder
import warnings
warnings.filterwarnings("ignore")


##Judul
st.image("logo_unp.png")
st.write(""" 
# Web App Recommendation
         
#### :books: Website Aplikasi Rekomendasi Buku Perpustakaan UNP :books:
         
*** 
""")

#Input Data
dataset= pd.read_excel('DATA PENELITIAN4.xlsx')
dataset= dataset[['Transaksi', 'Judul', 'Tahun Masuk', 'Fakultas', 'Hari']]
dataset.columns= ['Transaksi', 'Judul', 'Tahun_Masuk', 'Fakultas', 'Hari']
dataset['Tahun_Masuk']= dataset['Tahun_Masuk'].astype(str)

#Analsis Deskriptif Data Data 
##1
st.subheader('Explorasi Data')
fig, ax = plt.subplots(figsize= (5, 3))
dataset['Tahun_Masuk'].value_counts().plot(kind='bar', color='blue')
ax.set_xlabel('Tahun_Masuk')
ax.set_ylabel('Jumlah')
ax.set_title('Jumlah Peminjaman Buku menurut Tahun Masuk')
st.pyplot(fig)

##2
fig1, ax1 = plt.subplots(figsize=(5, 3))
dataset['Fakultas'].value_counts().plot(kind= 'bar', color= 'red')
ax1.set_xlabel('Fakultas')
ax1.set_ylabel('Jumlah')
ax1.set_title('Jumlah Peminjaman menurut Fakultas')
st.pyplot(fig1)

##definisikan data

def get_data(Tahun_masuk= '', Fakultas= '', Hari=''):
    dataset= dataset.copy()
    filter_data= dataset.loc[
        (dataset["Tahun_masuk"].str.contains(Tahun_masuk))&
        (dataset['Fakultas'].str.contains(Fakultas))&
        (dataset["Hari"].str.contains(Hari))
    ]
    return filter_data if filter_data.shape[0] else "tidak ada hasil"

##transformasi data
Judul= dataset[['Transaksi','Judul']] 
transactions = Judul.groupby('Transaksi')['Judul'].apply(list).tolist()
te = TransactionEncoder()
te_array = te.fit(transactions).transform(transactions)
te_columns = te.columns_
dataset_encoded = pd.DataFrame(te_array, columns=te_columns)


##menjalankan algoritma FP-Growth
support_threshold= 0.0009
freq_items= fpgrowth(dataset_encoded, min_support=support_threshold, use_colnames= True)

##Association Rules
metric= "lift"
min_threshold= 1
rule= association_rules(freq_items, metric=metric, min_threshold=min_threshold, )[["antecedents", "consequents", "support", "confidence", "lift"]]
rule.sort_values('confidence', ascending= False, inplace= True)

##Association merge data perpustakaan
RULE= pd.read_excel('Hasilmerge3.xlsx')

##menampilkan 10 item paling sering dipinjam
rekomendasi= pd.read_excel('Hasilmerge2.xlsx')
st.subheader("Top 3 Rekomendasi Buku Perpustakaan UNP")
rekomendasi[0:3]

####APP
def parse_list(x):
    if isinstance(x, frozenset):
        return ", ".join(map(str, x))
    else:
        return str(x)
    
def return_item_judul(item_antecedents):
    DATASETS= RULE[["antecedents", "consequents"]].copy()
    DATASETS["antecedents"]= DATASETS["antecedents"].apply(parse_list)
    DATASETS["consequents"]= DATASETS["consequents"].apply(parse_list)

    item_antecedents_str = parse_list(item_antecedents)

    matches = DATASETS.loc[DATASETS["antecedents"] == item_antecedents_str]
    
    if not matches.empty:
        return matches.to_dict('records')
    else:
        return None
    
##Membuat fitur input
##membuat selectbox
isi= pd.read_excel('JUDUL BUKU.xlsx')
isi_item= isi['Judul'].values.tolist()
st.write("#### Cari Rekomendasi")
Item= st.selectbox("Judul", isi_item)
Item_set = frozenset([Item])

#Print Rekomendasi
result = return_item_judul(Item_set)

if result:
    st.markdown("Rekomendasi Buku Perpustakaan: ")
    result = return_item_judul(Item)
    
    st.success(f"Jika meminjam **{Item}**, maka dapat meminjam : ")
    for match in result:
        st.write(f"- {match['consequents']}")
else:
    st.error(f"Tidak ada rekomendasi untuk **{Item}**")

###Membuat select box ke-2
st.write("#### Rekomendasi Berdasarkan Fakultas")
rec_gabungan= pd.read_excel('HasilMerge.xlsx')

def User_input_features():
    Fakultas= st.selectbox("Fakultas", ["FIP", "FBS", "FMIPA", "FIS", "FT", "FIK", "FPP", "FPS", "OTHERS"])
    return Fakultas 

Fakultas= User_input_features()

class FilterData:
    def __init__(self, data):
        self.data= data
    
    def filter_rec(self, column, value):
        filtered_data= self.data[self.data[column]== value]
        return filtered_data
    
    def plot_top_ten(self, filtered_data, top_ten=10):
        fig, ax = plt.subplots(figsize= (7, 3))
        filtered_data['consequents'].value_counts().head(top_ten).sort_values(ascending= True).plot(kind= 'barh')
        ax.set_xlabel('Jumlah')
        ax.set_ylabel(f"Fakultas: {Fakultas}")
        ax.set_title('10 Buku paling direkomendasikan Menurut Fakultas')
        plt.tight_layout()
        return fig
        

filter_ins= FilterData(rec_gabungan)

filtered_data = filter_ins.filter_rec('Fakultas', Fakultas)

if not filtered_data.empty:
    fig = filter_ins.plot_top_ten(filtered_data, top_ten=10)
    st.pyplot(fig)
    st.success(f'**Rekomendasi** untuk Mahasiswa UNP Fakultas **{Fakultas}** dapat meminjam buku ini di Perpustakaan UNP')
else:
    st.error("Tidak Ada Data yang Dipilih.")



        

