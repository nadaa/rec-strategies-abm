# -*- coding: utf-8 -*-

import sys

import numpy as np
from mesa import Agent
from mesa.model import Model
from read_config import *
from scipy.stats import beta
from utils import update_consumer_personal_experiences

sys.path.append("..")


class ConsumerAgent(Agent):
    def __init__(self: Agent, id: int, model: Model, beta_params: list, threshold: float) -> None:
        super().__init__(id, model)
        self.consumer_id = id
        self.positive_negative_experience = beta_params.copy()
        self.compute_trust()
        self.initialtrust = self.trust
        self.true_utility = 0
        self.minimum_utility_threshold = threshold
        self.recommended_list = None
        self.selecteditem = None
        self.consumption_probability = self.trust
        self.consumption_probability_limits = [0, 0]  # [lower limit, upper limit]]
        self.provider_reputation_in_memory = 0  # to remember the previous reputation that had seen on the social media

    def consume_item(self: Agent) -> bool:
        """

        :return: bool.

        A function decides either to consume an item or not.
        """
        p = np.random.uniform(0, 1)
        if self.consumption_probability >= p:
            return 1
        else:
            return 0

    def compute_consumption_probability(self: Agent) -> None:
        """

         A function computes consumption probability by considering the personal experiences and other consumers' experiences shared on social media.
        """
        self.consumption_probability = self.trust
        if model_parameters['social_media_on']:
            if self.look_to_social_media():
                cons = model_parameters["trust_weight"] * self.trust + \
                    model_parameters["socia_media_weight"]*self.provider_reputation_in_memory
                self.consumption_probability = max(self.consumption_probability_limits[0], min(
                    self.consumption_probability_limits[1], cons))



    def compute_consumption_prob_limits(self):
        """

        A function to set limits for consumption probability by adding or subtracting a deviation from trust. The deviation_from trust is the result of multiplying:
        (a): which is a weighting factor of the social influence
        social_reliance: which is introduced to control the degree of social influence

        """
        deviation_from_trust = self.model.a * model_parameters["social_media_reliance"]
        self.consumption_probability_limits[0] = max(self.trust - deviation_from_trust, 0)
        self.consumption_probability_limits[1] = min(self.trust + deviation_from_trust, 1)

    def look_to_social_media(self):
        """
        A function to define consumer's decision to observe the social media
        """
        probability_looking_social_media = np.random.uniform()
        if probability_looking_social_media >= model_parameters["observing_socialmedia_likelihood"]:
            self.provider_reputation_in_memory = (
                self.model.social_media[0]) / (self.model.social_media[0] + self.model.social_media[1]+1)
            return 1
        return 0

    def compute_true_utility(self: Agent, item: int) -> float:
        """

        :param item: int item id.

        A function computes the true utility of the consumed item.
        """
        predicted_utility = item["rating"]
        error = np.random.normal(
            model_parameters["error"]["mu"],
            model_parameters["error"]["sd"])
        self.true_utility = predicted_utility + error
        if self.true_utility < 0.5:
            self.true_utility = 0.5
        if self.true_utility > 5:
            self.true_utility = 5
        self.true_utility = round(self.true_utility, 3)

    def pick_item(self: Agent, items: list) -> dict:
        """

        :param items: list of dicts.
        :return: int.

        A function chooses an item from a list of recommendations.
        """
        # generate N probabilities that are summed up to 1 from Dirichlet distribution
        rank_dist = np.random.dirichlet(
            np.ones(self.model.recommendation_length), size=1)
        # sort the probabilities descendingly, the first items on the list have
        # items on the top of the list get higher probabilities
        rank_dist = -np.sort(-rank_dist)
        indcies = list(range(len(items)))
        # pick a random index using the generated probabilities
        selected_indx = np.random.choice(indcies, p=rank_dist[0])
        selected_item = items[selected_indx]
        return selected_item

    def compute_trust(self: Agent) -> None:
        """

         A function updates consumer trust using the expected value of the beta distribution with the previous consumption experiences as the beta parameters.
        """
        self.trust = self.positive_negative_experience[0] / (
            self.positive_negative_experience[0] + self.positive_negative_experience[1])

    def post_to_social_media(self: Agent) -> None:
        p = np.random.uniform(0, 1)
        social_media_prob = self.social_media_prob()
        if p >= social_media_prob:
            if self.is_satisfied():
                self.model.social_media[0] += 1
            else:
                self.model.social_media[1] += 1

    def social_media_prob(self: Agent) -> float:
        """

        :return: float as a probability.

        A function computes the probability of posting to social media from U-shape beta distribution.
        """
        prob = (1.4 - beta.pdf(self.true_utility / 5, a=2, b=2) + 0.2) / 1.6
        return prob

    def send_feedback_decision(self: Agent) -> bool:
        """

        :return: bool as a decision to submit feedback to the provider.

        A function makes decision if a consumer submits feedback to the service provider or not.
        """
        p = np.random.uniform()
        if p >= self.model.feedback_likelihood:
            return 1
        return 0

    def is_satisfied(self: Agent) -> bool:
        """

        :return: bool.

         A function determines if consumer is satisfied of not.
        """
        if self.true_utility >= self.minimum_utility_threshold:
            return 1
        else:
            return 0

    def update_experience(self: Agent) -> None:
        """

         A function counts the number of positive and negative experiences a consumer encounters separately.
         """
        d = abs(self.minimum_utility_threshold - self.true_utility)
        if self.is_satisfied():
            self.positive_negative_experience[0] += update_consumer_personal_experiences(
                d)
        else:
            self.positive_negative_experience[1] += update_consumer_personal_experiences(
                d)

    def step(self):
        self.consumer_adapt()

    def consumer_adapt(self: Agent) -> None:
        """

         A function updates consumer's state variables each time step.
        """
        if model_parameters["drop_out_on"]:
            if self.trust < (
                    self.initialtrust *
                    model_parameters["dropout_threshold"]):
                self.model.dropout_consumers.append(self)

        self.selecteditem = None
        # get recommendtion list
        self.recommended_list = self.model.topn[self.consumer_id]
        # check if the agent consumed all the items
        if not self.recommended_list:
            print(f"No more item available for agent {self.consumer_id}")
            pass
        if self.consume_item():
            # compute the consumption rate
            # selecteditem as a tuple (movieid, rate)
            self.selecteditem = self.pick_item(self.recommended_list)
            # compute the true utility of consumed item
            self.compute_true_utility(self.selecteditem)
            # update provider utilities after consuming the item
            self.model.update_provider_utilities(self.selecteditem)
            send_feedback_to_provider = self.send_feedback_decision()
            if model_parameters["social_media_on"]:
                self.post_to_social_media()
            # remove the selecteditem from the recommendations, so it won't be recommended again
            inx = self.model.recommendations[self.consumer_id].index(
                self.selecteditem)
            del self.model.recommendations[self.consumer_id][inx]
            # replace the predicted utility by the true one
            self.selecteditem["rating"] = self.true_utility
            # send feedback and post public trust
            if send_feedback_to_provider:
                self.selecteditem["feedback"] = 1
            else:
                self.selecteditem["feedback"] = 0
            # save consumed items
            self.model.store_consumed_items(
                self.consumer_id, self.selecteditem)
            self.update_experience()
            self.compute_trust()
        self.compute_consumption_prob_limits()
        self.compute_consumption_probability()
