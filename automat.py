import numpy as np
from random import random, randint, shuffle
from matplotlib import pyplot as plt
from state import State
import random
from style import palette

DIM = 100


class Cell:
    """
    This class defines a cell in the automata, which is a place-holder for a
    Person. One can put a person in the cell,and check if the cell is empty.
    """

    def __init__(self):
        self.person = None

    def put(self, person):
        self.person = person

    def get(self):
        return self.person

    def is_empty(self):
        return True if self.person is None else False


class Person:
    def __init__(self, skepticism, i, j, L):
        self.skepticism = skepticism
        self.has_rumor = False
        self.received_rumor_from = 0
        self.generations_since_transmission = np.inf
        self.pos = (i, j)
        self.L = L
        self.is_spreading = False

    def set_has_rumor(self):
        if self.has_rumor:
            self.has_rumor = False
        else:
            self.has_rumor = True

    def spread_rumor(self, grid):
        if self.generations_since_transmission < self.L:
            self.generations_since_transmission += 1
            return
        next_generation_rumor_spreaders = []
        for neighbor in self.get_neighbors(grid):
            neighbor.received_rumor_from += 1
            if neighbor.skepticism == "S4":
                continue
            elif neighbor.skepticism == "S3":
                if neighbor.received_rumor_from < 2 and random.random() < 1 / 3:
                    next_generation_rumor_spreaders.append(neighbor)
                    neighbor.generations_since_transmission = 0
                elif neighbor.received_rumor_from >= 2 and random.random() < 2 / 3:
                    next_generation_rumor_spreaders.append(neighbor)
                    neighbor.generations_since_transmission = 0
                else:
                    neighbor.generations_since_transmission += 1
            elif neighbor.skepticism == "S2":
                if neighbor.received_rumor_from < 2 and random.random() < 2 / 3:
                    next_generation_rumor_spreaders.append(neighbor)
                    neighbor.generations_since_transmission = 0
                elif neighbor.received_rumor_from >= 2:
                    next_generation_rumor_spreaders.append(neighbor)
                    neighbor.generations_since_transmission = 0
                else:
                    neighbor.generations_since_transmission += 1
            elif neighbor.skepticism == "S1":
                next_generation_rumor_spreaders.append(neighbor)
                neighbor.generations_since_transmission = 0
        for rumor_spreader in next_generation_rumor_spreaders:
            rumor_spreader.has_rumor = True
            rumor_spreader.is_spreading = True
        self.is_spreading = False

    def get_neighbors(self, grid):
        position = self.pos
        i, j = position
        neighbors = []
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                neighbor_i, neighbor_j = i + di, j + dj
                if neighbor_i < 0 or neighbor_i >= DIM or \
                        neighbor_j < 0 or neighbor_j >= DIM:
                    continue
                if grid[neighbor_i][neighbor_j].get() is not None:
                    neighbors.append(grid[neighbor_i][neighbor_j].get())
        return neighbors


class CellularAutomaton:
    """
    This class implements the required cellular automata
    """

    def __init__(self, app):
        """
        Automata's constructor. An automata object contains a state, a pointer
        to the containing App object, dimensions, parameters, a grid as a 2d
        list, a list of creatures in the automata and a list named "trand" that
        stores the number of infected creatures in each generation.
        :param app: a pointer to the containing App object.
        :return: Automata object.
        """

        # Basic attributes.
        self.state = State()
        self.generation = 0
        self.app = app

        # Experiment's parameters -- initializes later by set() function.
        self.p = 0.0
        self.l = 0
        self.s1 = 0.0
        self.s2 = 0.0
        self.s3 = 0.0
        self.s4 = 0.0
        self.gen_limit = 0
        self.infected_persons = 0
        self.n_persons = 0

        # Data-structures.
        self.grid = []  # Provides a way for cell occupancy check.
        self.persons = []  # Traversing creatures is faster than cells.
        self.trand = []  # Store number of infected in each generation.

    def __advance(self):
        """
        This method defines the changes taking place in the transition between
        two generations in the automata.
        :return: None, but it updates attributes and frame.
        """

        # Advance generation.
        self.generation += 1

        # Clear canvas.
        self.app.frame.delete('all')

        # Create a new rectangle for each person according to state and type.
        for person in self.persons:

            # Select color.
            if person.has_rumor:
                color = palette.red
            else:
                color = palette.orange

            i, j = person.pos
            x0 = i*8
            y0 = j*6
            x1 = (i + 1)*8
            y1 = (j + 1)*6
            self.app.frame.create_rectangle(x0, y0, x1, y1, fill=color)

        # Update each creature's infection and position.
        count_infected = 0
        for person in self.persons:
            if person.has_rumor:
                count_infected += 1

        # Update the number of infected creatures.
        self.infected_persons = count_infected
        for person in self.persons:
            if person.is_spreading:
                person.spread_rumor(self.grid)

    def __update_info(self):
        """
        This private method updates information entries in the app.
        :return: None.
        """
        self.app.generation.delete(0, 'end')
        self.app.generation.insert(0, self.generation)
        self.app.h_rumor.delete(0, 'end')
        self.app.h_rumor.insert(0, self.infected_persons)
        self.app.distribution.delete(0, 'end')
        dist = str(int((self.infected_persons / self.n_persons) * 100)) + '%'
        self.app.distribution.insert(0, dist)

    def __loop(self):
        """
        This private method implements the simulation itself. It updates
        entries, save current number of infected, advance the automata, and then
        schedule an async call to itself to the next 100 milliseconds (using
        Tkinter), if there is no generation limitation.
        :return: None.
        """
        if self.state.is_running:
            self.__update_info()
            self.trand.append(self.infected_persons)
            self.__advance()
            if self.generation <= self.gen_limit:
                self.app.after(100, self.__loop)
            else:
                self.app.stop_btn_action()

    def plot(self):
        """
        This private method creates a plot and show it.
        :return: None, but it outputs a plot.
        """
        plt.figure()
        plt.title('Number of persons who heard the rumor per generation')
        plt.xlabel('Generation')
        plt.ylabel('percentage of listeners')
        percentage = [(x * 100) / len(self.persons) for x in self.trand]
        plt.plot([i+1 for i in range(len(self.trand))], percentage)
        print(len(self.trand))
        plt.show()
        # save the plot into a csv file
        with open('plot.csv', '+a') as f:
            f.write('Generation, Got the rumor (number of persons) \n')
            for i in range(len(self.trand)):
                f.write(str(i) + ',' + str(self.trand[i]) + '\n')

    def set(self, P, L, S1, S2, S3, S4, GL):
        """
        :param N: Number of creatures in the experiment.
        :param D: Fraction of N of infected creatures at the start state.
        :param X: Healing time by number of generations (i.e., days).
        :param R: Fraction of N of quick creatures.
        :param P_high: High infection probability.
        :param P_low: Low infection probability.
        :param T: The threshold to change between probabilities.
        :param L: Generation limit (zero means no limitation).
        :return: None, but it initializes attributes.
        """

        # Set parameters.
        self.p = P
        self.l = L
        self.s1 = S1
        self.s2 = S2
        self.s3 = S3
        self.s4 = S4
        self.gen_limit = GL
        self.n_persons = int(DIM * DIM * P)

        # Initialize a grid.
        self.grid = [[Cell() for j in range(DIM)] for i in range(DIM)]

        # Select random positions.
        positions = [(i, j) for j in range(DIM) for i in range(DIM)]
        shuffle(positions)
        positions = positions[:self.n_persons]

        probabilities = [self.s1, self.s2, self.s3, self.s4]
        skepticism = ""
        # Create and place persons.
        for (i, j) in positions:
            type_of_person = random.choices(range(1, 5), weights=probabilities)[0]
            if type_of_person == 1:
                skepticism = "S1"
            elif type_of_person == 2:
                skepticism = "S2"
            elif type_of_person == 3:
                skepticism = "S3"
            elif type_of_person == 4:
                skepticism = "S4"

            person = Person(skepticism, i, j, L)
            self.grid[i][j].put(person)
            self.persons.append(person)

        chosen = self.persons
        shuffle(chosen)
        spreader = chosen[0]
        spreader.set_has_rumor()
        spreader.spread_rumor(self.grid)

    def run(self):
        """
        This method make the simulation running.
        :return: None.
        """
        self.state.set_running()
        self.app.after(0, self.__loop)

    def pause(self):
        """
        This method pauses the simulation, in such way that the user can resume
        the running from the point she paused it.
        :return: None.
        """
        self.state.set_paused()

    def stop(self):
        """
        This method stops the simulation running.
        :return: None.
        """
        self.app.frame.delete('all')
        self.state.set_stopped()
        self.plot()
        self.grid = []
        self.persons = []
        self.trand = []
        self.generation = 0
        self.infected_persons = 0
