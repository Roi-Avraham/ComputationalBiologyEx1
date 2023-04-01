import numpy as np
from random import random, randint, shuffle
from matplotlib import pyplot as plt
from state import State
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

    def set_has_rumor(self):
        if self.has_rumor:
            self.has_rumor = False
        else:
            self.has_rumor = True


    def spread_rumor(self, grid):
        next_generation_rumor_spreaders = []
        for person in grid:
            if person.has_rumor:
                for neighbor in self.get_neighbors(person, grid):
                    if not neighbor.has_rumor:
                        neighbor.received_rumor_from += 1
                        if neighbor.skepticism == "S4":
                            continue
                        elif neighbor.skepticism == "S3":
                            if neighbor.received_rumor_from >= 2 and random.random() < 1 / 3:
                                neighbor.skepticism = "S2"
                                next_generation_rumor_spreaders.append(neighbor)
                            else:
                                neighbor.has_rumor = True
                                neighbor.generations_since_transmission = 0
                        elif neighbor.skepticism == "S2":
                            if neighbor.received_rumor_from >= 2 and random.random() < 2 / 3:
                                neighbor.skepticism = "S1"
                                next_generation_rumor_spreaders.append(neighbor)
                            else:
                                neighbor.has_rumor = True
                                neighbor.generations_since_transmission = 0
                        elif neighbor.skepticism == "S1":
                            neighbor.has_rumor = True
                            neighbor.generations_since_transmission = 0
                        neighbor.last_generation_transmitter = person
                self.last_generation_transmitter = person
        for rumor_spreader in next_generation_rumor_spreaders:
            rumor_spreader.has_rumor = True

    def update(self, grid):
        for person in grid:
            if person.generations_since_transmission < self.L:
                person.generations_since_transmission += 1
            else:
                person.has_rumor = False
                person.received_rumor_from = 0
                person.last_generation_transmitter = None

    def get_neighbors(self, person, grid):
        i, j = self.get_person_index(person, grid)
        neighbors = []
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                neighbor_i, neighbor_j = i + di, j + dj
                if neighbor_i < 0 or neighbor_i >= len(grid) or \
                        neighbor_j < 0 or neighbor_j >= len(grid[0]):
                    continue
                neighbors.append(grid[neighbor_i][neighbor_j])
        return neighbors

    def get_person_index(self, person, grid):
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] is person:
                    return i, j


# class RumorSpreader:
#     def __init__(self, grid, L):
#         self.grid = grid
#         self.last_generation_transmitter = None
#         self.L = L
#
#     def create_rumor(self):
#         self.last_generation_transmitter = None
#         random_person = random.choice(self.grid)
#         random_person.has_rumor = True


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
                color = palette.green

            # Find new position.
            i, j = person.pos
            x0 = i * 4
            y0 = j * 4
            x1 = (i + 1) * 4
            y1 = (j + 1) * 4
            self.app.frame.create_rectangle(x0, y0, x1, y1, fill=color)

        # Choose probability according to threshold.
        p = self.high_prob if self.n_infected < self.threshold else self.low_prob

        # Update each creature's infection and position.
        count_infected = 0
        for person in self.persons:
            person.infect(self.grid, p, self.healing_time)
            if person.infection > 0:
                count_infected += 1
            person.move(self.grid)

        # Update the number of infected creatures.
        self.infected_persons = count_infected

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
            if not self.gen_limit or self.generation <= self.gen_limit:
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
        plt.ylabel('Infected')
        plt.plot(list(range(len(self.trand))), self.trand)
        plt.show()

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
        self.n_persons = DIM*DIM*self.p

        # Initialize a grid.
        self.grid = [[Cell() for j in range(DIM)] for i in range(DIM)]

        # Select random positions.
        positions = [(i, j) for j in range(DIM) for i in range(DIM)]
        shuffle(positions)
        positions = positions[:self.n_persons]

        probabilities = [self.s1, self.s2, self.s3, self.s4]
        # Create and place persons.
        for (i, j) in positions:
            type_of_person = random.choices(range(1, 5), weights=probabilities)[0]
            person = Person(type_of_person, i, j, L)
            self.grid[i][j].put(person)
            self.persons.append(person)

        chosen = self.persons
        shuffle(chosen)
        spreader = chosen[0]
        spreader.set_has_rumor()

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

    # def init_simulation(self):
    #     # getting random numbers to represent the place in the matrix the cell get
    #     cells_pos = random.sample(range(self.rows * self.cols), self.number_of_persons)
    #     probabilities = [self.p_s1, self.p_s2, self.p_s3, self.p_s4]
    #     random_person = random.choice(cells_pos)
    #     for position in cells_pos:
    #         type_of_person = random.choices(range(1, 5), weights=probabilities)[0]
    #         if position == random_person:
    #             # spreading person
    #             self.create_person(position, type_of_person, INFECTED)
    #             self.infected_persons += 1
    #         else:
    #             self.create_person(position, type_of_person, NON_INFECTED)