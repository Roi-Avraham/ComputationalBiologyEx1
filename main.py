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
 # PART B
 def generate_population(n, p, l, s1_ratio, s2_ratio, s3_ratio, s4_ratio, cluster_size):
    population = []
    for i in range(n):
        if i % cluster_size == 0:
            # start a new cluster
            s1_count = int(s1_ratio * cluster_size)
            s2_count = int(s2_ratio * cluster_size)
            s3_count = int(s3_ratio * cluster_size)
            s4_count = int(s4_ratio * cluster_size)
            
            cluster = []
            for j in range(s1_count):
                cluster.append(Person(i+j, 'S1', []))
            for j in range(s2_count):
                cluster.append(Person(i+j+s1_count, 'S2', []))
            for j in range(s3_count):
                cluster.append(Person(i+j+s1_count+s2_count, 'S3', []))
            for j in range(s4_count):
                cluster.append(Person(i+j+s1_count+s2_count+s3_count, 'S4', []))
            
            population.extend(cluster)
        else:
            # add a random person to the previous cluster
            cluster = population[-cluster_size:]
            s1_count = sum(1 for p in cluster if p.type == 'S1')
            s2_count = sum(1 for p in cluster if p.type == 'S2')
            s3_count = sum(1 for p in cluster if p.type == 'S3')
            s4_count = sum(1 for p in cluster if p.type == 'S4')
            
            r = random.random()
            if r < s1_ratio:
                cluster.append(Person(i, 'S1', []))
            elif r < s1_ratio + s2_ratio:
                cluster.append(Person(i, 'S2', []))
            elif r < s1_ratio + s2_ratio + s3_ratio:
                cluster.append(Person(i, 'S3', []))
            else:
                cluster.append(Person(i, 'S4', []))
            
            population[-cluster_size:] = cluster
    
    return population

