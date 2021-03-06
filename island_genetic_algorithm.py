"""
  island_genetic_algorithm.py :   This file contains the island implementation of Genetic Algorithm.
  File created by             :   Shashank Goyal
  Last commit done by         :   Shashank Goyal
  Last commit date            :   30th October 2020
"""

# ThreadPoolExecutor and as_completed to run routines in parallel and get the result when it completes
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle 
import time
"""
Note: 	Here, the ThreadPoolExecutor is used and not ProcessPoolExecutor because 
        we can not use any objects that is not picklable and using the later
        results in pickling error.
"""

# numpy module for using genetic operations
import numpy as np
# tqdm module for progress bar
from tqdm import tqdm

# import knapsack object
from generate_data import Knapsack
# import the GeneticAlgorithm class to be inherited
from standard_genetic_algorithm import GeneticAlgorithm


def get_genome_sequence(code: int, padding: int):
    """
    This method is used to convert a base-10 number to its
    base-2 representation as an array.

    Args:
        code (int)      : It is the base-10 number to be converted.
        padding (int)   : It is the length of the array representation.

    Examples:
        >>> get_genome_sequence(7,2)
        array([1, 1, 1])
        >>> get_genome_sequence(7,3)
        array([1, 1, 1])
        >>> get_genome_sequence(7,4)
        array([0, 1, 1, 1])
        >>> get_genome_sequence(7,5)
        array([0, 0, 1, 1, 1])

    Returns:
        np.ndarray  : Array containing 0s and 1s representing base-2 of the `code`.
    """
    return np.array([int(x) for x in np.binary_repr(code, padding)])


def get_genome_value(genome: np.ndarray):
    """
    This method converts a numpy array (of zeros and ones) from base-2
    to corresponding base-10 value.

    Args:
        genome (np.ndarray) : The array containing sequence of 0s and 1s.

    Examples:
        >>> get_genome_value(np.array([1,1,0]))
        6
        >>> get_genome_value(np.array([1,0,0]))
        4
        >>> get_genome_value(np.array([0,1,0,0]))
        4
        >>> get_genome_value(np.array([0,0,1,0,0]))
        4

    Returns:
        int : Base-10 value of the `genome` array.
    """
    return int('0b' + ''.join([str(i) for i in genome.tolist()]), 2)


def fitness_func(code: int, knapsack_obj: Knapsack):
    """
    This method calculates the profit that can be achieved for a specific genome
    and returns it as the fitness of the genome.

    Args:
        code (int)               : It is the base-10 genome value.
        knapsack_obj (Knapsack)  : It is the object containing the vectors for the problem.

    Returns:
        int : Total profit value, if the weight load can be taken else `np.NINF`.
    """
    # get genome sequence
    genome = get_genome_sequence(code, knapsack_obj.n)
    # check if total load of genome fits in capacity
    if np.dot(genome, knapsack_obj.weights) <= knapsack_obj.capacity:
        # return the profit
        return np.dot(genome, knapsack_obj.values)
    # return Negative Infinity 
    return np.NINF


class IslandGeneticAlgorithm(GeneticAlgorithm):
    """Class to implement Island Genetic Algorithm.

    Attributes:
        inherited from super() class

    """

    def __init__(self, *args, **kwargs):
        """Initialization for Class.

        Args:
            *args       : Variable length argument list.
            **kwargs    : Arbitrary keyword arguments.

        """
        # set kwargs as super() attributes.
        super().__init__(*args, **kwargs)
        # set kwargs as instance attributes.
        super().__dict__.update(kwargs)

    def crossover_mutation(self, population: np.ndarray):
        """Generate the new generation after crossover and performs mutations.

        It is a combination of the `crossover` and `mutation` from the super class
        in order to make it easier to parallelize without too much branching.

        Args:
            population  : input population.

        Returns:
            np.ndarray  : initial population along with the new mutated generation.
        """
        # perform crossover
        population = self.crossover(population)
        # perform mutation
        population = self.mutation(population)
        # return the new generation and initial population after removing the repetitions
        return population

    def driver(self, selection_percentage: float, k_parallel: int = 5):
        """The driver method for the Island Genetic Algorithm.

        Args:
            selection_percentage	: percentage of population allowed to move to next step.
            k_parallel    			: number of parallel sub genetic algorithms routines.

        Returns:
            int : genome value of the winner genome
        """
        # empty list for all the winners throughout the cycles
        winner_genomes = []
        # iterate through the cycles
        for _ in tqdm(range(self.cycle), leave=False):
            # create initial population
            population = self.init_population()
            # loop until only one element is left in the population
            while len(population) > 1:
                # sanity precaution
                if selection_percentage * len(population) <= 1:
                    # only store the individual with the max fitness score
                    population = [max(population, key=lambda g: self.fitness_func(g))]
                    # break loop
                    break
                # select the top selection_percentage
                population = self.selection(population, selection_percentage)
                # parallelizing using ThreadPoolExecutor
                with ThreadPoolExecutor() as executor:
                    # add the driver method along with arguments to k_parallel future instances
                    futures = [executor.submit(self.crossover_mutation, population) for _ in range(k_parallel)]
                    # initialize population as empty array
                    population = np.array([], dtype=int)
                    # as each sub routine is completed
                    for f in as_completed(futures):
                        # stack horizontally over the population
                        population = np.hstack((population, f.result()))
                # remove repetitions
                population = np.unique(population)
            # add the winner genome of this cycle to the list
            winner_genomes.append(population[0])
        # choose the winner based on the maximum fitness scores out of the various winners
        best_genome = max(winner_genomes, key=lambda g: self.fitness_func(g))
        # return the winner value
        return best_genome



    # load the knapsack object from the file
if __name__ == "__main__":
    # name of file to load contents from
    fname = "./values/15_values.json"
    # load the knapsack object from the file
    knapsack_object = Knapsack(15, json_fname=fname)
    # convert knapsack vectors to numpy arrays
    knapsack_object.to_numpy()
    # values for the genetic algorithm instance
    genetic_algo_data = {
        'cycle': 20,
        'genome_size': knapsack_object.n,
        'init_pop_size': knapsack_object.n ** 2,
        'crossover_scheme': GeneticAlgorithm.UNIFORM_CROSSOVER,
        'mutation_scheme': GeneticAlgorithm.BIT_FLIP_MUTATION,
        'fitness_func': lambda genome: fitness_func(genome, knapsack_object),
        'seed_range': (0, 2 ** knapsack_object.n - 1),
        'encode': get_genome_value,
        'decode': lambda genome: get_genome_sequence(genome, knapsack_object.n)
    }

    # create an object
    ga = IslandGeneticAlgorithm(**genetic_algo_data)
    # run the driver method
    winner_genome = ga.driver(0.05, 10)
    # print the results
    print("Sequence: {}\nGenome Value: {}\nProfit: {}\nCapacity Used: {}".format
          (get_genome_sequence(winner_genome, knapsack_object.n),
           winner_genome,
           fitness_func(winner_genome, knapsack_object),
           np.dot(get_genome_sequence(winner_genome, knapsack_object.n), knapsack_object.weights)))
