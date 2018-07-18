import numpy as np
from scipy import stats
import time

class Model(object):
    """A model to describe opinion dynamics with continuous opinion and information filtering.
    """

    def __init__(self,
                 adjacency_matrix,
                 opinion,
                 information_uptake,
                 propaganda = None,
                 convergence_parameter = (1e9, 10, 1e-6),
                 step_resolution = None
                 ):

        """Initializes an instance of the model.

        Parameters
        ----------

        adjacency_matrix: numpy array (2D)
        opinion: numpy array (1D)
        information_uptake: int
        propaganda: list or tuple
            List of the opinion that propagandists have (e.g. [1,1,1,1], or a tuple (density, opinion)
        convergence_parameter: triple
            (max_step, consecutive_steps, consensus_)condition
        step_resolution: int
        """

        # number of individuals
        self.N = adjacency_matrix.shape[0]

        # contact graph
        self.adjacency_matrix= adjacency_matrix

        # parameters
        self.opinion = opinion
        self.information_uptake = information_uptake

        # propaganda
        self.propaganda = propaganda
        if isinstance(propaganda,list):
            for index, op in enumerate(propaganda):
                self.opinion[index] = op
                self.propaganda_length = len(self.propaganda)
        elif isinstance(propaganda, tuple) and int(propaganda[0] * self.N) > 0:
            for i in range(int(propaganda[0] * self.N)):
                self.opinion[i] = propaganda[1]
                self.propaganda_length = int(propaganda[0] * self.N)
        else:
            self.propaganda_length = 0

        # convergence parameter
        self.convergence_parameter = convergence_parameter

        # resolution for the trajectory
        if step_resolution == None:
            self.step_resolution = 1e9
        else:
            self.step_resolution = step_resolution

        # consensus
        self.consensus = None

        # a counter to check for convergence of the model
        self.counter = 0

        # average degree
        average_degree = np.sum(adjacency_matrix)/self.N

        # trajectory dict
        self.trajectory = {'opinion' : [],
                           'time' : [],
                           'N' : self.N,
                           'consensus' : self.consensus,
                           'information uptake' : self.information_uptake,
                           }

        print("model initialized with {} agents each having an information uptake of {} and an average degree of {}."
              .format(self.N, self.information_uptake, average_degree))

    def run(self):
        """Performs the dynamics until consensus or steps is reached

        Parameters
        ----------

        Returns
        -------
        self.trajectory: dict
        """

        # perform the amount of step as specified in self.convergence_parameter[0]
        for i in range(int(self.convergence_parameter[0])):

            # check for consensus and save to trajectory and terminate if consensus is reached
            if self.check_for_consensus_opinion(int(self.N * self.convergence_parameter[1])):
                self.save_to_trajectory(i)
                return self.trajectory

            # save opinions to trajectory
            self.save_to_trajectory(i)

            # randomly choosing an agent and their neighbors
            agent, neighbors = self.update_candidates()

            # perform opinion update
            self.opinion_update(agent, neighbors)

        self.consensus = False
        self.save_to_trajectory(int(self.convergence_parameter[0]))

        return self.trajectory

    def check_for_consensus_opinion(self, max_count):
        """Checks if consensus is reached.

        Parameters
        ----------
        max_count: int
            the amount of necessary consecutive time steps

        Returns
        -------
        True if consensus is reached, otherwise False.
        """

        if self.counter >= max_count:
            self.consensus = True
            print("......consensus reached")
            return self.consensus

        return False

    def update_candidates(self):
        """Randomly selects an agent and their neighbors.

        Returns
        -------
        agent: int
            a randomly selected agent
        neighbors: list
            the neighbors of the selected agent
        """

        # randomly select agent
        agent = np.random.randint(self.N)
        # check if the agent is a zealot/propagandist and repeat this step if so
        if self.propaganda and agent < self.propaganda_length:
            agent = self.update_candidates()[0]

        # getting the neighborhood of the agent
        neighbors = self.adjacency_matrix[agent].nonzero()[0]

        return agent, neighbors

    def opinion_update(self, agent, neighbors):
        """ The agent spreads their opinion to its followers.

        Parameters
        ----------
        agent: int
        neighbors: np.array

        Returns
        -------

        """

        opinions = self.opinion

        amount_of_neighbors = len(neighbors)
        if amount_of_neighbors:
            # array of opinion differences
            differences = np.abs(opinions[agent] - opinions[neighbors])
            indices_sorted = np.argsort(differences)
            neighbors_sorted = neighbors[indices_sorted]
            opinions_sorted = opinions[neighbors_sorted]
        else:
            return 0

        # opinion update
        news_feed = opinions_sorted[:self.information_uptake]
        # the following averaging turned out to be faster then np.mean, np.average or scipy.mean
        opinion_agent = np.sum(news_feed)/len(news_feed)
        # check if the consensus condition is True, if so add 1 to self.counter, otherwise set it to 0
        if np.absolute(opinion_agent - self.opinion[agent]) < self.convergence_parameter[2]:
            self.counter += 1
        else:
            self.counter = 0
        self.opinion[agent] = opinion_agent

    def save_to_trajectory(self, current_step):
        """Saves the opinion and time array to the trajectory dict

        Parameters
        ----------
        current_step: int
            the current time step of the model

        Returns
        -------

        """

        if current_step % self.step_resolution == 0:
            self.trajectory['opinion'].append(self.opinion.copy())
            self.trajectory['time'].append(current_step)
        elif self.consensus == True:
            self.trajectory['consensus'] = self.consensus
            self.trajectory['opinion'].append(self.opinion.copy())
            self.trajectory['time'].append(current_step)
        elif self.consensus == False:
            self.trajectory['consensus'] = self.consensus
            self.trajectory['opinion'].append(self.opinion.copy())
            self.trajectory['time'].append(current_step)
