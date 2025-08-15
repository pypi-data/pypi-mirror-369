from proloquor_model.members import Members
from proloquor_model.questions import Question
from proloquor_model.answers import Answers
from scipy.stats import chi2
import scipy.stats as stats
from math import sqrt
import numpy as np

class Vector:
    def __init__(self, members: Members, question: Question, answers: Answers, normalized = True):
        self.vector = np.zeros((members.numMembers(), len(question.responses)+1))

        for i, member in enumerate(members):
            member_answers = answers.findAnswers(member_uuid=member.uuid, question_uuid=question.uuid)
        
            num_answers = member_answers.numAnswers()
            if num_answers > 1:
                raise Exception("Invalid answers.")
            elif num_answers == 0:
                self.vector[i][0] = member.weight
            else:
                self.vector[i][member_answers.answers[0].response] += member.weight

        if normalized:
            self.vector = self.vector[self.vector[:, 0] == 0]

    def mean(self, response):
        responses = self.vector[:,response]
        # return np.mean(responses)
        return np.sum(responses) / np.sum(self.vector)
    
    def stdev(self, response, dof=1):
        responses = self.vector[:,response]
        m = self.mean(response)
        sq = np.square(responses - m)
        return np.sqrt(np.sum(sq) / (np.sum(self.vector) - dof))
        # return np.std(responses, ddof = dof)

    def margin_of_error(self, response, gamma, dof=1):
        sample_std = self.stdev(response, dof=dof)
        standard_error = sample_std/sqrt(len(self.vector))
        z = stats.norm.ppf((1 + gamma)/2.0)

        return z*standard_error

    def confidence_interval(self, response, gamma):
        responses = self.vector[:,response]
        sample_mean = np.mean(responses)
        moe = self.margin_of_error(response, gamma)

        return (self.mean(response) - moe, self.mean(response) + moe)