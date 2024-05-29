import numpy as np


def perturbByExponentialMechanism(perturbation_set, costs, epsilon=0.1):
    e_value = np.e
    probs = []
    for cost in costs:
        prob = e_value ** (-epsilon * cost)
        probs.append(prob)
    probs_array = np.array(probs)
    probs_array = probs_array / np.sum(probs_array)
    discrete_exponential_distribution = np.random.choice(len(costs), p=probs_array)
    return perturbation_set[discrete_exponential_distribution]


