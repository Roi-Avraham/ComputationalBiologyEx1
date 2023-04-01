from matplotlib import pyplot as plt
from random import random, randint, shuffle
from state import State
from style import palette


DIM = 100


class Cell:
    """
    This class defines a cell in the automatai, which is a place-holder for a
    person. One can put a person in the cell, remove a person from it and
    check if the cell is empty.
    """

    def __init__(self):
        self.person = None

    def put(self, person):
        self.person = person

    def get(self):
        return self.person

    def clear(self):
        self.person = None

    def is_empty(self):
        return True if self.person is None else False


class Person:
    """
    This class defines a creature in the automata. A creature can be a fast
    creature (moves ten steps each generation) or regular one (moves one step at
    a time). A creature can be in one of two states - infected or healthy. If
    the creature have an infected neighbor, there is a probability that he will
    be infected by it. Infection takes a given number of generations. In
    addition, a creature knows its position on a grid for performance reasons.
    """

    def __init__(self, i, j):
        """
        Creature's constructor.
        :param i: creature's i-position in a grid.
        :param j: creature's j-position in a grid.
        :return: Creature object.
        """
        self.steps = 1
        self.rumor = 0
        self.pos = (i, j)

    def move(self, grid):
        """
        Changes the creature's position attribute and position in the grid. This
        method avoid collisions, i.e., avoid placing a creature in an occupied
        cell. In this case, the method tries 5 times to draw a new random
        position with a uniform probability (out of the 9 options) and if it
        does not succeed, it leaves the creature in its position.
        :param grid: the grid of the automata.
        :return: None, but it changes pos attribute and the grid.
        """
        i, j = self.pos
        for _ in range(5):
            di, dj = randint(-1, 1), randint(-1, 1)
            new_i = (i + di * self.steps) % DIM
            new_j = (j + dj * self.steps) % DIM
            if new_i == i and new_j == j:
                break
            if grid[new_i][new_j].is_empty():
                self.pos = (new_i, new_j)
                grid[new_i][new_j].put(self)
                grid[i][j].clear()
                break

    def infect(self, grid, probability, healing_time):
        """
        This method is the creature state's update rule. If the creature have an
        infected neighbor, it will be infected by it in the given probability.
        :param grid: the grid of the automata.
        :param probability: probability of infection.
        :param healing_time: number of generation for illness.
        :return: None, but it changes attributes.
        """

        # If the creature is healthy, then check if it needs to be infected.
        if self.infection < 1:

            # Traverse its neighbor cells.
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if x == 0 and y == 0:
                        continue
                    ni = (self.pos[0] + x) % DIM  # Wrap-around.
                    nj = (self.pos[1] + y) % DIM  # Wrap-around.
                    neighbor = grid[ni][nj].creature

                    # If there is a neighbor, infect at the given probability.
                    if neighbor is not None and neighbor.infection > 0:
                        if random() < probability:
                            self.infection = healing_time
                            break

        # Otherwise, an infected creature can not be infected again and its
        # infection counter needs to be shortened by one generation.
        else:
            self.infection -= 1


class Automatai:
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
        self.n_creatures = 0
        self.n_quick = 0
        self.n_infected = 0
        self.healing_time = 0
        self.high_prob = 0.0
        self.low_prob = 0.0
        self.threshold = 0.0
        self.gen_limit = 0

        # Data-structures.
        self.grid = []  # Provides a way for cell occupancy check.
        self.creatures = []  # Traversing creatures is faster than cells.
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

        # Create a new rectangle for each creature according to state and type.
        for c in self.creatures:

            # Select color.
            if c.infection > 0:
                if c.steps == 10:
                    color = palette.red
                else:
                    color = palette.orange
            elif c.steps == 10:
                color = palette.cyan
            else:
                color = palette.white

            # Find new position.
            i, j = c.pos
            x0 = i * 4
            y0 = j * 4
            x1 = (i + 1) * 4
            y1 = (j + 1) * 4
            self.app.frame.create_rectangle(x0, y0, x1, y1, fill=color)

        # Choose probability according to threshold.
        p = self.high_prob if self.n_infected < self.threshold else self.low_prob

        # Update each creature's infection and position.
        count_infected = 0
        for c in self.creatures:
            c.infect(self.grid, p, self.healing_time)
            if c.infection > 0:
                count_infected += 1
            c.move(self.grid)

        # Update the number of infected creatures.
        self.n_infected = count_infected

    def __update_info(self):
        """
        This private method updates information entries in the app.
        :return: None.
        """
        self.app.generation.delete(0, 'end')
        self.app.generation.insert(0, self.generation)
        self.app.n_infected.delete(0, 'end')
        self.app.n_infected.insert(0, self.n_infected)
        self.app.distribution.delete(0, 'end')
        dist = str(int((self.n_infected / self.n_creatures) * 100)) + '%'
        self.app.distribution.insert(0, dist)
        self.app.capacity.delete(0, 'end')
        if self.threshold > 0:
            cap = str(int((self.n_infected / self.threshold) * 100)) + '%'
        else:
            cap = 'inf'
        self.app.capacity.insert(0, cap)

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
            self.trand.append(self.n_infected)
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
        plt.title('Number of infected creatures per generation')
        plt.xlabel('Generation')
        plt.ylabel('Infected')
        plt.plot(list(range(len(self.trand))), self.trand)
        plt.show()

    def set(self, N, D, X, R, P_high, P_low, T, L):
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
        self.n_creatures = N
        self.n_quick = int(R * N)
        self.n_infected = int(D * N)
        self.healing_time = X
        self.high_prob = P_high
        self.low_prob = P_low
        self.threshold = int(T * N)
        self.gen_limit = L

        # Initialize a grid.
        self.grid = [[Cell() for j in range(DIM)] for i in range(DIM)]

        # Select random positions.
        positions = [(i, j) for j in range(DIM) for i in range(DIM)]
        shuffle(positions)
        positions = positions[:self.n_creatures]

        # Create and place creatures.
        for (i, j) in positions:
            c = Person(i, j)
            self.grid[i][j].put(c)
            self.creatures.append(c)

        # Select n_infected random creatures and make them infected.
        chosen = self.creatures
        shuffle(chosen)
        chosen = chosen[:self.n_infected]
        for c in chosen:
            c.infection = self.healing_time

        # Select n_quick random creatures and set their steps attribute to 10.
        chosen = self.creatures
        shuffle(chosen)
        chosen = chosen[:self.n_quick]
        for c in chosen:
            c.steps = 10

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
        self.creatures = []
        self.trand = []
        self.generation = 0
