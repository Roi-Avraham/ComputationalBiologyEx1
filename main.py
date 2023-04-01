import random

class Person:
    def __init__(self, p, s_type):
        self.p = p
        self.s_type = s_type
        self.rumored = False

class Network:
    def __init__(self, n, p, l, s1_ratio, s2_ratio, s3_ratio):
        self.n = n
        self.p = p
        self.l = l
        self.s1_ratio = s1_ratio
        self.s2_ratio = s2_ratio
        self.s3_ratio = s3_ratio
        self.people = []
        self.rumored_count = 0
        self.generation = 0
        self.history = []
        self.initialize()

    def initialize(self):
        self.people = []
        self.rumored_count = 0
        self.generation = 0
        self.history = []
        s1_count = int(self.n * self.s1_ratio)
        s2_count = int(self.n * self.s2_ratio)
        s3_count = int(self.n * self.s3_ratio)
        s4_count = self.n - s1_count - s2_count - s3_count
        for i in range(s1_count):
            self.people.append(Person(self.p, 'S1'))
        for i in range(s2_count):
            self.people.append(Person(self.p, 'S2'))
        for i in range(s3_count):
            self.people.append(Person(self.p, 'S3'))
        for i in range(s4_count):
            self.people.append(Person(self.p, 'S4'))
        random.shuffle(self.people)

    def simulate(self):
        self.initialize()
        while self.rumored_count < self.n:
            self.generation += 1
            self.history.append(self.rumored_count)
            for i, person in enumerate(self.people):
                if person.rumored:
                    continue
                if i >= self.l:
                    neighbors = self.people[i - self.l:i]
                else:
                    neighbors = self.people[:i] + self.people[self.n - self.l + i:]
                if any(neighbor.rumored for neighbor in neighbors):
                    if random.random() < person.p:
                        person.rumored = True
                        self.rumored_count += 1
