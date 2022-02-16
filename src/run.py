# -*- coding: utf-8 -*-

import time
import pandas as pd
from mesa.batchrunner import BatchRunner
from model import RecommendationModel
from plots import *
from read_config import *
from utils import store_recommender_systems_generated_data  # create_all_directories

if __name__ == "__main__":
    print("Simulation begins ...\n")
    var_params = {"recommendation_strategy": model_parameters["recommendation_strategy"],
                  "quantile_consumer_expectation": model_parameters["quantile_consumer_expectation"]}

    # create a timestamp for each result fol
    timestr = time.strftime("%Y%m%d-%H%M%S")

    # create_all_directories()
    store_recommender_systems_generated_data()
    batch_run = BatchRunner(RecommendationModel,
                            fixed_parameters=None,
                            variable_parameters=var_params,
                            iterations=model_parameters["number_of_runs"],
                            max_steps=model_parameters["timesteps"],
                            model_reporters={
                                "DataCollector": lambda m: m.datacollector},
                            display_progress=True
                            )
    batch_run.run_all()

    br_df = batch_run.get_model_vars_dataframe()
    br_step_model_data = pd.DataFrame()
    br_step_agent_data = pd.DataFrame()
    for i in range(len(br_df["DataCollector"])):
        i_run_model = br_df["DataCollector"][i].get_model_vars_dataframe()
        br_step_model_data = br_step_model_data.append(i_run_model)
        i_run_agent = br_df["DataCollector"][i].get_agent_vars_dataframe()
        br_step_agent_data = br_step_agent_data.append(i_run_agent)

    plot_results(br_step_model_data, br_step_agent_data, timestr)
    print("Data is stored")
