import base64

import dit_dc_lib as dit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import streamlit.components.v1 as components

st.markdown(
    "<h1 style='text-align: center; color:#841230;'>Groupe 4 - DATA SCRAPER APP</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h2 style='text-align: center; color:#841230;'>Gestion dans un mode DevOps</h2>",
    unsafe_allow_html=True,
)

st.markdown(
    """
Cette application permet de collecter les données du site expat-dakar sur plusieurs pages !
* **Librairies python:** base64, pandas, streamlit, requests, bs4
* **Source de données :** [Expat-Dakar](https://www.expat-dakar.com/).
"""
)

page_options = (
    "Télécharger données collectées",
    "Collecter données",
    "Remplir formulaire",
    "Voir tableaux de bord",
)

st.sidebar.title("Action souhaitée")
page = st.sidebar.selectbox("", page_options, key="action")

if page == page_options[1]:
    num_pages_to_scrap = st.sidebar.selectbox(
        "Sélectionnez le nombre de pages sur lesquelles collecter les données",
        tuple(np.arange(1, 201)),
        key="num_pages",
    )


# Fonction Background
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
        f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


add_bg_from_local("img_file_g4.jpg")

# Stocker les données dans des variables
Vehicles = pd.read_csv("Web_Scraper_voiture_G4.csv", sep=";")
Motocycles = pd.read_csv("web_scraper_url2_G4.csv", sep=";")
equipements = pd.read_csv("Equipement_piece_1.csv", sep=";")


# caching des données
@st.cache_data
def convert_df(df):
    return df.to_csv().encode("utf-8")


def load(dataframe, title, key, key1):
    st.markdown(
        """
    <style>
    div.stButton {text-align:center}
    </style>""",
        unsafe_allow_html=True,
    )

    if st.button(title, key1):
        # st.header(title)

        st.subheader("Display data dimension")
        st.write(
            "Data dimension: "
            + str(dataframe.shape[0])
            + " rows and "
            + str(dataframe.shape[1])
            + " columns."
        )
        st.dataframe(dataframe)

        csv = convert_df(dataframe)

        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name=f"{title.lower().replace(' ', '_')}_data.csv",
            mime="text/csv",
            key=key,
        )


def scrap_and_show_data(title, key):
    st.markdown(
        """
    <style>
    div.stButton {text-align:center}
    </style>""",
        unsafe_allow_html=True,
    )
    st.title(title)
    dataframe = pd.DataFrame()
    with st.spinner(text="Collecte en cours ..."):
        dataframe = dit.scrap_data(title, num_pages_to_scrap)
    st.success("Collecte réussie !")

    st.subheader("Display data dimension")
    st.write(
        "Data dimension: "
        + str(dataframe.shape[0])
        + " rows and "
        + str(dataframe.shape[1])
        + " columns."
    )
    st.dataframe(dataframe)

    csv = convert_df(dataframe)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name=f"{title.lower().replace(' ', '_')}_data.csv",
        mime="text/csv",
        key=key,
    )


def treat_price_column(price_txt):
    if price_txt is None:
        return 0
    if isinstance(price_txt, float):
        return int(price_txt) if not np.isnan(price_txt) else 0
    if isinstance(price_txt, int):
        return price_txt
    price = (
        price_txt.lower()
        .replace("cfa", "")
        .replace("f", "")
        .replace(" ", "")
        .replace("\u202f", "")
    )
    return int(price)


def load_charts():

    st.title("Voitures")
    plt.style.use("ggplot")
    cleaned_cars = Vehicles[Vehicles["annee"].notnull() & Vehicles["prix"].notnull()]
    cleaned_cars["prix_nbr"] = cleaned_cars["prix"].apply(treat_price_column)
    grouped_auto_par_annee = cleaned_cars.groupby(["annee", "etat"])
    grouped_marque_auto_par_annee = cleaned_cars.groupby(["annee", "marque"])
    grouped_boite_auto_par_annee = cleaned_cars.groupby(["annee", "boite_vitesse"])
    nbr_auto_par_annee_par_etat = grouped_auto_par_annee.count()
    nbr_auto_par_annee_par_boite = grouped_boite_auto_par_annee.count()
    mean_prix_auto_par_annee_par_marque = grouped_marque_auto_par_annee[
        "prix_nbr"
    ].mean()
    # st.write(nbr_auto_par_annee_par_boite.reset_index())
    fig, ax = plt.subplots(4, 1, constrained_layout=True, figsize=(20, 35))

    ax[0].set_title("Nombre de voitures par année selon l'état")
    sns.lineplot(
        nbr_auto_par_annee_par_etat, x="annee", y="marque", hue="etat", ax=ax[0]
    )
    ax[0].set(xlabel="Année", ylabel="Nombre de voitures")

    ax[1].set_title("Nombre de voitures par année par type de boîte de vitesse")
    sns.lineplot(
        nbr_auto_par_annee_par_boite.reset_index(),
        x="annee",
        y="etat",
        hue="boite_vitesse",
        ax=ax[1],
    )
    ax[1].set(xlabel="Année", ylabel="Nombre de voitures")

    ax[2].set_title("Prix moyen des voitures par année par marque")
    sns.lineplot(
        mean_prix_auto_par_annee_par_marque.reset_index(),
        x="annee",
        y="prix_nbr",
        hue="marque",
        ax=ax[2],
    )
    ax[2].set(xlabel="Année", ylabel="Prix moyen")

    ax[3].set_title("Prix moyen des voitures par année par marque - vue 2D")
    sns.histplot(
        mean_prix_auto_par_annee_par_marque.reset_index(),
        x="annee",
        y="marque",
        cbar=True,
        ax=ax[3],
    )
    ax[3].set(xlabel="Année", ylabel="Marque")

    st.pyplot(fig)

    st.title("Motos")
    # plt.figure(figsize=(20,60))
    # plt.style.use('Solarize_Light2')

    cleaned_motos = Motocycles[
        Motocycles["annee"].notnull() & Motocycles["prix"].notnull()
    ]
    cleaned_motos["prix_nbr"] = cleaned_motos["prix"].apply(treat_price_column)
    grouped_moto_par_annee = cleaned_motos.groupby(["annee", "etat"])
    grouped_marque_par_annee = cleaned_motos.groupby(["annee", "marque"])
    nbr_moto_par_annee_par_etat = grouped_moto_par_annee.count()
    mean_prix_moto_par_annee_par_marque = grouped_marque_par_annee["prix_nbr"].mean()
    # st.write(mean_prix_moto_par_annee_par_marque)
    fig, ax = plt.subplots(3, 1, constrained_layout=True, figsize=(20, 30))

    # ax[0,0].tick_params(axis='x', labelrotation=90)
    ax[0].set_title("Nombre de motos par année selon l'état")
    sns.lineplot(
        nbr_moto_par_annee_par_etat, x="annee", y="marque", hue="etat", ax=ax[0]
    )
    ax[0].set(xlabel="Année", ylabel="Nombre de motos")

    ax[1].set_title("Prix moyen des motos par année par marque")
    sns.lineplot(
        mean_prix_moto_par_annee_par_marque.reset_index(),
        x="annee",
        y="prix_nbr",
        hue="marque",
        ax=ax[1],
    )
    ax[1].set(xlabel="Année", ylabel="Prix moyen")

    ax[2].set_title("Prix moyen des motos par année par marque - vue 2D")
    sns.histplot(
        mean_prix_moto_par_annee_par_marque.reset_index(),
        x="annee",
        y="marque",
        cbar=True,
        ax=ax[2],
    )
    ax[2].set(xlabel="Année", ylabel="Marque")

    st.pyplot(fig)

    st.title("Equipements")

    equipements["adresse"].fillna("", inplace=True)
    equipements["Etat"].fillna("", inplace=True)
    # plt.figure(figsize=(20,60))
    # plt.style.use('Solarize_Light2')
    plt.style.use("ggplot")
    fig, ax = plt.subplots(2, 2, constrained_layout=True, figsize=(15, 15))

    ax[0, 0].tick_params(axis="x", labelrotation=90)
    ax[0, 0].set_title("Nombre d'équipements à vendre par adresse")
    sns.histplot(equipements, x="adresse", ax=ax[0, 0])
    ax[0, 0].set(xlabel="Adresse", ylabel="Nombre d'équipements")

    ax[0, 1].set_title("Etat")
    nbr_par_etat = equipements["Etat"].value_counts()
    ax[0, 1].pie(nbr_par_etat, labels=nbr_par_etat.index)

    equipements["prix_nbr"] = equipements["prix"].apply(treat_price_column)
    grouped_eq = (
        equipements[equipements["prix"].notna()].groupby("Etat")["prix_nbr"].mean()
    )
    # st.write(grouped_eq)
    ax[1, 0].tick_params(axis="x", labelrotation=90)
    ax[1, 0].set_title("Prix moyen en fonction de l'état")
    ax[1, 0].bar(grouped_eq.index, grouped_eq.values)
    ax[1, 0].set(xlabel="Etat", ylabel="Prix moyen")
    # plt.tight_layout()
    st.pyplot(fig)

    # st.bar_chart(equipements.value_counts(), x="Etat")


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


local_css("style.css")


if page == page_options[0]:
    # Charger les données
    load(Vehicles, "Voitures", "1", "101")
    load(Motocycles, "Motos et scooters", "2", "102")
    load(equipements, "Equipements", "3", "103")
elif page == page_options[1]:
    scrap_and_show_data("Voitures", "1")
    scrap_and_show_data("Motos", "2")
    scrap_and_show_data("Equipements", "3")
elif page == page_options[2]:
    components.html(
        """
    <iframe src="https://ee.kobotoolbox.org/i/kUWU2Twx" width="900" height="1200"></iframe>
    """,
        width=900,
        height=1200,
        scrolling=False,
    )
elif page == page_options[3]:
    load_charts()
else:
    pass
