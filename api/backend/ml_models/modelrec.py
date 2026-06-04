import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import requests
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from flask import current_app
from backend.db_connection import get_db

class university_ranking_model:

    def _get_universities(self) -> list:
        """Fetches all universities from the modelrec table in the database."""
        with get_db().cursor(dictionary=True) as cursor:
            cursor.execute(
                'SELECT name, city, student_fees, highest_degree, staff_fte, web_pages '
                'FROM modelrec '
                'ORDER BY name'
            )
            rows = cursor.fetchall()
        if not rows:
            raise ValueError('No data found...')
        return rows

    def predict(self, student_budget: float, student_degree: int, student_size: int) -> pd.DataFrame:
        """Ranks all universities by cosine similarity to the student's preferences.
        
        Args:
            student_budget: max acceptable student fees in EUR
            student_degree: highest degree level (1=bachelors, 2=masters, 3=doctoral)
            student_size: preferred university size on a 1-10 scale
        
        Returns:
            DataFrame with columns name, city, match_number sorted by best match first.
        """
        budget = float(student_budget)
        degree = int(student_degree)
        size = int(student_size)

        universities = self._get_universities()
        model_df = pd.DataFrame(universities)
        keeping_cols = ['student_fees', 'highest_degree', 'staff_fte']

        X_mat = model_df[keeping_cols].to_numpy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_mat)
        staff_min = model_df['staff_fte'].min()
        staff_max = model_df['staff_fte'].max()

        student_staff = staff_min + (size - 1) * (staff_max - staff_min) / 9
        student_input = np.array([[budget, degree, student_staff]])
        student_input_scaled = scaler.transform(student_input)

        cosine_scores = []
        for i in range(X_scaled.shape[0]):
            uni_vector = X_scaled[i]
            dot_product = np.dot(student_input_scaled[0], uni_vector)
            student_norm = np.linalg.norm(student_input_scaled[0])
            uni_norm = np.linalg.norm(uni_vector)
            if student_norm == 0 or uni_norm == 0:
                cosine_score = 0
            else:
                cosine_score = dot_product / (student_norm * uni_norm)
            cosine_scores.append(cosine_score)

        results_df = pd.DataFrame({
            'name': model_df['name'],
            'city': model_df['city'],
            'cosine_score': cosine_scores
        })

        ranked = results_df.sort_values(by='cosine_score', ascending=False)
        ranked = ranked.reset_index(drop=True)
        ranked.index = ranked.index + 1
        ranked['match_number'] = (ranked['cosine_score'] * 100).round(2).astype(str)

        output = ranked[['name', 'city', 'match_number']]
        output.index.name = 'rank'

        current_app.logger.info(f'Predicted university rankings for student with budget {budget}, degree {degree}, size {size}')
        return output

    def get_top_matches(self, student_budget: float, student_degree: int, student_size: int, top_n: int = 10) -> pd.DataFrame:
        """Returns the top n universities ranked by cosine similarity.
        
        Args:
            student_budget: max acceptable student fees in EUR
            student_degree: highest degree level (1=bachelors, 2=masters, 3=doctoral)
            student_size:   preferred university size on a 1-10 scale
            top_n:          number of results to return (default 10)
        
        Returns:
            DataFrame with the top n matches.
        """
        ranked = self.predict(student_budget, student_degree, student_size)
        return ranked.head(top_n)