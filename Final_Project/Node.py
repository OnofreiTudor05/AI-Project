import copy
import math
import numpy as np


class Node:
    def __init__(self, no, father, config):
        self.index = no
        self.father = father
        self.config = copy.deepcopy(config)
        self.score = 0.00001
        self.visited = 0.00001
        self.v = []

    def get_config(self):
        return self.config

    def get_index(self):
        return self.index

    def update_score(self, score):
        self.score += score

    def update_visit(self):
        self.visited += 1

    def add_child(self, nod):
        self.v.append(nod)

    def get_child_size(self):
        return len(self.v)

    def get_child(self, id_number):
        return self.v[id_number]

    def get_score(self):
        return self.score

    def get_visited(self):
        return self.visited

    def get_info_square(self, i, j, field):
        return self.config[i][j].info[field]

    def get_formula_value(self, n):
        return self.score / self.visited + 3. / 7. * math.sqrt(np.log(n) / self.visited)
