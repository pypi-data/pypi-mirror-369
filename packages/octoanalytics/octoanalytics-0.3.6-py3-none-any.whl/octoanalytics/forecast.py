"""
Classe Forecast
---------------
Ce module contient la classe Forecast qui permet de :
1. Récupérer les températures horaires moyennes lissées sur les grandes villes françaises
2. Effectuer une prévision de consommation (ou autre cible) à l’aide d’un modèle Random Forest.

Auteur : Jean Bertin
Email : jean.bertin@octopusenergy.fr
"""

import numpy as np
import pandas as pd
import requests
import holidays
from tqdm import tqdm
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


class Forecast:

    @staticmethod
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

    @staticmethod
    def eval_forecastML(df, temp_df, cal_year=None, datetime_col='timestamp', target_col='MW', plot_chart=False, save_path=None):
        """
        Calcule un forecast (et éventuellement affiche un graphique) pour une année donnée.

        Paramètres :
        -----------
        df : pd.DataFrame
            Données historiques contenant au moins les colonnes datetime_col et target_col.
        temp_df : pd.DataFrame
            Données de température avec colonnes ['datetime', 'temperature'].
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
        if cal_year is None and plot_chart:
            raise ValueError("Vous devez fournir `cal_year` si vous souhaitez générer un graphique.")

        # 2. Fixe la graine aléatoire pour assurer la reproductibilité
        np.random.seed(42)

        # 3. Copie des données d'origine pour éviter modifications involontaires
        df = df.copy()

        # 4. Uniformise la colonne datetime
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

        # 8. Définition de la période de test correspondant à l’année cal_year
        test_start = expected_start
        test_end = expected_end

        # 9. Nettoyage des données météo
        temp_df = temp_df.copy()
        temp_df[datetime_col] = pd.to_datetime(temp_df['timestamp'], utc=True).dt.tz_localize(None)
        #temp_df = temp_df.drop(columns=['timestamp'])

        # 10. Fusion avec les données principales
        df = pd.merge(df, temp_df, on=datetime_col, how='left')

        # 11. Remplissage des valeurs manquantes
        df['temperature'] = df['temperature'].ffill().bfill()

        # 12. Ajout des features temporelles
        def add_features(df):
            df['hour'] = df[datetime_col].dt.hour
            df['dayofweek'] = df[datetime_col].dt.dayofweek
            df['month'] = df[datetime_col].dt.month

            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['dayofweek_sin'] = np.sin(2 * np.pi * df['dayofweek'] / 7)
            df['dayofweek_cos'] = np.cos(2 * np.pi * df['dayofweek'] / 7)
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

            df['minute'] = df[datetime_col].dt.minute
            df['is_weekend'] = (df['dayofweek'] >= 5).astype(int)
            df['dayofyear'] = df[datetime_col].dt.dayofyear
            df['week'] = df[datetime_col].dt.isocalendar().week.astype(int)
            df['quarter'] = df[datetime_col].dt.quarter
            df['is_month_start'] = df[datetime_col].dt.is_month_start.astype(int)
            df['is_month_end'] = df[datetime_col].dt.is_month_end.astype(int)

            fr_holidays = holidays.country_holidays('FR')
            df['is_holiday'] = df[datetime_col].dt.date.astype(str).isin(fr_holidays).astype(int)

            df['heating_on'] = (df['temperature'] < 15).astype(int)
            df['cooling_on'] = (df['temperature'] > 25).astype(int)

            df['temp_below_10'] = np.maximum(0, 10 - df['temperature'])
            df['temp_above_30'] = np.maximum(0, df['temperature'] - 30)
            df['temp_diff_15'] = df['temperature'] - 15

            return df

        df = add_features(df)

        # 13. Suppression des valeurs manquantes restantes
        df = df.dropna().reset_index(drop=True)

        # 14. Séparation train/test
        train_df = df[(df[datetime_col] < test_start) | (df[datetime_col] > test_end)].copy()
        test_df = df[(df[datetime_col] >= test_start) & (df[datetime_col] <= test_end)].copy()

        # 15. Vérification de la taille des données d'entraînement
        if len(train_df) < 1000:
            raise ValueError("Pas assez de données pour entraîner le modèle.")

        # 16. Entraînement modèle Random Forest
        features = [col for col in train_df.columns if col not in [datetime_col, target_col]]
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(train_df[features], train_df[target_col])

        # 17. Prédictions sur la période test
        test_df['forecast'] = model.predict(test_df[features])

        # 18. Graphique interactif optionnel
        if plot_chart:
            y_true = test_df[target_col].values
            y_pred = test_df['forecast'].values
            mask = y_true != 0
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

        # 19. Retourne les résultats
        return test_df[[datetime_col, target_col, 'forecast']]
    
    @staticmethod
    def eval_forecast(df,cal_year,datetime_col='timestamp',target_col='MW',plot_chart=False,save_path=None):
        """
        Prévision par translation temporelle en utilisant deux blocs :
        - Bloc APRÈS (année cal_year+1) → mappé sur le DÉBUT de l'année cal_year.
        - Bloc AVANT (année cal_year-1) → mappé sur la FIN de l'année cal_year.
        Alignement des jours de semaine (lundi→lundi). Les trous éventuels sont comblés
        en utilisant les vraies données de l'année de test .

        Paramètres
        ----------
        df : pd.DataFrame
            Données historiques avec au moins [datetime_col, target_col].
        cal_year : int
            Année civile à prédire (ex. 2024).
        datetime_col : str
            Nom de la colonne datetime.
        target_col : str
            Nom de la cible (ex. MW).
        plot_chart : bool
            Si True, trace un graphique Plotly (prévision vs réel + MAPE).
        save_path : str | None
            Si fourni, enregistre le graphique en HTML.

        Retour
        ------
        pd.DataFrame : colonnes [datetime_col, target_col, 'forecast']
        """

        # --- 1) Normalisation & tri
        df = df.copy()
        df[datetime_col] = pd.to_datetime(df[datetime_col], utc=True).dt.tz_localize(None)
        df = df.dropna(subset=[datetime_col, target_col])
        df = df.sort_values(datetime_col).reset_index(drop=True)

        # --- 2) Définition de la période test
        start_test = pd.Timestamp(f'{cal_year}-01-01 00:00:00')
        end_test   = pd.Timestamp(f'{cal_year}-12-31 23:59:59')
        test_mask  = (df[datetime_col] >= start_test) & (df[datetime_col] <= end_test)
        test_df    = df.loc[test_mask, [datetime_col, target_col]].copy()

        if test_df.empty:
            raise ValueError(f"Aucune donnée disponible pour l'année {cal_year}.")

        test_index = test_df[datetime_col]

        # --- 3) Découpe des blocs source
        before_df = df[df[datetime_col] < start_test].copy()   # Bloc AVANT
        after_df  = df[df[datetime_col] > end_test].copy()     # Bloc APRÈS

        if before_df.empty:
            raise ValueError("Bloc avant (données < 1er janvier de l'année test) manquant.")
        if after_df.empty:
            raise ValueError("Bloc après (données > 31 décembre de l'année test) manquant.")

        # --- 4) Fonctions utilitaires
        def _weekday_align_shift(source_start_ts, target_start_ts):
            """Décalage en jours pour aligner le jour de semaine de source sur target."""
            return (target_start_ts.weekday() - source_start_ts.weekday()) % 7

        def _map_block_to_window(block_df, years_delta, window_start, window_end):
            """
            Mappe un bloc source sur une fenêtre cible [window_start, window_end] :
            - Décalage d'années
            - Alignement jours de semaine
            - Reindex exact sur la fenêtre cible
            """
            if block_df.empty:
                return pd.Series(dtype=float)

            tmp = block_df.copy()
            tmp[datetime_col] = tmp[datetime_col] + pd.DateOffset(years=years_delta)
            src_start = tmp[datetime_col].iloc[0]
            day_shift = _weekday_align_shift(src_start, window_start)
            tmp[datetime_col] = tmp[datetime_col] + pd.Timedelta(days=day_shift)

            tmp = tmp[(tmp[datetime_col] >= window_start) & (tmp[datetime_col] <= window_end)].copy()
            if tmp.empty:
                return pd.Series(dtype=float)

            window_index = test_index[(test_index >= window_start) & (test_index <= window_end)]
            tmp = tmp.set_index(datetime_col).sort_index()
            aligned = tmp.reindex(window_index)[target_col]
            return aligned

        # --- 5) Définition des fenêtres cibles
        # Début d'année ← bloc APRÈS
        after_start_src = after_df[datetime_col].min()
        after_end_src   = after_df[datetime_col].max()
        after_window_start = pd.Timestamp(cal_year, after_start_src.month, after_start_src.day,
                                        after_start_src.hour, after_start_src.minute, after_start_src.second)
        after_window_end   = pd.Timestamp(cal_year, after_end_src.month, after_end_src.day,
                                        after_end_src.hour, after_end_src.minute, after_end_src.second)
        after_window_start = max(after_window_start, start_test)
        after_window_end   = min(after_window_end,   end_test)

        # Fin d'année ← bloc AVANT
        before_start_src = before_df[datetime_col].min()
        before_end_src   = before_df[datetime_col].max()
        before_window_start = pd.Timestamp(cal_year, before_start_src.month, before_start_src.day,
                                        before_start_src.hour, before_start_src.minute, before_start_src.second)
        before_window_end   = pd.Timestamp(cal_year, before_end_src.month, before_end_src.day,
                                        before_end_src.hour, before_end_src.minute, before_end_src.second)
        before_window_start = max(before_window_start, start_test)
        before_window_end   = min(before_window_end,   end_test)

        # --- 6) Construction de la prévision
        forecast = pd.Series(index=test_index, dtype=float)

        # Bloc APRÈS
        if after_window_start <= after_window_end:
            f_after = _map_block_to_window(after_df, years_delta=-1,
                                        window_start=after_window_start,
                                        window_end=after_window_end)
            forecast.loc[f_after.index] = f_after.values

        # Bloc AVANT
        if before_window_start <= before_window_end:
            f_before = _map_block_to_window(before_df, years_delta=+1,
                                            window_start=before_window_start,
                                            window_end=before_window_end)
            forecast.loc[f_before.index] = f_before.values

        # --- 7) Remplacement des trous par les vraies valeurs de l'année test
        result = test_df.copy()
        result['forecast'] = forecast.values
        missing_mask = result['forecast'].isna()
        result.loc[missing_mask, 'forecast'] = result.loc[missing_mask, target_col]

        # --- 8) Graphique optionnel
        if plot_chart:
            y_true = result[target_col].values
            y_pred = result['forecast'].values
            mask = ~np.isnan(y_true) & ~np.isnan(y_pred) & (y_true != 0)
            mape = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100 if mask.any() else np.nan

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=result[datetime_col], y=result[target_col],
                mode='lines', name='Réel', line=dict(color='blue')))
            fig.add_trace(go.Scatter(
                x=result[datetime_col], y=result['forecast'],
                mode='lines', name='Prévision',
                line=dict(color='red', dash='dash')))

            title = f'Prévision par translation — cal_year={cal_year}'
            if not np.isnan(mape):
                title += f' — MAPE: {mape:.2f}%'

            fig.update_layout(
                title=title,
                xaxis_title='Date',
                yaxis_title=target_col,
                hovermode='x unified',
                template='plotly_white'
            )

            if save_path:
                fig.write_html(save_path)
            else:
                fig.show()

        return result
    
