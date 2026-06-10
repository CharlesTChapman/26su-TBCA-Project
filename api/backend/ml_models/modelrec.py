import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import math
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from flask import current_app
from backend.db_connection import get_db

class university_ranking_model:

    def _get_universities(self) -> list:
        """Fetches all universities from the university table in the database."""
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT name, location AS city, student_fees, highest_degree, staff_fte, web_pages '
                'FROM university '
                'ORDER BY name'
            )
            rows = cursor.fetchall()
        if not rows:
            raise ValueError('No data found...')
        return rows
    
    def _get_country_coords(self, country: str) -> tuple: # type: ignore
        """Fetches the lat/long for a given country name from the country_coords table.
        
        Args:
            country: country name as entered by the student

        Returns:
            Tuple (latitude, longitude) or None if not found.
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT latitude, longitude FROM country_coords WHERE country = %s',
                (country,)
            )
            row = cursor.fetchone()
        if row is None:
            current_app.logger.warning(f'No coordinates found for country: {country}')
            return None
        return (float(row['latitude']), float(row['longitude']))

    def _filter_by_distance(self, model_df: pd.DataFrame, student_country: str, max_distance_km: float) -> pd.DataFrame:
        """Filters universities to only those within max_distance_km of the student's city.
        
        Args:
            model_df:         full university dataframe
            student_country:     student's city or country from their survey
            max_distance_km:  maximum distance in km

        Returns:
            Filtered dataframe containing only universities within range.
        """
        geolocator = Nominatim(user_agent="tbcacademics")
        student_loc = geolocator.geocode(student_country)
        if student_loc is None:
            current_app.logger.warning(f'Could not geocode student city: {student_country}, skipping distance filter')
            return model_df
        student_coords = (student_loc.latitude, student_loc.longitude)

        def within_range(uni_city: str) -> bool:
            try:
                uni_loc = geolocator.geocode(uni_city)
                if uni_loc is None:
                    return False
                return geodesic(student_coords, (uni_loc.latitude, uni_loc.longitude)).km <= max_distance_km
            except Exception:
                return False

        filtered = model_df[model_df['city'].apply(within_range)].reset_index(drop=True)
        current_app.logger.info(f'Distance filter: {len(filtered)}/{len(model_df)} universities within {max_distance_km}km of {student_country}')
        return filtered

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates the haversine distance in km between two lat/long points.
        
        Args:
            lat1, lon1: coordinates of point 1
            lat2, lon2: coordinates of point 2

        Returns:
            Distance in kilometers.
        """
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _get_country_coords(self, country: str) -> tuple: # type: ignore
        """Fetches the lat/long for a given country name from the country_coords table.
        
        Args:
            country: country name as entered by the student

        Returns:
            Tuple (latitude, longitude) or None if not found.
        """
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT latitude, longitude FROM country_coords WHERE country = %s',
                (country,)
            )
            row = cursor.fetchone()
        if row is None:
            current_app.logger.warning(f'No coordinates found for country: {country}')
            return None
        return (float(row['latitude']), float(row['longitude']))

    def _haversine_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates the haversine distance in km between two lat/long points.
        
        Args:
            lat1, lon1: coordinates of point 1
            lat2, lon2: coordinates of point 2

        Returns:
            Distance in kilometers.
        """
        R = 6371.0
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _filter_by_distance(self, model_df: pd.DataFrame, student_country: str, max_distance_km: float) -> pd.DataFrame:
        """Filters universities to only those within max_distance_km of the student's country.
        
        Args:
            model_df:         full university dataframe
            student_country:  student's country from their survey
            max_distance_km:  maximum distance in km

        Returns:
            Filtered dataframe containing only universities within range.
        """
        coords = self._get_country_coords(student_country)
        if coords is None:
            current_app.logger.warning(f'Skipping distance filter — no coords for: {student_country}')
            return model_df

        student_lat, student_lon = coords

        def within_range(row: pd.Series) -> bool:
            try:
                if pd.isna(row['latitude']) or pd.isna(row['longitude']):
                    return False
                dist = self._haversine_km(student_lat, student_lon, float(row['latitude']), float(row['longitude']))
                return dist <= max_distance_km
            except Exception:
                return False

        filtered = model_df[model_df.apply(within_range, axis=1)].reset_index(drop=True)
        current_app.logger.info(
            f'Distance filter: {len(filtered)}/{len(model_df)} universities within {max_distance_km}km of {student_country}'
        )
        return filtered

    def predict(self, student_budget: float, student_degree: int, student_size: int, top_n: int = None, student_country: str = None, max_distance_km: float = None) -> dict: # type: ignore
        """Ranks all universities by cosine similarity to the student's preferences.
        
        Args:
            student_budget:    max acceptable per-student fees in EUR
            student_degree:    highest degree level (1=bachelors, 2=masters, 3=doctoral)
            student_size:      preferred university size (1=Small, 2=Medium, 3=Large)
            top_n:             number of results to return (default None = all)
            student_country:   student's country for distance filtering (optional)
            max_distance_km:   maximum distance from student's country in km (optional)

        Returns:
            Dict keyed by rank with values {name, city, match_number}.
        """
        budget = float(student_budget)
        degree = int(student_degree)
        size   = int(student_size)

        universities = self._get_universities()
        model_df = pd.DataFrame(universities)
        keeping_cols = ['per_student_fees', 'highest_degree', 'staff_fte']

        if student_country and max_distance_km:
            model_df = self._filter_by_distance(model_df, student_country, max_distance_km)
            if model_df.empty:
                current_app.logger.warning('No universities found within distance range, returning empty result')
                return {}

        model_df = model_df.dropna(subset=keeping_cols).reset_index(drop=True)

        X_mat = model_df[keeping_cols].to_numpy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_mat)
        staff_min = model_df['staff_fte'].min()
        staff_max = model_df['staff_fte'].max()

        student_staff = staff_min + (size - 1) * (staff_max - staff_min) / 2
        student_input = np.array([[budget, degree, student_staff]])
        student_input_scaled = scaler.transform(student_input)

        cosine_scores = []
        for i in range(X_scaled.shape[0]):
            uni_vector   = X_scaled[i]
            dot_product  = np.dot(student_input_scaled[0], uni_vector)
            student_norm = np.linalg.norm(student_input_scaled[0])
            uni_norm     = np.linalg.norm(uni_vector)
            if student_norm == 0 or uni_norm == 0:
                cosine_score = 0
            else:
                cosine_score = dot_product / (student_norm * uni_norm)
            cosine_scores.append(cosine_score)

        results_df = pd.DataFrame({
            'name':         model_df['name'],
            'city':         model_df['city'],
            'cosine_score': cosine_scores
        })

        ranked = results_df.sort_values(by='cosine_score', ascending=False).reset_index(drop=True)
        ranked.index = ranked.index + 1

        if top_n is not None:
            ranked = ranked.head(top_n)

        output = {
            int(rank): {
                'name':         row['name'],
                'city':         row['city'],
                'match_number': round(row['cosine_score'] * 100, 2)
            }
            for rank, row in ranked.iterrows()
        }

        current_app.logger.info(
            f'university.predict(budget={budget}, degree={degree}, size={size}, '
            f'country={student_country}, max_km={max_distance_km})'
        )
        return output
