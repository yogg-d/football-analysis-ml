"""Modelling tools: pass clustering and expected-points simulation."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class convertYards(BaseEstimator, TransformerMixin):
    """Convert 0-100 pitch coords to yards (120 x 80). Operates on a copy."""

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X = X.copy()
        for col, scale in (("x", 120 / 100), ("y", 80 / 100),
                           ("endX", 120 / 100), ("endY", 80 / 100)):
            if col in X.columns:
                X[col] = X[col] * scale
        return X


class customScaler(BaseEstimator, TransformerMixin):
    """Scale yard coords to 0-1. x/120, y/80 (fixes old bug where y was /120).

    NOTE: ``PassClusterModel65.joblib`` was trained with the buggy /120
    scaler, so its predictions will shift slightly under the corrected
    scaler. Retrain the clustering pipeline with this fixed scaler when
    convenient; the code path is otherwise unchanged.
    """

    def fit(self, X, y=None):
        self.max_x = 120
        self.max_y = 80
        return self

    def transform(self, X, y=None):
        X = X.copy()
        for col in ("x", "endX"):
            if col in X.columns:
                X[col] = X[col] / 120
        for col in ("y", "endY"):
            if col in X.columns:
                X[col] = X[col] / 80
        return X


def _pass_cluster_model_path():
    # tools/models.py -> repo root -> model/pass_cluster_model
    return (Path(__file__).resolve().parent.parent
            / "model" / "pass_cluster_model" / "PassClusterModel65.joblib")


def get_pass_clusters(events, data_mode='whoscored'):
    """Assign pass-cluster ids using the saved 65-cluster k-means pipeline."""
    if data_mode == 'whoscored':
        passes_out = events[events['eventType'] == 'Pass'].copy()
    elif data_mode == 'statsbomb':
        passes_out = events[events['type_name'] == 'Pass'].copy()
        passes_out['x'] = 100 * passes_out['x'] / 120
        passes_out['y'] = 100 * passes_out['y'] / 80
        passes_out['endX'] = 100 * passes_out['end_x'] / 120
        passes_out['endY'] = 100 * passes_out['end_y'] / 80
    else:
        raise ValueError("Specify 'whoscored' or 'statsbomb' as data mode")

    if passes_out.empty:
        passes_out['pass_cluster_id'] = pd.Series(dtype=int)
        return passes_out

    model_path = _pass_cluster_model_path()
    if not model_path.exists():
        raise FileNotFoundError(f"Pass cluster model not found at {model_path}")
    cluster_model = joblib.load(model_path)

    passes_out['pass_cluster_id'] = cluster_model.predict(passes_out)

    # cluster centres are in scaled space; recover yard coords robustly
    try:
        model_step = (cluster_model.named_steps['model']
                      if hasattr(cluster_model, 'named_steps') else cluster_model['model'])
        cluster_centers = np.asarray(model_step.cluster_centers_) * 120
    except Exception:
        cluster_centers = None

    if cluster_centers is not None:
        cid = passes_out['pass_cluster_id'].to_numpy()
        passes_out['pass_cluster_mean_x'] = cluster_centers[cid, 0]
        passes_out['pass_cluster_mean_y'] = cluster_centers[cid, 1]
        passes_out['pass_cluster_mean_end_x'] = cluster_centers[cid, 2]
        passes_out['pass_cluster_mean_end_y'] = cluster_centers[cid, 3]

        if data_mode == 'whoscored':
            passes_out['pass_cluster_mean_x'] = 100 * passes_out['pass_cluster_mean_x'] / 120
            passes_out['pass_cluster_mean_y'] = 100 * passes_out['pass_cluster_mean_y'] / 80
            passes_out['pass_cluster_mean_end_x'] = 100 * passes_out['pass_cluster_mean_end_x'] / 120
            passes_out['pass_cluster_mean_end_y'] = 100 * passes_out['pass_cluster_mean_end_y'] / 80

    if data_mode == 'statsbomb':
        passes_out['x'] = 120 * passes_out['x'] / 100
        passes_out['y'] = 80 * passes_out['y'] / 100
        passes_out = passes_out.drop(columns=['endX', 'endY'], errors='ignore')

    return passes_out


def simulate_match_outcome(events, matches, match_id, sim_count=10000, seed=None):
    """Monte-Carlo match outcome from shot xG (vectorised, reproducible)."""
    rng = np.random.default_rng(seed)
    match_simulate = matches[matches['match_id'] == match_id]
    if match_simulate.empty:
        raise ValueError(f"match_id {match_id} not found in matches dataframe")
    match_xg_events = events[(events['match_id'] == match_id)
                             & events['shot_statsbomb_xg'].notna()]
    home_team = match_simulate['home_team'].values[0]
    away_team = match_simulate['away_team'].values[0]
    home_xg_list = match_xg_events[match_xg_events['team_name'] == home_team][
        'shot_statsbomb_xg'].to_numpy(dtype=float)
    away_xg_list = match_xg_events[match_xg_events['team_name'] == away_team][
        'shot_statsbomb_xg'].to_numpy(dtype=float)

    home_goals = (rng.random((sim_count, len(home_xg_list))) < home_xg_list).sum(axis=1) \
        if len(home_xg_list) else np.zeros(sim_count, dtype=int)
    away_goals = (rng.random((sim_count, len(away_xg_list))) < away_xg_list).sum(axis=1) \
        if len(away_xg_list) else np.zeros(sim_count, dtype=int)
    outcomes = np.where(home_goals > away_goals, 'home',
                        np.where(away_goals > home_goals, 'away', 'draw'))

    match_simulation_results = pd.DataFrame(
        {'home_goals': home_goals, 'away_goals': away_goals, 'outcome': outcomes})
    match_simulation_results['home_team'] = home_team
    match_simulation_results['away_team'] = away_team

    result_dict = {
        'match_id': match_id,
        'home_xg': float(home_xg_list.sum()),
        'away_xg': float(away_xg_list.sum()),
        'home_win_probability': float((outcomes == 'home').mean()),
        'away_win_probability': float((outcomes == 'away').mean()),
        'draw_probability': float((outcomes == 'draw').mean()),
    }
    result_dict['home_xpoints'] = result_dict['home_win_probability'] * 3 + result_dict['draw_probability']
    result_dict['away_xpoints'] = result_dict['away_win_probability'] * 3 + result_dict['draw_probability']

    if 'home_xpoints' in matches.columns:
        matches_out = matches.copy()
        for k, v in result_dict.items():
            if k == 'match_id':
                continue
            matches_out.loc[matches_out['match_id'] == match_id, k] = v
    else:
        join_df = pd.DataFrame(result_dict, index=[0])
        matches_out = pd.merge(matches, join_df, on='match_id', how='left')

    return matches_out, match_simulation_results
