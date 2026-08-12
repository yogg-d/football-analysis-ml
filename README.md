# football-analysis-ml
Analysis and visualisation of football data.


Python is used for extraction, processing, analysis and visualisation of event data, aggregated team data, market value data and more.

## Workflow
data_directory: Storage of raw football data used for projects.
tools: Custom python package containing modules that support football data import, processing, manipulation and visualisation.
projects: Series of projects that cover various elements of football data analytics. Also contains any template scripts used to import raw data from various football data APIs, websites or data services.

## Projects

### Model Development and Implementation

####  Expected Goals Modelling

Data Source: Wyscout

Project Area: model & model_development_and_implementation

Code: xg_log_regression_model.py, xg_neural_network.py & shot_xg_plot.py

Summary and Output: Implementation and testing of basic expected goals probabilistic models. This work includes development and comparison of a logistic regression expected goals model and a neural network expected goals model, each trained off over 40000 shots taken across Europe's 'big five' leagues during the 2017/2018 season. The models are used to calculate expected goals for specific players, clubs and leagues over a defined time period.

#### Pass Cluster Modelling

Data Source: Opta

Project Area: model, model_development_and_implementation & External Repo: ml_models_collection

Code: pass_cluster_data_collection.py, models.py, External Repo: ml_model.ipynb

Summary and Output: Using 5,000,000+ passes withn Europe's "Big 5" leagues (Opta data, 2019/20 - 2022/23), I have constructed a clustering model that is able to assign successful passes to one of 65 clusters. This work involves the construction of a machine learning pipeline and testing of a variety of classification algorithms. The chosen model uses a k Means clustering algorithm to assign passes, which I have then packaged up within a clustering function to support many of my football analytics projects.

#### Expected Points Modelling

Data Source: Statsbomb

Project Area: tools

Code: models.py

Summary and Output: Implementation of a Monte-Carlo method to model the probability of individual match outcomes based on shot events and their associated expected goals (xG). A large number (10000+) of simulations are run on a given match to approximate win probability for each team, and draw probability. Expected points in a given match is then simply calculated as 3 × win_probability + 1 × draw_proability. The method adopted is reliant on the assumption that xG represents scoring probability, and that individual shot events are independent.
