
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
import os
import numpy as np
import pandas as pd



class convertYards(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        X['x'] = X['x'] * (120 / 100)
        X['y'] = X['y'] * (80 / 100)
        X['endX'] = X['endX'] * (120 / 100)
        X['endY'] = X['endY'] * (80 / 100)
        return X


class customScaler(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.max_x = 120
        self.max_y = 80
        return self

    def transform(self, X, y=None):
        X['x'] = X['x'] / 120
        X['y'] = X['y'] / 120
        X['endX'] = X['endX'] / 120
        X['endY'] = X['endY'] / 120
        return X


def get_pass_clusters(events, data_mode='whoscored'):
    
    if data_mode == 'whoscored':
        passes_out = events[events['eventType'] == 'Pass'].copy()
    elif data_mode == 'statsbomb':
        passes_out = events[events['type_name'] == 'Pass'].copy()
        passes_out['x'] = 100*passes_out['x']/120
        passes_out['y'] = 100*passes_out['y']/80
        passes_out['endX'] = 100*passes_out['end_x'] / 120
        passes_out['endY'] = 100*passes_out['end_y'] / 80
    else:
        raise ValueError("Specify 'whoscored' or 'statsbomb' as data mode")

    
    current_dir = os.getcwd()
    os.chdir(current_dir.split("football-data-analytics")[0] +
             "football-data-analytics/model_directory/pass_cluster_model")
    cluster_model = joblib.load("PassClusterModel65.joblib")
    os.chdir(current_dir)

    
    passes_out['pass_cluster_id'] = cluster_model.predict(passes_out)
    cluster_centers = cluster_model['model'].cluster_centers_ * 120
    passes_out['pass_cluster_mean_x'] = passes_out['pass_cluster_id'].apply(lambda x: cluster_centers[x, 0])
    passes_out['pass_cluster_mean_y'] = passes_out['pass_cluster_id'].apply(lambda x: cluster_centers[x, 1])
    passes_out['pass_cluster_mean_end_x'] = passes_out['pass_cluster_id'].apply(lambda x: cluster_centers[x, 2])
    passes_out['pass_cluster_mean_end_y'] = passes_out['pass_cluster_id'].apply(lambda x: cluster_centers[x, 3])

   
    if data_mode == 'whoscored':
        passes_out['pass_cluster_mean_x'] = 100*passes_out['pass_cluster_mean_x']/120
        passes_out['pass_cluster_mean_y'] = 100*passes_out['pass_cluster_mean_y']/80
        passes_out['pass_cluster_mean_end_x'] = 100*passes_out['pass_cluster_mean_end_x']/120
        passes_out['pass_cluster_mean_end_y'] = 100*passes_out['pass_cluster_mean_end_y']/80

    elif data_mode == 'statsbomb':
        passes_out['x'] = 120*passes_out['x']/100
        passes_out['y'] = 80*passes_out['y']/100
        passes_out = passes_out.drop(columns=['endX', 'endY'])

    return passes_out


def simulate_match_outcome(events, matches, match_id, sim_count=10000):
    
    home_goal_list = []
    away_goal_list = []
    outcome_list = []

    
    match_simulate = matches[matches['match_id'] == match_id]
    match_xg_events = events[(events['match_id'] == match_id) &
                             (events['shot_statsbomb_xg'] == events['shot_statsbomb_xg'])]
    home_xg_list = match_xg_events[match_xg_events['team_name'] == match_simulate['home_team'].values[0]][
        'shot_statsbomb_xg'].values
    away_xg_list = match_xg_events[match_xg_events['team_name'] == match_simulate['away_team'].values[0]][
        'shot_statsbomb_xg'].values

    
    for i in range(sim_count):

        
        home_goals = 0
        away_goals = 0

        
        if len(home_xg_list) > 0:

            for xg_shot in home_xg_list:
                rand_prob = np.random.random()
                home_goals = home_goals + 1 if rand_prob < xg_shot else home_goals

        
        if len(away_xg_list) > 0:

            for xg_shot in away_xg_list:
                rand_prob = np.random.random()
                away_goals = away_goals + 1 if rand_prob < xg_shot else away_goals

        
        home_goal_list.append(home_goals)
        away_goal_list.append(away_goals)

        
        outcome = 'home' if home_goals > away_goals else 'away' if away_goals > home_goals else 'draw'
        outcome_list.append(outcome)

    
    match_simulation_results = pd.DataFrame(zip(home_goal_list, away_goal_list, outcome_list),
                                            columns=['home_goals', 'away_goals', 'outcome'])
    match_simulation_results['home_team'] = match_simulate['home_team'].values[0]
    match_simulation_results['away_team'] = match_simulate['away_team'].values[0]

   
    result_dict = dict()

    
    result_dict['match_id'] = match_id
    result_dict['home_xg'] = home_xg_list.sum()
    result_dict['away_xg'] = away_xg_list.sum()
    result_dict['home_win_probability'] = outcome_list.count('home') / sim_count
    result_dict['away_win_probability'] = outcome_list.count('away') / sim_count
    result_dict['draw_probability'] = outcome_list.count('draw') / sim_count
    result_dict['home_xpoints'] = result_dict['home_win_probability'] * 3 + result_dict['draw_probability'] * 1
    result_dict['away_xpoints'] = result_dict['away_win_probability'] * 3 + result_dict['draw_probability'] * 1

    
    if 'home_xpoints' in matches.columns:
        matches_out = matches.copy()
        matches_out.loc[matches['match_id'] == match_id, list(result_dict.keys())[1:]] = list(result_dict.values())[
                                                                                            1:]
    else:
        join_df = pd.DataFrame(result_dict, index=[0])
        matches_out = pd.merge(matches, join_df, left_on='match_id', right_on='match_id', how='left')

    return matches_out, match_simulation_results

        
        if len(home_xg_list) > 0:

            for xg_shot in home_xg_list:
                rand_prob = np.random.random()
                home_goals = home_goals + 1 if rand_prob < xg_shot else home_goals

       
        if len(away_xg_list) > 0:

            for xg_shot in away_xg_list:
                rand_prob = np.random.random()
                away_goals = away_goals + 1 if rand_prob < xg_shot else away_goals

       
        home_goal_list.append(home_goals)
        away_goal_list.append(away_goals)

        
        outcome = 'home' if home_goals > away_goals else 'away' if away_goals > home_goals else 'draw'
        outcome_list.append(outcome)

    
    match_simulation_results = pd.DataFrame(zip(home_goal_list, away_goal_list, outcome_list),
                                            columns=['home_goals', 'away_goals', 'outcome'])
    match_simulation_results['home_team'] = match_simulate['home_team'].values[0]
    match_simulation_results['away_team'] = match_simulate['away_team'].values[0]

    
    result_dict = dict()

    
    result_dict['match_id'] = match_id
    result_dict['home_xg'] = home_xg_list.sum()
    result_dict['away_xg'] = away_xg_list.sum()
    result_dict['home_win_probability'] = outcome_list.count('home') / sim_count
    result_dict['away_win_probability'] = outcome_list.count('away') / sim_count
    result_dict['draw_probability'] = outcome_list.count('draw') / sim_count
    result_dict['home_xpoints'] = result_dict['home_win_probability'] * 3 + result_dict['draw_probability'] * 1
    result_dict['away_xpoints'] = result_dict['away_win_probability'] * 3 + result_dict['draw_probability'] * 1

    
    if 'home_xpoints' in matches.columns:
        matches_out = matches.copy()
        matches_out.loc[matches['match_id'] == match_id, list(result_dict.keys())[1:]] = list(result_dict.values())[
                                                                                            1:]
    else:
        join_df = pd.DataFrame(result_dict, index=[0])
        matches_out = pd.merge(matches, join_df, left_on='match_id', right_on='match_id', how='left')

    return matches_out, match_simulation_results
