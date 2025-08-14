"""
This module implements the main functionality of octoanalytics.

Author: Jean Bertin
"""

__author__ = "Jean Bertin"
__email__ = "jean.bertin@octopusenergy.fr"
__status__ = "planning"

import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
import holidays
import matplotlib.pyplot as plt
import holidays
import requests
from tqdm import tqdm
from sklearn.impute import SimpleImputer
import plotly.graph_objects as go
import tentaclio as tio
import os
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from typing import Optional
from databricks import sql
from yaspin import yaspin
import pandas as pd
from databricks import sql
import requests
import urllib3
import pandas as pd
from tqdm import tqdm


def get_temp_smoothed_fr(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Récupère les températures moyennes horaires lissées sur plusieurs grandes villes françaises.

    Paramètres :
    -----------
    start_date : str
        Date de début (format 'YYYY-MM-DD').
    end_date : str
        Date de fin (format 'YYYY-MM-DD').

    Retour :
    -------
    pd.DataFrame
        DataFrame avec les colonnes ['timestamp', 'temperature'] représentant la température moyenne lissée.
    """

    # 1. Définition des grandes villes françaises pour lisser les données à l'échelle nationale
    cities = {
        "Paris": (48.85, 2.35),
        "Lyon": (45.76, 4.84),
        "Marseille": (43.30, 5.37),
        "Lille": (50.63, 3.07),
        "Toulouse": (43.60, 1.44),
        "Strasbourg": (48.58, 7.75),
        "Nantes": (47.22, -1.55),
        "Bordeaux": (44.84, -0.58)
    }

    city_dfs = []  # 2. Liste pour stocker les DataFrames de chaque ville

    # 3. Boucle sur chaque ville pour récupérer les données météo horaires via l'API Open-Meteo
    for city, (lat, lon) in tqdm(cities.items(), desc="Fetching city data"):
        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "temperature_2m",
            "timezone": "Europe/Paris"
        }
        try:
            # 4. Requête GET à l'API météo
            response = requests.get(url, params=params)
            response.raise_for_status()  # Vérifie que la requête est OK
            data = response.json()

            # 5. Construction du DataFrame pour la ville courante
            df = pd.DataFrame({
                'timestamp': data['hourly']['time'],
                city: data['hourly']['temperature_2m']
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'])  # Conversion en datetime
            df.set_index('timestamp', inplace=True)  # Mise en index sur la date/heure

            city_dfs.append(df)  # 6. Ajout du DataFrame ville à la liste

        except Exception as e:
            print(f"Error with {city}: {e}")  # 7. Gestion simple des erreurs

    # 8. Fusion de tous les DataFrames de villes selon l'index timestamp (concaténation horizontale)
    df_all = pd.concat(city_dfs, axis=1)

    # 9. Calcul de la moyenne horaire sur toutes les villes (lissage national)
    df_all['temperature'] = df_all.mean(axis=1)

    # 10. Retourne uniquement la colonne timestamp et la température moyenne lissée (réinitialisation de l'index)
    return df_all[['temperature']].reset_index()

def eval_forecast(df, temp_df, cal_year=None, datetime_col='timestamp', target_col='MW', plot_chart=False, save_path=None):
    """
    Calcule un forecast (et éventuellement affiche un graphique) pour une année donnée.

    Paramètres :
    -----------
    df : pd.DataFrame
        Données historiques contenant au moins les colonnes datetime_col et target_col.
    temp_df : pd.DataFrame
        Données de température avec colonnes ['timestamp', 'temperature'].
    cal_year : int ou None, optionnel (par défaut None)
        Année civile pour laquelle générer la prévision. Obligatoire si plot_chart=True.
    datetime_col : str, optionnel (par défaut 'timestamp')
        Nom de la colonne contenant les timestamps dans df.
    target_col : str, optionnel (par défaut 'MW')
        Nom de la colonne cible à prédire dans df.
    plot_chart : bool, optionnel (par défaut False)
        Indique si un graphique interactif Plotly doit être généré.
    save_path : str ou None, optionnel
        Chemin pour sauvegarder le graphique HTML si plot_chart est True.

    Retour :
    --------
    pd.DataFrame
        DataFrame contenant les colonnes datetime_col, target_col et 'forecast' (prévision).
    """

    # 1. Vérifie la cohérence des paramètres
    #    - Nécessité de fournir cal_year si on souhaite afficher un graphique
    if cal_year is None and plot_chart:
        raise ValueError("Vous devez fournir `cal_year` si vous souhaitez générer un graphique.")

    # 2. Fixe la graine aléatoire pour assurer la reproductibilité des résultats du modèle
    np.random.seed(42)

    # 3. Copie des données d'origine pour éviter modifications involontaires
    df = df.copy()

    # 4. Uniformise la colonne datetime
    #    - Conversion en datetime avec fuseau UTC pour standardiser
    #    - Suppression du fuseau (naïve) pour éviter conflits lors des jointures/fusions
    df[datetime_col] = pd.to_datetime(df[datetime_col], utc=True).dt.tz_localize(None)

    # 5. Suppression des lignes où datetime ou target est manquant
    df = df.dropna(subset=[datetime_col, target_col])

    # 6. Tri chronologique des données et ré-indexation
    df = df.sort_values(datetime_col).reset_index(drop=True)

    # 7. Vérification que les données couvrent toute l’année cal_year
    expected_start = pd.Timestamp(f"{cal_year}-01-01 00:00:00")
    expected_end = pd.Timestamp(f"{cal_year}-12-31 23:59:59")
    if not ((df[datetime_col] <= expected_start).any() and (df[datetime_col] >= expected_end).any()):
        raise ValueError(
            f"Les données ne couvrent pas toute l’année civile {cal_year}.\n"
            f"Période attendue : {expected_start.date()} à {expected_end.date()}\n"
            f"Données disponibles de {df[datetime_col].min().date()} à {df[datetime_col].max().date()}"
        )

    # 8. Définition explicite de la période de test correspondant à l’année de forecast
    test_start = expected_start
    test_end = expected_end

    # 9. Préparation et nettoyage des données de température
    temp_df = temp_df.copy()
    # Conversion en datetime avec fuseau UTC, puis suppression du fuseau pour homogénéité
    temp_df[datetime_col] = pd.to_datetime(temp_df['timestamp'], utc=True).dt.tz_localize(None)
    #temp_df = temp_df.drop(columns=['timestamp'])

    # 10. Fusion des données météo avec les données principales sur datetime_col
    df = pd.merge(df, temp_df, on=datetime_col, how='left')

    # 11. Remplissage des valeurs manquantes de température par propagation avant puis arrière
    df['temperature'] = df['temperature'].ffill().bfill()

    # 12. Ajout des features temporelles et météo utiles à la modélisation
    def add_features(df):
        # Extraction des composantes temporelles classiques
        df['hour'] = df[datetime_col].dt.hour
        df['dayofweek'] = df[datetime_col].dt.dayofweek
        df['month'] = df[datetime_col].dt.month

        # Encodage cyclique pour les composantes périodiques (heure, jour de la semaine, mois)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
        df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

        # Autres variables temporelles pertinentes
        df['minute'] = df[datetime_col].dt.minute
        df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
        df['dayofyear'] = df[datetime_col].dt.dayofyear
        df['week'] = df[datetime_col].dt.isocalendar().week.astype(int)
        df['quarter'] = df[datetime_col].dt.quarter
        df['is_month_start'] = df[datetime_col].dt.is_month_start.astype(int)
        df['is_month_end'] = df[datetime_col].dt.is_month_end.astype(int)

        # Jours fériés français
        fr_holidays = holidays.country_holidays('FR')
        df['is_holiday'] = df[datetime_col].dt.date.astype(str).isin(fr_holidays).astype(int)

        # Indicateurs chauffage/climatisation basés sur la température
        df['heating_on'] = (df['temperature'] < 15).astype(int)
        df['cooling_on'] = (df['temperature'] > 25).astype(int)

        # Variables supplémentaires liées à la température (transformation)
        df['temp_below_10'] = np.maximum(0, 10 - df['temperature'])
        df['temp_above_30'] = np.maximum(0, df['temperature'] - 30)
        df['temp_diff_15'] = df['temperature'] - 15

        return df

    df = add_features(df)

    # 13. Suppression des lignes avec des valeurs manquantes éventuelles après enrichissement
    df = df.dropna().reset_index(drop=True)

    # 14. Séparation des données en ensembles d'entraînement et de test
    #     - Train = données hors de l’année cal_year
    #     - Test = données durant l’année cal_year
    train_df = df[(df[datetime_col] < test_start) | (df[datetime_col] > test_end)].copy()
    test_df = df[(df[datetime_col] >= test_start) & (df[datetime_col] <= test_end)].copy()

    # 15. Vérification de la taille suffisante des données d'entraînement
    if len(train_df) < 1000:
        raise ValueError("Pas assez de données pour entraîner le modèle.")

    # 16. Entraînement d’un modèle Random Forest sur les features dérivées
    features = [col for col in train_df.columns if col not in [datetime_col, target_col]]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(train_df[features], train_df[target_col])

    # 17. Prédiction sur la période test (année cal_year)
    test_df['forecast'] = model.predict(test_df[features])

    # 18. Affichage optionnel d’un graphique interactif avec Plotly
    if plot_chart:
        y_true = test_df[target_col].values
        y_pred = test_df['forecast'].values
        mask = y_true != 0  # Exclusion des zéros pour le calcul du MAPE
        mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=test_df[datetime_col], y=test_df[target_col],
            mode='lines', name='Valeurs réelles', line=dict(color='blue')))
        fig.add_trace(go.Scatter(
            x=test_df[datetime_col], y=test_df['forecast'],
            mode='lines', name='Prévision', line=dict(color='red', dash='dash')))

        fig.update_layout(
            title=f'Prévision vs Réel — MAPE: {mape:.2f}%',
            xaxis_title='Date',
            yaxis_title=target_col,
            hovermode='x unified',
            template='plotly_white',
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            legend=dict(x=0.01, y=0.99, font=dict(color='white')),
            xaxis=dict(color='white', gridcolor='gray'),
            yaxis=dict(color='white', gridcolor='gray'),
            margin=dict(t=100)
        )

        if save_path:
            fig.write_html(save_path)
            print(f"Graph saved as interactive HTML at: {save_path}")
        else:
            fig.show()

    # 19. Retourne les résultats : timestamp, valeur réelle, et prévision
    return test_df[[datetime_col, target_col, 'forecast']]

def get_spot_price_fr(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Récupère les prix spot de l’électricité en France depuis Databricks (marché EPEX spot)
    via la connexion simplifiée avec tentaclio.

    Paramètres :
    -----------
    start_date : str
        Date de début au format 'YYYY-MM-DD'.
    end_date : str
        Date de fin au format 'YYYY-MM-DD'.

    Retour :
    -------
    pd.DataFrame
        DataFrame avec les colonnes ['delivery_from', 'price_eur_per_mwh'] contenant
        les dates/heures de livraison et les prix spot correspondants.
    """

    # 1. Initialisation du spinner de chargement avec yaspin (affiche un message pendant l'exécution)
    with yaspin(text="Chargement des prix spot depuis Databricks...") as spinner:

        # 2. Connexion à Databricks via tentaclio (gestionnaire de contexte simplifié)
        databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
        with tio.db(databricks) as client:

            # 3. Construction de la requête SQL pour récupérer les prix spot
            query = f"""
                SELECT delivery_from, price_eur_per_mwh
                FROM consumer.inter_energymarkets_epex_hh_spot_prices
                WHERE source_identifier = 'epex'
                  AND price_date >= '{start_date}'
                  AND price_date < '{end_date}'
                ORDER BY delivery_from
            """

            # 4. Récupération du curseur lié à la connexion Databricks
            cursor = client.cursor

            # 5. Exécution de la requête SQL sur le serveur Databricks
            cursor.execute(query)

            # 6. Récupération de toutes les lignes retournées par la requête
            rows = cursor.fetchall()

            # 7. Extraction des noms de colonnes depuis la description du curseur
            columns = [desc[0] for desc in cursor.description]

        # 8. Fin de la tâche : afficher une coche verte dans le spinner pour indiquer le succès
        spinner.ok("✅")

    # 9. Conversion des résultats en DataFrame pandas avec colonnes appropriées
    spot_df = pd.DataFrame(rows, columns=columns)

    # 10. Conversion de la colonne 'delivery_from' en datetime sans fuseau horaire (local naive)
    spot_df['delivery_from'] = pd.to_datetime(spot_df['delivery_from'], utc=True).dt.tz_localize(None)

    # 11. Conversion de la colonne 'price_eur_per_mwh' en float pour faciliter les calculs
    spot_df['price_eur_per_mwh'] = spot_df['price_eur_per_mwh'].astype(float)

    # 12. Retour du DataFrame final contenant les données de prix spot
    return spot_df

def get_forward_price_fr_annual(cal_year: int) -> pd.DataFrame:
    """
    Récupère les prix forward annuels d’électricité en France pour une année donnée depuis Databricks (EEX),
    en utilisant une connexion simplifiée via tentaclio.

    Paramètres :
    -----------
    cal_year : int
        Année civile de livraison souhaitée (ex. 2026).

    Retour :
    -------
    pd.DataFrame
        DataFrame contenant les colonnes ['trading_date', 'forward_price', 'cal_year'] avec les
        dates de trading, les prix forward correspondants et l’année civile associée.
    """

    # 1. Initialisation du spinner de chargement
    with yaspin(text="Chargement des prix forward depuis Databricks...") as spinner:

        # 2. Connexion via tentaclio
        databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
        with tio.db(databricks) as client:

            # 3. Construction de la requête SQL
            query = f"""
                SELECT setllement_price AS forward_price, trading_date
                FROM consumer.stg_eex_power_future_results_fr 
                WHERE long_name = 'EEX French Power Base Year Future' 
                  AND delivery_start >= '{cal_year}-01-01'
                  AND delivery_end <= '{cal_year}-12-31'
                ORDER BY trading_date
            """

            # 4. Exécution de la requête
            cursor = client.cursor
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

        # 5. Indication de succès via le spinner
        spinner.ok("✅")

    # 6. Transformation en DataFrame
    forward_df = pd.DataFrame(rows, columns=columns)

    # 7. Nettoyage et typage
    forward_df['trading_date'] = pd.to_datetime(forward_df['trading_date'], utc=True)
    forward_df['forward_price'] = forward_df['forward_price'].astype(float)
    forward_df['cal_year'] = cal_year

    # 8. Retour du résultat
    return forward_df


def get_forward_price_fr_months(cal_year_month: str) -> pd.DataFrame:
    """
    Récupère les prix forward mensuels d’électricité en France depuis Databricks (EEX),
    en utilisant une connexion standardisée via tentaclio.

    Paramètres :
    -----------
    cal_year_month : str
        Mois de livraison au format 'YYYY-MM' (exemple : '2025-03').

    Retour :
    -------
    pd.DataFrame
        DataFrame avec les colonnes ['trading_date', 'forward_price', 'cal_year'] 
        contenant les dates de trading, les prix forward mensuels et le mois associé.
    """

    # 1. Calcul des bornes temporelles du mois
    start_date = datetime.strptime(cal_year_month, "%Y-%m")
    end_date = start_date + relativedelta(months=1)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    # 2. Initialisation du spinner de chargement
    with yaspin(text="Chargement des prix forward mensuels depuis Databricks...") as spinner:

        # 3. Connexion via tentaclio
        databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
        with tio.db(databricks) as client:

            # 4. Requête SQL
            query = f"""
                SELECT setllement_price, trading_date, delivery_start, delivery_end
                FROM consumer.stg_eex_power_future_results_fr 
                WHERE long_name = 'EEX French Power Base Month Future' 
                  AND delivery_start >= '{start_str}'
                  AND delivery_start < '{end_str}'
                  AND setllement_price IS NOT NULL
                ORDER BY trading_date
            """
            forward_df = client.get_df(query)

        # 5. Fin du chargement
        spinner.ok("✅")

    # 6. Nettoyage et enrichissement
    forward_df.rename(columns={'setllement_price': 'forward_price'}, inplace=True)
    forward_df['trading_date'] = pd.to_datetime(forward_df['trading_date'], utc=True)
    forward_df['forward_price'] = forward_df['forward_price'].astype(float)
    forward_df['cal_year'] = cal_year_month
    forward_df = forward_df.drop_duplicates()

    # 7. Retour des données
    return forward_df


def get_pfc_fr(price_date: int, delivery_year: int) -> pd.DataFrame:
    """
    Récupère les courbes de prix Price Forward Curve (« PFC ») pour la France depuis Databricks.

    Paramètres :
    -----------
    price_date : int
        Année de la date de prix (exemple : 2024).
    delivery_year : int
        Année de livraison des prix forward (exemple : 2025).

    Retour :
    -------
    pd.DataFrame
        DataFrame contenant les colonnes ['delivery_from', 'price_date', 'forward_price'] 
        correspondant aux dates de livraison, date de prix et prix forward associés.
    """

    # 1. Initialisation du spinner yaspin
    with yaspin(text="Chargement des prix PFC depuis Databricks...") as spinner:

        # 2. Connexion via tentaclio
        databricks = "databricks+thrift://octoenergy-oefr-prod.cloud.databricks.com/"
        with tio.db(databricks) as client:

            # 3. Construction de la requête SQL
            query = f"""
                SELECT delivery_from,
                       price_date,
                       forward_price
                FROM consumer.stg_octo_curves
                WHERE mode = 'EOD'
                  AND asset = 'FRPX'
                  AND year(delivery_from) = '{delivery_year}'
                  AND year(price_date) = '{price_date}'
                ORDER BY price_date
            """

            # 4. Exécution de la requête
            cursor = client.cursor
            cursor.execute(query)
            rows = cursor.fetchall()
            colnames = [desc[0] for desc in cursor.description]

        # 5. Fin du chargement
        spinner.ok("✅")

    # 6. Conversion en DataFrame pandas
    df = pd.DataFrame(rows, columns=colnames)

    # 7. Retour du DataFrame
    return df


def calculate_prem_risk_vol(forecast_df: pd.DataFrame,spot_df: pd.DataFrame,forward_df: pd.DataFrame,quantile: int = 70,plot_chart: bool = False,variability_factor: float = 1.1,save_path: Optional[str] = None) -> float:
    """
    Calcule la prime de risque volume à partir des prévisions de consommation, des prix spot et 
    d’un ensemble de prix forward. Cette prime mesure l’impact de l’erreur de prévision sur la valeur 
    économique, en supposant un écart entre consommation réelle et prévision.

    Paramètres :
    -----------
    forecast_df : pd.DataFrame
        Données de consommation et prévisions, contenant :
            - une colonne 'timestamp' (datetime)
            - une colonne 'forecast' (prévisions de consommation en MW)
            - une colonne 'MW' (consommation réalisée en MW)
    spot_df : pd.DataFrame
        Données de prix spot avec les colonnes ['delivery_from', 'price_eur_per_mwh'].
    forward_df : pd.DataFrame
        Liste des prix forward (calendaires ou autres), avec au minimum la colonne ['forward_price'].
    quantile : int, par défaut 70
        Le quantile à extraire (entre 1 et 100) de la distribution des primes calculées.
    plot_chart : bool, par défaut False
        Si True, affiche un graphique interactif de la distribution des primes de risque volume.
    variability_factor : float, par défaut 1.1
        Facteur multiplicatif appliqué à l’erreur de prévision pour simuler une incertitude plus élevée.
    save_path : str, optionnel
        Si défini, sauvegarde le graphique au format HTML à ce chemin.

    Retour :
    -------
    float
        La valeur du quantile demandé (en €/MWh), représentant la prime de risque volume.
    """

    # 1. Conversion des colonnes temporelles en datetime sans timezone
    forecast_df['timestamp'] = pd.to_datetime(forecast_df['timestamp']).dt.tz_localize(None)
    spot_df['delivery_from'] = pd.to_datetime(spot_df['delivery_from']).dt.tz_localize(None)

    # 2. Année de référence basée sur la dernière date de prévision
    latest_date = forecast_df['timestamp'].max()
    latest_year = latest_date.year
    print(f"Using year from latest date: {latest_year} (latest forecast: {latest_date.strftime('%Y-%m-%d')})")

    # 3. Vérification des prix forward
    if forward_df.empty:
        raise ValueError("No forward prices provided.")
    forward_prices = forward_df['forward_price'].tolist()

    # 4. Jointure forecast + spot
    merged_df = pd.merge(
        forecast_df,
        spot_df,
        left_on='timestamp',
        right_on='delivery_from',
        how='inner'
    )
    if merged_df.empty:
        raise ValueError("No data available to merge spot and forecast.")

    # 5. Simulation de l’erreur de prévision (écart entre réel et prévu)
    merged_df['diff_conso'] = (merged_df['MW'] - merged_df['forecast']) * variability_factor
    conso_totale_MWh = merged_df['MW'].sum()
    if conso_totale_MWh == 0:
        raise ValueError("Annual consumption is zero, division not possible.")

    # 6. Calcul de la prime de risque pour chaque prix forward
    premiums = []
    for fwd_price in forward_prices:
        merged_df['diff_price'] = merged_df['price_eur_per_mwh'] - fwd_price
        merged_df['produit'] = merged_df['diff_conso'] * merged_df['diff_price']
        premium = abs(merged_df['produit'].sum()) / conso_totale_MWh
        premiums.append(premium)

    # 7. Visualisation de la distribution (optionnel)
    if plot_chart or save_path:
        premiums_sorted = sorted(premiums)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=premiums_sorted,
            x=list(range(1, len(premiums_sorted) + 1)),
            mode='lines+markers',
            name='Premiums',
            line=dict(color='cyan')
        ))
        fig.update_layout(
            title="Risk premium distribution (volume)",
            xaxis_title="Index (sorted)",
            yaxis_title="Premium (€/MWh)",
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            hovermode='closest'
        )
        if save_path:
            fig.write_html(save_path)
            print(f"Graphique interactif enregistré : {save_path}")
        if plot_chart:
            fig.show()

    # 8. Extraction du quantile demandé
    if not (1 <= quantile <= 100):
        raise ValueError("Quantile must be an integer between 1 and 100.")
    quantile_value = np.percentile(premiums, quantile)
    print(f"Quantile {quantile} risque volume = {quantile_value:.4f} €/MWh")
    return float(quantile_value)

def calculate_prem_risk_shape(forecast_df: pd.DataFrame,pfc_df: pd.DataFrame,spot_df: pd.DataFrame,quantile: int = 70,plot_chart: bool = False,save_path: Optional[str] = None) -> float:
    """
    Calcule la prime de risque de shape à partir d'une prévision de consommation, des prix forward (PFC)
    et des prix spot. Le résultat représente une mesure du risque pris lorsqu'on achète un produit
    à profil plat et qu'on revend au profil réel sur le marché spot.

    Paramètres :
    -----------
    forecast_df : pd.DataFrame
        Données de prévision de consommation, avec :
            - une colonne 'timestamp' (datetime)
            - une colonne 'MW' (consommation réalisée en MW)
            - une colonne 'forecast' (prévisions de consommation en MW)
    pfc_df : pd.DataFrame
        Données de prix forward (PFC) avec les colonnes :
            ['delivery_from', 'forward_price', 'price_date'].
    spot_df : pd.DataFrame
        Données de prix spot avec les colonnes :
            ['delivery_from', 'price_eur_per_mwh'].
    quantile : int, par défaut 70
        Le quantile à extraire de la distribution des coûts shape (en valeur absolue).
    plot_chart : bool, par défaut False
        Si True, affiche un graphique interactif (Plotly) des valeurs triées de prime de shape.
    save_path : str, optionnel
        Si défini, sauvegarde le graphique interactif au format HTML à ce chemin.

    Retour :
    -------
    float
        La valeur du quantile demandé (en €/MWh), mesurant la prime de risque de shape.
    """

    # 1. Prétraitement de la prévision de consommation
    df_conso_prev = forecast_df.copy()
    df_conso_prev = df_conso_prev.rename(columns={'timestamp': 'delivery_from'})
    df_conso_prev['delivery_from'] = pd.to_datetime(df_conso_prev['delivery_from'], utc=True)
    #df_conso_prev = df_conso_prev[df_conso_prev['MW'] != 0]

    # Suppression des données du 1er avril au 31 octobre (inclus)
    df_conso_prev = df_conso_prev[~df_conso_prev['delivery_from'].dt.month.isin(range(4, 11))]

    # 2. Prétraitement des données PFC
    pfc = pfc_df.copy()
    pfc['delivery_from'] = pd.to_datetime(pfc['delivery_from'], utc=True)

    # 3. Fusion PFC + prévisions conso (jour)
    df = pd.merge(pfc, df_conso_prev[['delivery_from', 'forecast']], on='delivery_from', how='left').dropna()

    df['value'] = df['forward_price'] * df['forecast']
    df['delivery_month'] = pd.to_datetime(df['delivery_from'].dt.tz_localize(None)).dt.to_period('M')
    df['price_date'] = pfc['price_date']

    # 4. Agrégation mensuelle pour simuler un profil plat
    gb_month = df.groupby(['price_date', 'delivery_month']).agg(
        bl_volume_month=('forecast', 'mean'),
        bl_value_month=('value', 'sum'),
        forward_price_sum_month=('forward_price', 'sum')
    )
    gb_month['bl_value_month'] = gb_month['bl_value_month'] / gb_month['forward_price_sum_month']
    gb_month.reset_index(inplace=True)

    # 5. Prétraitement des données spot
    spot = spot_df.copy()
    spot = spot.rename(columns={'price_eur_per_mwh': 'spot_price'})
    spot['delivery_from'] = pd.to_datetime(spot['delivery_from'], utc=True)

    # 6. Fusion conso + PFC + spot
    df = df.merge(spot[['delivery_from', 'spot_price']], on='delivery_from', how='left').dropna()
    df = df.merge(gb_month, on=['price_date', 'delivery_month'], how='left').dropna()

    # 7. Calcul des volumes résiduels entre profil réel et plat
    df['residual_volume'] = df['forecast'] - df['bl_value_month']
    df['residual_value'] = df['residual_volume'] * df['spot_price']

    # 8. Agrégation mensuelle des coûts shape
    agg = df.groupby(['price_date']).agg(
        residual_value_month=('residual_value', 'sum'),
        conso_month=('forecast', 'sum')
    )
    agg['shape_cost'] = agg['residual_value_month'] / agg['conso_month']
    agg['abs_shape_cost'] = agg['shape_cost'].abs()

    # 9. Affichage graphique (optionnel)
    if plot_chart or save_path:
        sorted_vals = agg['abs_shape_cost'].sort_values().reset_index(drop=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=sorted_vals,
            x=list(range(1, len(sorted_vals) + 1)),
            mode='lines+markers',
            name='Shape Risk',
            line=dict(color='cyan')
        ))
        fig.update_layout(
            title="Shape Risk Distribution",
            xaxis_title="Index (sorted)",
            yaxis_title="€/MWh",
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            hovermode='closest'
        )
        if save_path:
            fig.write_html(save_path)
            print(f"Graphique interactif enregistré : {save_path}")
        if plot_chart:
            fig.show()

    # 10. Extraction du quantile souhaité
    quantile_value = np.percentile(agg['abs_shape_cost'], quantile)
    print(f"Quantile {quantile} risque shape = {quantile_value:.4f} €/MWh")
    return float(quantile_value)



def calculate_prem_risk_thermo(load_curve_df: pd.DataFrame, temp_df: pd.DataFrame, spot_df: pd.DataFrame, quantile: int = 70, n_scenarios: int = 1000, temp_variation_range: float = 5.0, plot_chart: bool = False, save_path: Optional[str] = None) -> float:
    """
    Calcule la prime de risque thermique en simulant des scénarios de température 
    s'écartant progressivement de la température normale.

    Paramètres :
    -----------
    load_curve_df : pd.DataFrame
        Données de consommation avec colonnes ['timestamp', 'MW'].
    temp_df : pd.DataFrame
        Données de température avec colonnes ['timestamp', 'temperature'].
    spot_df : pd.DataFrame
        Données de prix spot avec colonnes ['delivery_from', 'price_eur_per_mwh'].
    quantile : int, par défaut 70
        Quantile (en %) à extraire de la distribution des primes calculées.
    n_scenarios : int, par défaut 1000
        Nombre de scénarios de température simulés.
    temp_variation_range : float, par défaut 5.0
        Plage d'écart simulé autour de la température normale (°C).
    plot_chart : bool, par défaut False
        Si True, affiche un graphique interactif (Plotly) des primes simulées triées.
    save_path : str, optionnel
        Si défini, sauvegarde le graphique interactif au format HTML à ce chemin.

    Retour :
    --------
    float
        Valeur du quantile demandé (en €/MWh), mesurant la prime de risque thermique.
    """

    # 1. Définition des mois d'hiver et d'été
    winter_months = [11, 12, 1, 2, 3]
    summer_months = [6, 7, 8, 9]

    # 2. Conversion des colonnes timestamps en datetime UTC
    load_curve_df['timestamp'] = pd.to_datetime(load_curve_df['timestamp'], utc=True)
    temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'], utc=True)
    spot_df['delivery_from'] = pd.to_datetime(spot_df['delivery_from'], utc=True)

    # 3. Fusion "asof" des données consommation avec température sur timestamp le plus proche
    merged = pd.merge_asof(
        load_curve_df.sort_values('timestamp'),
        temp_df.sort_values('timestamp'),
        left_on='timestamp',
        right_on='timestamp',
        direction='nearest'
    )

    # 4. Extraction du mois pour différencier saison hiver/été
    merged['month'] = merged['timestamp'].dt.month

    # 5. Calcul du gradient consommation-température pour l'hiver par régression linéaire
    winter_df = merged[merged['month'].isin(winter_months)]
    X_winter = winter_df['temperature'].values.reshape(-1, 1)
    y_winter = winter_df['MW'].values
    model_winter = LinearRegression().fit(X_winter, y_winter)
    gradient_winter = model_winter.coef_[0]

    # 6. Calcul du gradient consommation-température pour l'été
    summer_df = merged[merged['month'].isin(summer_months)]
    X_summer = summer_df['temperature'].values.reshape(-1, 1)
    y_summer = summer_df['MW'].values
    model_summer = LinearRegression().fit(X_summer, y_summer)
    gradient_summer = model_summer.coef_[0]

    # 7. Filtrage des prix spot sur la période étudiée
    spot_period = spot_df[
        (spot_df['delivery_from'] >= load_curve_df['timestamp'].min()) &
        (spot_df['delivery_from'] <= load_curve_df['timestamp'].max())
    ]
    avg_spot_price = spot_period['price_eur_per_mwh'].mean()

    # 8. Extraction de la température normale sur la période
    temp_period = temp_df[
        (temp_df['timestamp'] >= load_curve_df['timestamp'].min()) &
        (temp_df['timestamp'] <= load_curve_df['timestamp'].max())
    ].copy()

    temp_normal = temp_period['temperature'].values
    month_nums = temp_period['timestamp'].dt.month.values

    # 9. Attribution des gradients selon la saison pour chaque timestamp
    gradients = np.where(
        np.isin(month_nums, winter_months),
        gradient_winter,
        np.where(np.isin(month_nums, summer_months), gradient_summer, 0)
    )

    # 10. Simulation de n_scenarios de températures variant linéairement autour de la température normale
    temp_scenarios = np.array([
        temp_normal + np.linspace(-temp_variation_range, temp_variation_range, n_scenarios)[i]
        for i in range(n_scenarios)
    ])

    # 11. Calcul de l'écart en MW pour chaque scénario
    delta_MW = (temp_scenarios - temp_normal) * gradients

    # 12. Calcul des primes en €/MWh pour chaque scénario
    premiums = np.abs(delta_MW * avg_spot_price).mean(axis=1)

    # 13. Extraction du quantile demandé (conversion % -> fraction)
    quantile_norm = quantile / 100
    quantile_value = np.quantile(premiums, quantile_norm)

    # 14. Affichage graphique (optionnel)
    if plot_chart or save_path:
        sorted_premiums = np.sort(premiums)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=sorted_premiums,
            x=list(range(1, len(sorted_premiums) + 1)),
            mode='lines+markers',
            name='Prime risque thermique',
            line=dict(color='orange')
        ))
        fig.add_hline(y=quantile_value, line_dash="dash", line_color="red",
                      annotation_text=f"{quantile}e percentile = {quantile_value:.2f} €/MWh",
                      annotation_position="top right")
        fig.update_layout(
            title="Distribution des primes de risque thermique",
            xaxis_title="Index (trié)",
            yaxis_title="Prime thermique (€/MWh)",
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            hovermode='closest'
        )
        if save_path:
            fig.write_html(save_path)
            print(f"Graphique interactif enregistré : {save_path}")
        if plot_chart:
            fig.show()

    # 15. Affichage console et retour de la valeur du quantile
    print(f"Quantile {quantile}% prime risque thermique = {quantile_value:.4f} €/MWh")
    return quantile_value
