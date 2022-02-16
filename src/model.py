# -*- coding: utf-8 -*-

import itertools
import pickle
import time
from collections import defaultdict
import numpy as np
from consumer import ConsumerAgent
from mesa.model import Model
from mesa_utils.datacollection import DataCollector
from mesa_utils.schedule import RandomActivationByType
from read_config import *
from service_provider import providerAgent
from utils import *


class RecommendationModel(Model):
    c = itertools.count(1)

    def __init__(self, **kwargs):
        self.schedule = RandomActivationByType(self)
        self.running = True

        self.initialize_parameters(**kwargs)
        # Setup agents
        self.create_provider()
        self.create_consumers()

        # collecting data from the simulation
        self.datacollector = DataCollector(
            model_reporters={"Strategy": "recommendation_strategy",
                             "model_params": get_params,
                             "step": lambda m: m.schedule.steps,
                             "total_profit": lambda m: np.round(m.total_profit, 3),
                             "number_of_consumption": lambda m: np.round(m.number_of_consumption, 3),
                             "avg_profit_per_consumption": lambda m: np.round(m.avg_profit_per_consumption, 3)
                             },
            agent_reporters={
                "step": lambda a: a.model.schedule.steps if a.__class__.__name__ == "ConsumerAgent" else None,
                "consumerId": lambda a: a.consumer_id if a.__class__.__name__ == "ConsumerAgent" else None,
                "trust": lambda a: a.trust if a.__class__.__name__ == "ConsumerAgent" else None,

                "minimum_utility_threshold": lambda
                a: a.minimum_utility_threshold if a.__class__.__name__ == "ConsumerAgent" else None,
                "true_utility": lambda a: a.true_utility if a.__class__.__name__ == "ConsumerAgent" else None,
                "selecteditem": lambda a: a.selecteditem if a.__class__.__name__ == "ConsumerAgent" else None,
                "consumption_probability": lambda a: a.consumption_probability if a.__class__.__name__ == "ConsumerAgent" else None,
                "lower_limit": lambda a: a.consumption_probability_limits[0] if a.__class__.__name__ == "ConsumerAgent" else None,
                "upper_limit": lambda a: a.consumption_probability_limits[1] if a.__class__.__name__ == "ConsumerAgent" else None,
                "model_params": lambda a: get_params(a) if a.__class__.__name__ == "ConsumerAgent" else None,
                "strategy": lambda a: a.model.recommendation_strategy if a.__class__.__name__ == "ConsumerAgent" else None,
                "is_satisfied": lambda a: a.is_satisfied() if a.__class__.__name__ == "ConsumerAgent" else None,
                "num_positive_personal": lambda a: np.round(a.positive_negative_experience[0],
                                                            3) if a.__class__.__name__ == "ConsumerAgent" else None,
                "num_negative_personal": lambda a: np.round(a.positive_negative_experience[1],
                                                            3) if a.__class__.__name__ == "ConsumerAgent" else None
            }
        )
        self.datacollector.collect(self)

    def create_provider(self: object) -> None:
        """

         This function creates a provider agent and adds it to the scheduler to be activated before any agent.
        """
        provider = providerAgent(0, self)
        self.schedule.add(provider)

    def create_consumers(self: object) -> None:
        """

         A function creates consumer agents and adds them to the scheduler to be activated in a random order.
        """
        datapath = get_data_dir()
        initials_betapath = os.path.join(datapath, "trust", "beta_initials.p")
        initial_beta = pickle.load(open(initials_betapath, "rb"))
        for i in range(1, self.num_consumers + 1):
            beta_params = initial_beta[i]
            consumer = ConsumerAgent(
                i, self, beta_params, self.consumers_thresholds[i])
            self.schedule.add(consumer)

    def initialize_parameters(self: object, **kwargs: dict) -> None:
        """

        :param **kwargs: dict may store parameters values.

         This function initialize model variables using the parameters defined in the config file.
         Model variables hold values to be shared with all agents.
        """
        self.consumers_thresholds = {}
        recdata_path = get_rec_dir()
        self.recommendations = pickle.load(
            open(f"{recdata_path}/consumers_items_utilities_predictions.p", "rb"))
        self.ratings_df = get_ratings_data()
        self.recommendation_strategy = kwargs["recommendation_strategy"]
        self.quantile_consumer_expectation = kwargs["quantile_consumer_expectation"]
        self.recommendation_length = model_parameters["recommendation_length"]
        self.seed = next(self.c)
        self.profit_data = generate_profitdata(self.seed)
        self.num_consumers = self.ratings_df["userId"].nunique()
        self.num_items = get_num_items
        self.user_consumed_items = defaultdict(list)
        self.time = model_parameters["timesteps"]
        self.runs = model_parameters["number_of_runs"]
        self.feedback_likelihood = model_parameters["feedback_likelihood"]
        if self.seed == self.runs:
            setattr(RecommendationModel, "c", itertools.count(1))
        # compute the consumers" expectation thresholds
        self.compute_thresholds()
        # get the recommendations
        self.get_precomputed_consumers_utilities(0)
        self.social_media = [0, 0]  # [number_of_likes, number_of dislikes]
        self.dropout_consumers = []
        self.topn = None
        # the output of these variables are taken from the provider agent
        self.total_profit = 0
        self.number_of_consumption = 0
        self.avg_profit_per_consumption = 0

    def compute_thresholds(self: object) -> None:
        """

         This function computes the expectation threshold for each consumer by taking the quantile value of the items ranked
         descendingly according to their perceived utilities to each consumer.
        """
        print("Compute consumer's expectation thresholds..")
        for c, recs in self.recommendations.items():
            ratings_c = [r["rating"] for r in recs]
            self.consumers_thresholds[c] = np.quantile(
                ratings_c, self.quantile_consumer_expectation)
        print("Done")

    def update_consumer_thresholds(self: object) -> None:
        """

         This function adds precomputed the expectation thresholds for each consumer.
        """
        self.compute_thresholds()
        consumers_class = list(self.schedule.agents_by_type.keys())[1]
        for a in self.schedule.agents_by_type[consumers_class]:
            a.minimum_utility_threshold = self.consumers_thresholds[a.consumer_id]

    def get_precomputed_consumers_utilities(self, i: bool) -> None:
        """
        :param i: bool as flag to distinguish initial consumer utilities or an update of the predictions.
         A function loads the precomputed consumers items" utilities or update the previous utilities.
        """
        weights = [[0.5, 0.5], [0, 1], [0.9, 0.1]]
        recdata_path = get_rec_dir()
        if self.recommendation_strategy == "consumer_only":
            pass

        elif self.recommendation_strategy == "balance_equal_weights":
            self.recommendations = rerank_items_consider_profit(
                self.recommendations, self.profit_data, weights[0])

        elif self.recommendation_strategy == "profit_only":
            self.recommendations = rerank_items_consider_profit(
                self.recommendations, self.profit_data, weights[1])

        elif self.recommendation_strategy == "balance_unequal_weights":
            self.recommendations = rerank_items_consider_profit(
                self.recommendations, self.profit_data, weights[2])

        else:
            if i == 0:
                self.recommendations = pickle.load(
                    open(f"{recdata_path}/consumers_items_utilities_predictions_popular.p", "rb"))
            else:
                popular_items = get_popular_items(get_ratings_data())
                self.recommendations = get_predictions_popular_items(
                    self.num_consumers, popular_items, self.predictive_model)

    def update_provider_utilities(self: object, item: int) -> None:
        """

        :param item: int represents the consumed item.

         This function summed up the profit gained from consumed items
        """
        # get the provider instance from the scheduler
        provider_class = list(self.schedule.agents_by_type.keys())[0]
        provider = self.schedule.agents_by_type[provider_class][0]
        provider.update_provider_utilities(item)
        self.total_profit = provider.total_profit_of_consumed_items
        self.number_of_consumption = provider.number_of_consumption
        self.avg_profit_per_consumption = provider.avg_profit_per_consumption

    def update_predictions(self: object) -> None:
        """

         A function predicts consumers' utilities periodically in the simulation.
         considering consumers' feedback
         """
        predictions, predictive_model = predict_consumers_items_utilities(
            self.ratings_df)
        self.predictive_model = predictive_model
        self.recommendations = get_ordered_recs(predictions)
        self.get_precomputed_consumers_utilities(1)
        self.remove_consumed_items()

    def recompute_consumers_utilities(self: object) -> None:
        """

        A function to replace the predicted consumers utilities with the true utilities of the consumed items
        """
        for k, vlist in self.user_consumed_items.items():
            for v in vlist:
                # if the flag of sending feedback is on
                if v["feedback"]:
                    row = {
                        "userId": k, "movieId": v["iid"], "rating": rescale_rating(v["rating"])}
                    self.ratings_df = self.ratings_df.append(
                        row, ignore_index=True)
        self.update_predictions()
        self.user_consumed_items = defaultdict(list)

    def remove_consumed_items(self: object) -> None:
        """

        A function to remove the consumed items for each consumer to make sure consumers receive unique recommendations
        """
        for uid, recs in self.recommendations.items():
            s = set([(x["iid"]) for x in self.user_consumed_items[uid]])
            recs = [x for x in recs if x["iid"] not in s]
            self.recommendations[uid] = recs
        self.user_consumed_items = defaultdict(list)

    def store_consumed_items(self: object, consumer_id: int, item_id: int) -> None:
        """

        :param consumer_id: A consumer id who consumed an item
        :param item_id: An id of the selected item

         A function to store consumed items for each consumer in a dict
        """
        self.user_consumed_items[consumer_id].append(item_id)

    def step(self):
        """

        A function to handle model adaptation each time step
        """
        t0 = time.process_time()
        if (self.schedule.steps + 1) % model_parameters["frequency_update_expectation"] == 0:
            self.update_consumer_thresholds()

        # recompute consumers' utilities
        # if (self.schedule.steps + 1) % model_parameters["frequency_recompute_utilities"] == 0:
        #     self.recompute_consumers_utilities()

        # compute a, as the influence strength of social media, model_parameters["numposts_threshold"]: is the minimum amount of posts required by
        # consumers to be influenced by the social media
        num_posts = self.social_media[0] + \
            self.social_media[1]
        self.a = min((num_posts / (model_parameters["numposts_threshold"])), 1)
        self.schedule.step()
        # remove dropout consumers from the platform
        for c in self.dropout_consumers:
            c.active = False
            self.schedule.remove(c)
        self.dropout_consumers = []
        # collect data
        self.datacollector.collect(self)
        t1 = time.process_time()
        print(f"step {self.schedule.steps}, time spent: {t1 - t0}")
