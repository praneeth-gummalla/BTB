from btb.selection import Selector, UCB1
from btb.bandit import ucb1_bandit
import numpy as np

# the minimum number of scores that each choice must have in order to use best-K
# optimizations. If not all choices meet this threshold, default UCB1 selection
# will be used.
K_MIN = 2


class BestKReward(Selector):
    def __init__(self, choices, **kwargs):
        """
        Needs:
            k: number of best scores to consider
        """
        super(BestKReward, self).__init__(choices, **kwargs)
        self.k = kwargs.pop('k', K_MIN)
        self.ucb1 = UCB1(choices, **kwargs)

    def select(self, choice_scores):
        """
        Keeps the choice counts intact, but only let the bandit see the top k
        learners' scores.
        """
        # if we don't have enough scores to do K-selection, fall back to UCB1
        if min([len(s) for s in choice_scores.values()]) < K_MIN:
            print 'BestK: Not enough choices to do K-selection; using UCB1'
            return self.ucb1.select(choice_scores)

        print 'BestK: using Best K bandit selection'

        # sort each list of scores in descending order, then keep the five best
        # scores and replace the rest of them with zeros.
        best_k_scores = {}
        for c, s in choice_scores.items():
            # only use choices from our set of possibilities
            if c not in self.choices:
                continue
            zeros = (len(s) - self.k) * [0]
            best_k_scores[c] = sorted(s, reverse=True)[:self.k] + zeros

        # use the bandit function to choose an arm
        return ucb1_bandit(best_k_scores)


class BestKVelocity(Selector):
    def __init__(self, **kwargs):
        """
        Needs:
            k: number of best scores to consider
        """
        super(BestKVelocity, self).__init__(choices, **kwargs)
        self.k = kwargs.get('k', K_MIN)
        self.ucb1 = UCB1(choices, **kwargs)

    def select(self, choice_scores):
        """
        Keeps the frozen set counts intact but only uses the top k learner's
        velocities over their last for usage in rewards for the bandit
        calculation
        """
        # if we don't have enough scores to do K-selection, fall back to UCB1
        if min([len(s) for s in choice_scores.values()]) < K_MIN:
            return self.ucb1.select(choice_scores)

        # sort each list of scores in descending order, then compute velocity of
        # the five best scores and pad out the list with zeros.
        best_k_velocities = {}
        for c, s in choice_scores.items():
            # only use choices from our set of possibilities
            if c not in self.choices:
                continue
            # take the k + 1 best scores so we can get k velocities
            best_scores = sorted(scores, reverse=True)[:self.k+1]
            velocities = [best_scores[i] - best_scores[i+1] for i in
                          range(len(best_scores) - 1)]
            # pad the list out with zeros, so the length of the list is
            # maintained
            zeros = (len(s) - self.k) * [0]
            best_k_velocities[c] = velocities + zeros

        return ucb1_bandit(best_k_velocities)