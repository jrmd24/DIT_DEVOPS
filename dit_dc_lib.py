import pandas as pd
from bs4 import BeautifulSoup as bs
from requests import get


def scrap_data(data_type, num_pages) -> pd.DataFrame:
    if data_type.lower() == "equipements":
        return scrap_equipments(num_pages)
    elif data_type.lower() == "motos":
        return scrap_motos(num_pages)
    elif data_type.lower() == "voitures":
        return scrap_voitures(num_pages)
    else:
        return None


def scrap_equipments(num_pages) -> pd.DataFrame:

    df_glob = pd.DataFrame()

    for p in range(1, num_pages + 1):
        url_liste = f"https://www.expat-dakar.com/equipements-pieces?page={p}"

        res = None
        try:
            res = get(url_liste)
        except:
            continue

        soup = bs(res.text, "html.parser")  # stocker le code html dans un objet bs
        a_elems = soup.find_all("a", class_="listing-card__inner")
        links = [a_elem["href"] for a_elem in a_elems]

        info_container_type = ["class", "class", "class_tag", "class", "src"]
        info_names = ["Article", "Etat", "Adresse", "Prix", "image_lien"]
        info_tags = ["h1", "dd", "div_span", "span", "img"]
        info_class = [
            "listing-item__header",
            "listing-item__properties__description",
            "listing-item__address",
            "listing-card__price__value",
            "vh-img",
        ]

        data = []

        for link in links:

            try:
                res_article = get(link)
                soup_article = bs(
                    res_article.text, "html.parser"
                )  # stocker le code html dans un objet bs

                obj = {}
                for container_type, name, tag, elem_class in zip(
                    info_container_type, info_names, info_tags, info_class
                ):
                    try:
                        current_info = None
                        current_info_text = ""
                        if "_" in container_type:
                            current_info = soup_article.find(
                                tag.split("_")[0], class_=elem_class
                            ).find_all(tag.split("_")[1])
                            current_info_text = ",".join(
                                [x.text.strip() for x in current_info]
                            )
                        elif "class" not in container_type:
                            current_info = soup_article.find(tag, class_=elem_class)[
                                container_type
                            ]
                            current_info_text = current_info
                        else:
                            current_info = soup_article.find(tag, class_=elem_class)
                            current_info_text = current_info.text.strip()
                    except:
                        current_info_text = ""

                    obj[name] = current_info_text
                obj["details"] = link
                data.append(obj)
            except:
                pass
        df = pd.DataFrame(data)
        df_glob = pd.concat([df_glob, df], axis=0).reset_index(drop=True)
    return df_glob


def scrap_motos(num_pages) -> pd.DataFrame:
    # Scraper sur plusieurs pages
    df = pd.DataFrame()

    for p in range(1, num_pages + 1):
        url = f"https://www.expat-dakar.com/motos-scooters?page={p}"
        resp = None
        try:
            resp = get(url)
        except:
            continue

        soup = bs(resp.text, "html.parser")
        containers = soup.find_all("div", class_="listings-cards__list-item")
        data = []
        for container in containers:
            try:
                inf = container.find(
                    "div", class_="listing-card__header__tags"
                ).find_all("span")
                etat_moto = inf[0].text
                marque = inf[1].text
                annee = inf[2].text
                prix = (
                    container.find("span", class_="listing-card__price__value 1")
                    .text.strip()
                    .replace("\u202f", "")
                    .replace(" F Cfa", "")
                )
                adresse = (
                    container.find("div", class_="listing-card__header__location")
                    .text.replace("\n", "")
                    .split(",")
                )
                quartier = adresse[0]
                region = adresse[1]
                lien_image = container.find(
                    "img", class_="listing-card__image__resource vh-img"
                )["src"]

                obj = {
                    "etat": etat_moto,
                    "marque": marque,
                    "annee": annee,
                    "prix": prix,
                    "quartier": quartier,
                    "region": region,
                    "lien_image": lien_image,
                }
                data.append(obj)
            except:
                pass

        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)

    return df


def scrap_voitures(num_pages) -> pd.DataFrame:
    df = pd.DataFrame()
    for p in range(1, num_pages + 1):

        url = f"https://www.expat-dakar.com/voitures?page={p}"

        resp = None
        try:
            resp = get(url)
        except:
            continue

        soup = bs(resp.text, "html.parser")
        voitures = soup.find_all("div", class_="listings-cards__list-item")
        data = []
        for voiture in voitures:
            try:
                Etat = voiture.find(
                    "span", class_="listing-card__header__tags__item--condition"
                ).text
                Marque = voiture.find(
                    "span", class_="listing-card__header__tags__item--make"
                ).text
                Annee = voiture.find(
                    "span", class_="listing-card__header__tags__item--buildyear"
                ).text
                Boite_vitesse = voiture.find(
                    "span", class_="listing-card__header__tags__item--transmission"
                ).text
                Adresse = (
                    voiture.find("div", class_="listing-card__header__location")
                    .text.strip()
                    .replace("\n", "")
                )
                Prix = voiture.find(
                    "span", class_="listing-card__price__value"
                ).text.strip()
                Image_lien = voiture.find(
                    "img", "listing-card__image__resource vh-img"
                )["src"]

                obj = {
                    "Etat": Etat,
                    "Marque": Marque,
                    "Annee": Annee,
                    "Boite_vitesse": Boite_vitesse,
                    "Adresse": Adresse,
                    "Prix": Prix,
                    "Image_lien": Image_lien,
                }
                data.append(obj)
            except:
                pass

        DF = pd.DataFrame(data)
        df = pd.concat([df, DF], axis=0).reset_index(drop=True)
    return df
