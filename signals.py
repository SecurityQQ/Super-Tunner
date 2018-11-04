from collections import Counter
from scipy.stats import shapiro
import numpy as np
from utils import *

class Signal:
    def __init__(self, capacity):
        self.history = []
        self.capacity = capacity

    def push_note(self, freq):
        n = freq_to_number(freq)
        self.history.append((freq, n, int(round(n))))
        print(self.history[-1])
        self.pop_note()

    def pop_note(self):
        if len(self.history) > self.capacity:
            self.history.pop(0)

    def is_correct(self):
        mean, std = self.get_stats()
        # n_predicted = list(map(lambda x: x[2], self.history))
        # return len(Counter(n_predicted).keys()) < 2 and len(self.history) == self.capacity
        if len(self.history) == self.capacity:
            time_series = np.array(list(map(lambda x: x[1], self.history)))
            time_series = (time_series - mean) / std
            w, pval = shapiro(time_series)
            return pval > 0.05

    def predict_note(self):
        counted_notes = Counter(list(map(lambda x: x[2], self.history)))
        return counted_notes.most_common(1)[0]

    def get_stats(self):
        freqs = list(map(lambda x: x[1], self.history))
        mean = np.mean(freqs)
        std = np.std(freqs)
        return (mean + 1e-20), (std + 1e-20)

    def get_corrected_note(self):
        a = Counter(list(map(lambda x: x[2], self.history))).most_common(1)[0][0]
        return note_name(a)


class Commands:

    def __init__(self):
        self.commands = {}
        self.trigger_funcs = {}

    def add_command(self, time_history, label, triger_func):
        if not self.check_exists(time_history):
            print("Added a command: {}".format(label))
            self.commands[label] = np.array(time_history)
            self.trigger_funcs[label] = triger_func
            return True
        else: ## run a command
            print("Command with same freq exists")
            return False

    def trigger_command(self, time_history, payload):
        label = self.check_exists(time_history)
        if label:
            self.trigger_funcs[label](payload)


    def check_exists(self, time_history):
        arrayed_history = np.asarray(time_history)
        for k, v in self.commands.items():
            metric = self.metric(v, arrayed_history)
            print(metric)
            if metric < self.threshold():
                return k
        return False

    def metric(self, a, b):
        if a.shape != b.shape:
            print(a.shape, b.shape)
        assert a.shape == b.shape
        return np.sum(2 * (a - b) ** 2 / (a ** 2 + b ** 2))

    def threshold(self):
        return 0.2
