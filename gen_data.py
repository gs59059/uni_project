# json module used to store and load the knapsack objects in json files
import json
# choice method to select an objects from a list of objects
from random import choice

# numpy module for dot product, cumulative sum, random integer generation
import numpy as np


class Knapsack:
    """Class to represent and store Knapsack Problem Object.
    Attributes: 
        n       (int)                   : number of items in the knapsack.
        weights (np.ndarray or list)    : contains the weights vector.
        values  (np.ndarray or list)    : contains the  corresponding value vector.
        capacity (int)                  : capacity value of the knapsack.
    """

    def __init__(self, n: int, upper_seed: int = 51, json_fname: str = None):
        """Initialization for Class.
        Args:
            n           : number of items in the knapsack.
            upper_seed  : used as the upper limit on the range while generating the values.
            json_fname  : name of the file to load the knapsack object from.
        """

        # if file name is specified
        if json_fname is not None:
            # open the json file
            with open(json_fname, 'r') as json_file:
                # update the self attributes with the contents of the file
                self.__dict__ = json.load(json_file)
            # end function
            return

        # number of items
        self.n = n
        # take cumulative sum of an array of random integers to make it strictly increasing
        self.values = np.cumsum(np.random.randint(low=1, high=upper_seed, size=n))
        # take cumulative sum of an array proportional to the value vector and round off as integers
        self.weights = (np.cumsum(np.multiply(self.values, np.random.rand(n, )))).astype(np.int)
        # add weights vector to the values vector inorder to make value vector greater than weights vector
        self.values += self.weights
        # capacity is chosen as three times the weight of one of top 10 percent of the weight vectors
        self.capacity = int(3 * choice(self.weights[int(-0.1 * n):]))

        # convert values vector to list
        self.values = self.values.tolist()
        # convert weights vector to list
        self.weights = self.weights.tolist()

    def __repr__(self):
        """Implementation of `repr` dunder method.
        Returns:
            str: String representation of the class attributes.
        """
        string = "Capacity: {}\nNumber of Items: {}\nWeights: {}\nValues: {}\n".format(self.capacity,
                                                                                       self.n,
                                                                                       self.weights,
                                                                                       self.values)
        return string

    def to_numpy(self):
        """Converts the weights and values vector back to numpy arrays.
        """
        self.weights = np.array(self.weights, dtype=np.int)
        self.values = np.array(self.values, dtype=np.int)


if __name__ == "__main__":
    for items in [10,15,20,25,30]:
        # number of items
        no_of_items = items
        # upper seed
        seed = 51
        # path to save the file
        fname = str(no_of_items) + '_valuesnew.json'

        # knapsack object
        k = Knapsack(no_of_items, seed)
        # display the contents of the knapsack object
        #print(k)
        print(k.__dict__)
        print(type(k.__dict__))
        print(k.__dict__['n'])
        # create the file
        with open(fname, 'w') as file:
            # store the contents of the object in the file
            json.dump(k.__dict__, file)

        # ========================== Sanity Check ========================== 
        # load a new object with the contents of the file just created
        k_load = Knapsack(no_of_items, json_fname=fname)
    # display the contents of this loaded knapsack object
    #print(k_load)
    #print("Sanity Check Complete")
    #print(k_load.weights)