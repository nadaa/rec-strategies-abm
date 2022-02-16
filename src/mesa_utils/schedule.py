import random
from collections import defaultdict

from mesa.time import RandomActivation


class RandomActivationByType(RandomActivation):
    '''
    A scheduler which activates each type of agent once per step, in random
    order, with the order reshuffled every step.
    This is equivalent to the NetLogo 'ask type...' and is generally the
    default behavior for an ABM.
    Assumes that all agents have a step() method.
    '''
    agents_by_type = defaultdict(list)

    def __init__(self, model):
        super().__init__(model)
        self.agents_by_type = defaultdict(list)

    def add(self, agent):
        '''
        Add an Agent object to the schedule
        Args:
            agent: An Agent to be added to the schedule.
        '''

        self.agents.append(agent)
        agent_class = type(agent)
        self.agents_by_type[agent_class].append(agent)

    def remove(self, agent):
        '''
        Remove all instances of a given agent from the schedule.
        '''

        while agent in self.agents:
            self.agents.remove(agent)

        agent_class = type(agent)
        while agent in self.agents_by_type[agent_class]:
            self.agents_by_type[agent_class].remove(agent)

    def step(self, by_type=True):
        '''
        Executes the step of each agent type, one at a time, in random order.
        Args:
            by_type: If True, run all agents of a single type before running
                      the next one.
        '''
        if by_type:
            for agent_class in self.agents_by_type:
                self.step_type(agent_class)
            self.steps += 1
            self.time += 1
        else:
            super().step()

    def step_type(self, type):
        '''
        Shuffle order and run all agents of a given type.
        Args:
            type: Class object of the type to run.
        '''
        agents = self.agents_by_type[type]
        random.shuffle(agents)
        for agent in agents:
            agent.step()

    def get_type_count(self, type_class):
        '''
        Returns the current number of agents of certain type in the queue.
        '''
        return len(self.agents_by_type[type_class])