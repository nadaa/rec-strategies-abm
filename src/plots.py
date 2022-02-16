import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from read_config import *
from utils import get_exec_path, store_scenarios, create_directory


def plot_results(model_data: pd.DataFrame, agents_data: pd.DataFrame, t: time) -> None:
    """

     :param model_data: pandas dataframe holds model's state variables.
     :param agents_data: pandas dataframe holds consumers' state variables.
     :param t: time used to be contacted to the execution directory name.

     A function creates all the figures from the generated csv files.
    """
    exec_path = get_exec_path()
    exec_path += t
    create_directory(exec_path)
    store_scenarios(exec_path)
    scenarios = agents_data["model_params"].unique()
    agents_groups = agents_data.groupby("model_params")
    model_groups = model_data.groupby("model_params")
    for s in scenarios:
        agent_scenario = agents_groups.get_group(s)
        model_scenario = model_groups.get_group(s)
        plot_all(exec_path, agent_scenario, model_scenario, s)
        agent_scenario.to_csv(f"{exec_path}/agents-data-{s}.csv", index=False)
        model_scenario.to_csv(f"{exec_path}/model-data-{s}.csv", index=False)


def plot_per_type(exec_path: str, scenario_df: pd.DataFrame, s: str, plot_type: str) -> None:
    """

    :param exec_path: str of execution directory path.
    :param scenario_df: pandas dataframe of sensitive model parameters.
    :param s: str of scenario name.
    :param plot_type: str of plot type.

     A function plots the data for each scenario separately either at at the agent or model scopes.
    """
    fig, ax = plt.subplots(1, 1)
    plt.figure(plot_type)
    tick_spacing = model_parameters["timesteps"] / 10
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    df = scenario_df.groupby(
        "step", as_index=False).agg({plot_type: "mean"})
    plt.plot(list(df["step"]), list(df[plot_type]), label=s)
    plt.legend(loc=(1.1, 0.5))
    plt.tight_layout()
    plt.xlabel("Time")
    plt.ylabel(plot_type.capitalize())
    plt.savefig(f"{exec_path}/time-{plot_type}.png")
    plt.close(fig)


def plot_all(exec_path: str, agent_scenario: pd.DataFrame, model_scenario: pd.DataFrame, s: str) -> None:
    """
    :param exec_path: str of execution directory path.
    :param agent_scenario: pandas dataframe of consumers data per scenario.
    :param model_scenario: pandas dataframe of model data per scenario.
    :param s: str of scenario name.

     A function generates different plots using model and agents data.
    """
    model_scenario = model_scenario[model_scenario["total_profit"] > 0]
    plot_per_type(exec_path, agent_scenario, s, "trust")
    #plot_per_type(exec_path, model_scenario, s, "avg_profit_per_consumption")
    plot_per_type(exec_path, model_scenario, s, "total_profit")
    plot_per_type(exec_path, agent_scenario, s, "consumption_probability")
