import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# ------------------------------------------------------
# Función scraping
# ------------------------------------------------------
def scrape_data(url):
    BASE = "https://www.elespanol.com"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = []

    for item in soup.select("div.data-news"):

        name_tag = item.select_one(".data-author .data-name")
        name = name_tag.get_text(strip=True) if name_tag else None

        office_tag = item.select_one(".data-office")
        office = office_tag.get_text(strip=True) if office_tag else None

        position_tag = item.select_one(".data-position")
        position = position_tag.get_text(strip=True) if position_tag else None

        link_tag = item.select_one(".data-author a")
        href = link_tag["href"] if link_tag else None
        if href and not href.startswith("http"):
            href = BASE + href

        # Segunda página: LinkedIn
        linkedin = None
        if href:
            r2 = requests.get(href, headers=headers)
            soup2 = BeautifulSoup(r2.text, "html.parser")
            linkedin_item = soup2.select_one("li.list-network__item--linkedin a")
            if linkedin_item:
                linkedin = linkedin_item.get("href")

        rows.append({
            "Nombre": name,
            "Empresa": office,
            "Cargo": position,
            "Perfil": href,
            "LinkedIn": linkedin
        })

    return pd.DataFrame(rows)

# ------------------------------------------------------
# Interfaz Streamlit
# ------------------------------------------------------
st.title("Scraper de Directivas (Filtro por Empresa)")

default_url = "https://www.elespanol.com/mujer/lastop100/votaciones/36/directivas/"
user_url = st.text_input("Introduce la URL:", value=default_url)

if st.button("Obtener datos"):
    with st.spinner("Extrayendo información..."):
        df = scrape_data(user_url)

        st.subheader("Filtro por empresa")

        empresas = ["Todas"] + sorted(df["Empresa"].dropna().unique().tolist())
        empresa_filter = st.selectbox("Selecciona la empresa:", empresas)

        filtered_df = df.copy()
        if empresa_filter != "Todas":
            filtered_df = filtered_df[filtered_df["Empresa"] == empresa_filter]

        # Enlaces clicables
        filtered_df["LinkedIn"] = filtered_df["LinkedIn"].apply(
            lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else ""
        )
        filtered_df["Perfil"] = filtered_df["Perfil"].apply(
            lambda x: f'<a href="{x}" target="_blank">{x}</a>' if x else ""
        )

        st.subheader("Resultados")
        st.write(filtered_df.to_html(escape=False), unsafe_allow_html=True)

        st.success("Datos cargados correctamente 👍")
