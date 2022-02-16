from mesa import Agent
from mesa.model import Model
from read_config import *
from utils import *


class providerAgent(Agent):
    def __init__(self: Agent, id: int, model: Model) -> None:
        super().__init__(id, model)
        self.recommendation_strategy = None
        self.recommendations = model.recommendations
        self.total_profit_of_consumed_items = 0
        self.number_of_consumption = 0
        self.avg_profit_per_consumption = 0

    def update_provider_utilities(self: Agent, item: int) -> None:
        """

         :param item: int of item id.

         A function computes service provider"s utilities.
        """
        self.total_profit_of_consumed_items += self.model.profit_data[item["iid"]]
        self.number_of_consumption += 1
        self.avg_profit_per_consumption = self.total_profit_of_consumed_items / \
            self.number_of_consumption

    def get_total_profit(self) -> None:
        return self.total_profit

    def reset_provider_utilities(self) -> None:
        """

        This function resets the utilities of the service provider.
        """
        self.total_profit_of_consumed_items = 0
        self.number_of_consumption = 0
        self.avg_profit_per_consumption = 0

    def apply_recommendation_strategy(self) -> None:
        """

          A function sets a recommendation recommendation_strategy to be applied on the recommended items.
           Five strategies were implemented and one is only used in each simulation run:
           consumer_only: Recommened items to maximize consumer items' utilities.
           balance_equal_weights: Recommened items while balancing consumer items" utilities and provider's utility (profit) using equal weights.
           profit_only: Recommend items to maximize provider's utility.
           balance_unequal_weights: Recommened items while balancing consumer items' utilities and provider's utility (profit) using a higher weight on consumers items' utilities.
           popular_based: Recommened items with the highest number of ratings.
        """
        self.recommendation_strategy = self.model.recommendation_strategy
        self.model.topn = get_top_n(
            self.model.recommendations, model_parameters["recommendation_length"])

    def step(self):
        self.reset_provider_utilities()
        self.apply_recommendation_strategy()
