import numpy as np
from random import random, randint, shuffle
from matplotlib import pyplot as plt
from state import State
from style import palette

DIM = 100


class Person:
    def __init__(self, skepticism):
        self.skepticism = skepticism
        self.has_rumor = False
        self.received_rumor_from = 0
        self.generations_since_transmission = np.inf


class RumorSpreader:
    def __init__(self, grid, transmission_prob, L):
        self.grid = grid
        self.transmission_prob = transmission_prob
        self.last_generation_transmitter = None
        self.L = L

    def create_rumor(self):
        self.last_generation_transmitter = None
        random_person = random.choice(self.grid)
        random_person.has_rumor = True

    def spread_rumor(self):
        next_generation_rumor_spreaders = []
        for person in self.grid:
            if person.has_rumor:
                for neighbor in self.get_neighbors(person):
                    if not neighbor.has_rumor:
                        neighbor.received_rumor_from += 1
                        if neighbor.skepticism == "S4":
                            continue
                        elif neighbor.skepticism == "S3":
                            if neighbor.received_rumor_from >= 2 and random.random() < 1/3:
                                neighbor.skepticism = "S2"
                                next_generation_rumor_spreaders.append(neighbor)
                            else:
                                neighbor.has_rumor = True
                                neighbor.generations_since_transmission = 0
                        elif neighbor.skepticism == "S2":
                            if neighbor.received_rumor_from >= 2 and random.random() < 2/3:
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

    def update(self):
        for person in self.grid:
            if person.generations_since_transmission < self.L:
                person.generations_since_transmission += 1
            else:
                person.has_rumor = False
                person.received_rumor_from = 0
                person.last_generation_transmitter = None

    def get_neighbors(self, person):
        i, j = self.get_person_index(person)
        neighbors = []
        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                neighbor_i, neighbor_j = i + di, j + dj
                if neighbor_i < 0 or neighbor_i >= len(self.grid) or \
                   neighbor_j < 0 or neighbor_j >= len(self.grid[0]):
                    continue
                neighbors.append(self.grid[neighbor_i][neighbor_j])
        return neighbors

    def get_person_index(self, person):
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] is person:
                    return i, j


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

    def set(self, P, L, S1, S2, S3, S4):
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





















# class CellularAutomaton:
#     def __init__(self, master):
#         self.master = master
#         master.title("Spreading Rumours")
#
#         # Parameters
#         self.P = 0.5
#         self.S4_percentage = 0.1
#         self.S3_percentage = 0.3
#         self.S2_percentage = 0.3
#         self.S1_percentage = 0.3
#         self.transmission_prob = 0.5
#         self.L = 3
#         self.num_generations = 50
#
#         # Grid display
#         self.grid_display = tk.Canvas(master, width=800, height=800)
#         self.grid_display.pack(side=tk.LEFT)
#
#         # Stats display
#         self.stats_display = tk.Frame(master, width=400, height=800)
#         self.stats_display.pack(side=tk.RIGHT)
#
#         # Create grid of people
#         self.grid = self.create_grid()
#
#         # Create RumorSpreader object
#         self.rumor_spreader = RumorSpreader(self.grid, self.transmission_prob)
#
#         # Draw initial grid
#         self.draw_grid()
#
#         # Create stats labels
#         self.create_stats_labels()
#
#         # Start simulation
#         self.start_simulation()
#
#     def create_grid(self):
#         """
#         Creates a grid of Person objects with the specified parameters.
#         """
#         grid = []
#         num_people = 800 // 16
#         for i in range(num_people):
#             row = []
#             for j in range(num_people):
#                 skepticism = self.get_skepticism()
#                 person = Person(skepticism)
#                 row.append(person)
#             grid.append(row)
#         return grid
#
#     def get_skepticism(self):
#         """
#         Randomly generates a skepticism level for a person based on the specified
#         percentages.
#         """
#         r = random.random()
#         if r < self.S4_percentage:
#             return "S4"
#         elif r < self.S4_percentage + self.S3_percentage:
#             return "S3"
#         elif r < self.S4_percentage + self.S3_percentage + self.S2_percentage:
#             return "S2"
#         else:
#             return "S1"
#
#     def draw_grid(self):
#         """
#         Draws the grid of people on the canvas.
#         """
#         self.grid_display.delete("all")
#         for i in range(len(self.grid)):
#             for j in range(len(self.grid[0])):
#                 x1 = j * 16
#                 y1 = i * 16
#                 x2 = x1 + 16
#                 y2 = y1 + 16
#                 person = self.grid[i][j]
#                 color = self.get_color(person)
#                 self.grid_display.create_rectangle(x1, y1, x2, y2, fill=color)
#
#     def get_color(self, person):
#         """
#         Returns the color for a person based on their skepticism level and whether
#         they have the rumor or not.
#         """
#         if person.has_rumor:
#             return "red"
#         elif person.skepticism == "S4":
#             return "black"
#         elif person.skepticism == "S3":
#             return "blue"
#         elif person.skepticism == "S2":
#             return "green"
#         else:
#             return "gray"
#
#     def create_stats_labels(self):
#         """
#         Creates the labels to display simulation stats.
#         """
#         tk.Label(self.stats_display, text="Simulation Parameters").pack()
#         tk.Label(self.stats_display, text=f"P = {self.P}").pack()
#         tk.Label(self.stats_display, text=f"S4 percentage = {self.S4_percentage}").pack()
#         tk.Label(self.stats_display, text= f"S3 percentage = {self.S3_percentage}").pack()
#         tk.Label(self.stats_display, text=f"S2 percentage = {self.S2_percentage}").pack()
#         tk.Label(self.stats_display, text=f"S1 percentage = {self.S1_percentage}").pack()
#         tk.Label(self.stats_display, text=f"Transmission probability = {self.transmission_prob}").pack()
#         tk.Label(self.stats_display, text=f"L = {self.L}").pack()
#         tk.Label(self.stats_display, text=f"Number of generations = {self.num_generations}").pack()
#         tk.Label(self.stats_display, text="Simulation Stats").pack()
#         self.generation_label = tk.Label(self.stats_display, text="Generation: 0")
#         self.generation_label.pack()
#         self.infected_label = tk.Label(self.stats_display, text="Infected: 0")
#         self.infected_label.pack()
#         self.recovered_label = tk.Label(self.stats_display, text="Recovered: 0")
#         self.recovered_label.pack()
#
#     def start_simulation(self):
#         """
#         Starts the simulation and updates the grid and stats display for each generation.
#         """
#         for generation in range(1, self.num_generations + 1):
#             self.rumor_spreader.spread_rumor(self.P, self.L)
#             self.update_grid()
#             self.update_stats(generation)
#             self.master.update()
#             time.sleep(0.05)
#
#     def update_stats(self, generation):
#         """
#         Updates the simulation stats displayed on the GUI for each generation.
#         """
#         num_infected = self.rumor_spreader.get_num_infected()
#         num_recovered = self.rumor_spreader.get_num_recovered()
#         self.generation_label.config(text=f"Generation: {generation}")
#         self.infected_label.config(text=f"Infected: {num_infected}")
#         self.recovered_label.config(text=f"Recovered: {num_recovered}")
#
#     def update_grid(self):
#         """
#         Updates the grid display for each generation.
#         """
#         for i in range(len(self.grid)):
#             for j in range(len(self.grid[0])):
#                 person = self.grid[i][j]
#                 color = self.get_color(person)
#                 self.grid_display.itemconfig(self.grid_rects[i][j], fill=color)
#
#     def reset_simulation(self):
#         """
#         Resets the simulation to its initial state.
#         """
#         self.grid = self.create_grid()
#         self.rumor_spreader = RumorSpreader(self.grid, self.transmission_prob)
#         self.draw_grid()
#         self.update_stats(0)



