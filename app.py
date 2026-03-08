import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os

# Konfigurasi halaman
st.set_page_config(page_title="Network Saham KSEI", layout="wide")
st.title("🕸️ Peta Relasi Kepemilikan Saham KSEI")
st.markdown("Pilih entitas di sebelah kiri untuk melihat jaringannya.")

# Membaca Data
@st.cache_data
def load_data():
    df = pd.read_csv('data_ksei_terstruktur.csv')
    return df

df = load_data()

# Sidebar untuk Pencarian
st.sidebar.header("🔍 Pencarian Entitas")
search_type = st.sidebar.radio("Cari Berdasarkan:", ("Emiten (ISSUER NAME)", "Investor (INVESTOR NAME)"))

if search_type == "Emiten (ISSUER NAME)":
    # Ambil list unik emiten
    options = df['ISSUER_NAME'].dropna().unique().tolist()
    options.sort()
    selected_node = st.sidebar.selectbox("Pilih Nama Emiten:", options)
    
    # Filter data hanya yang berkaitan dengan emiten terpilih
    filtered_df = df[df['ISSUER_NAME'] == selected_node]
else:
    # Ambil list unik investor
    options = df['INVESTOR_NAME'].dropna().unique().tolist()
    options.sort()
    selected_node = st.sidebar.selectbox("Pilih Nama Investor:", options)
    
    # Filter data hanya yang berkaitan dengan investor terpilih
    filtered_df = df[df['INVESTOR_NAME'] == selected_node]

# Tombol untuk Generate
if st.sidebar.button("Visualisasikan Relasi"):
    st.subheader(f"Peta Relasi untuk: **{selected_node}**")
    
    # Inisialisasi Graph
    G = nx.Graph()
    
    # Memasukkan titik (nodes) dan garis (edges)
    for index, row in filtered_df.iterrows():
        emiten = str(row['ISSUER_NAME'])
        investor = str(row['INVESTOR_NAME'])
        persentase = str(row['PERCENTAGE'])
        
        # Tambahkan node Emiten (Bentuk Kotak/Warna Biru)
        G.add_node(emiten, group="emiten", title="Emiten", color="#3498db", shape="box")
        # Tambahkan node Investor (Bentuk Lingkaran/Warna Merah)
        G.add_node(investor, group="investor", title="Investor", color="#e74c3c", shape="dot")
        
        # Tambahkan garis relasi
        G.add_edge(investor, emiten, title=f"Kepemilikan: {persentase}%")
    
    # Konversi ke Pyvis untuk interaktivitas di web
    net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
    net.from_nx(G)
    
    # Menambahkan opsi fisika agar grafiknya terlihat natural dan elastis
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=150, spring_strength=0.05, damping=0.09)
    
    # Simpan ke HTML sementara
    path = '/tmp' if os.name != 'nt' else '.'
    html_file = f"{path}/network.html"
    net.save_graph(html_file)
    
    # Baca dan tampilkan HTML di dalam Streamlit
    HtmlFile = open(html_file, 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=650)
    
    # Menampilkan tabel data mentahnya juga di bawah
    st.markdown("### 📊 Detail Data")
    st.dataframe(filtered_df[['SHARE_CODE', 'ISSUER_NAME', 'INVESTOR_NAME', 'INVESTOR_TYPE', 'PERCENTAGE']])
