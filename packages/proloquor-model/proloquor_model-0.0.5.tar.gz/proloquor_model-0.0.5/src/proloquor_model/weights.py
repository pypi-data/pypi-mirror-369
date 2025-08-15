from proloquor_model.answers import Answer
from proloquor_model.answers import Answers
from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from proloquor_model.members import Member
from proloquor_model.members import Members
from proloquor_model.joint import Joint
from scipy.optimize import minimize
import numpy as np
import warnings
import logging

class Weights:
  def __init__(self, members: Members, questions: Questions, answers: Answers):
    self.members = members
    self.questions = questions
    self.answers = answers
    self.foundational_questions = []
    self.expected = []
    self.done = []

  def add_foundational_question(self, question: Question, expected):
    self.foundational_questions.append(question)
    self.expected.append(expected)
    self.done.append(False)

  def minimize(self):
    logger = logging.getLogger(__name__)

    def objective(weights):
      for member in self.members:
        offset = 0
        weight = 1.0
        for question in self.foundational_questions:
          answer = self.answers.findAnswers(member.uuid, question.uuid)
          if answer.numAnswers() == 1:
            weight *= weights[answer.answers[0].response + offset - 1]
          else:
            weight = 0
          offset += len(question.responses)
        member.weight = weight

      joint = Joint(self.members, self.questions, self.answers)
      error = 0
      for q, question in enumerate(self.foundational_questions):
        error += np.sum((self.expected[q] - joint.Pr_A_normalized(question.uuid)) ** 2)

      logger.debug("%f: %s", error, np.round(weights, 6))
      return error
    
    weights = np.array([])

    for question in self.foundational_questions:
      weights = np.append(weights, np.ones(len(question.responses)))
    
    minimize(objective, weights, bounds=[(0.1, 10)] * len(weights), method='L-BFGS-B')

  def calculate(self):
    logger = logging.getLogger(__name__)

    joint = Joint(self.members, self.questions, self.answers)

    weights = {}
    for i in range(1, 20):
      for q, question in enumerate(self.foundational_questions):
        with warnings.catch_warnings():
          warnings.simplefilter("ignore")
          weights[question.uuid] = np.nan_to_num(self.expected[q] / joint.Pr_A_normalized(question.uuid), posinf=1.0)
        logger.debug("%-40s: %s", question.description, np.round(weights[question.uuid], 6))
        if np.isclose(np.sum(weights[question.uuid]), len(weights[question.uuid])):
          self.done[q] = True

      if np.all(self.done):
        break

      for member in self.members:
        for question in self.foundational_questions:
          member_responses = self.answers.findAnswers(member.uuid, question.uuid)
          if member_responses.numAnswers() > 0:
            member.weight *= weights[question.uuid][member_responses.answers[0].response - 1]

      joint = Joint(self.members, self.questions, self.answers)