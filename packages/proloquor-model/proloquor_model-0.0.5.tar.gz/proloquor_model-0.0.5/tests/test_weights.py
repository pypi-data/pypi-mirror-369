import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

import logging
import pytest
import copy
import numpy as np
from proloquor_model.members import Member
from proloquor_model.members import Members
from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from proloquor_model.answers import Answer
from proloquor_model.answers import Answers
from proloquor_model.joint import Joint
from proloquor_model.vector import Vector
from proloquor_model.weights import Weights
from . import environment

@pytest.fixture(autouse=True)
def configure():

    logging.basicConfig(level=logging.INFO)

    # Pre-test setup
    global population_members, questions, population_answers, membership_members, membership_answers
    
    population_members = environment.create_population_members(size=8000)
    questions = environment.create_questions()
    population_answers = environment.create_population_answers(population_members, questions)
    
    membership_members = environment.create_membership_members(population_members, questions, population_answers)
    membership_answers = environment.create_membership_answers(membership_members, questions, population_answers)

    # Run the test
    yield

    # Post-test Teardown
    pass

def test_minimize():
    questionA = questions.questions[0]
    questionB = questions.questions[1]
    questionC = questions.questions[2]
    population_joint = Joint(population_members, questions, population_answers)

    weighted_members = copy.deepcopy(membership_members)
    weights = Weights(weighted_members, questions, membership_answers)
    weights.add_foundational_question(questionA, population_joint.Pr_A_normalized(questionA.uuid))
    weights.add_foundational_question(questionB, population_joint.Pr_A_normalized(questionB.uuid))
    weights.minimize()

    weighted_joint = Joint(weighted_members, questions, membership_answers)
    membership_joint = Joint(membership_members, questions, membership_answers)

    success = run = 0
    for question in questions:
        vector = Vector(weighted_members, question, membership_answers)
        print(f"\n{question.description}: ")
        print(f"Population: {population_joint.Pr_A_normalized(question.uuid)}")
        print(f"Membership: {membership_joint.Pr_A_normalized(question.uuid)}")
        print(f"Weighted:   {weighted_joint.Pr_A_normalized(question.uuid)}")
        for response in question.responses:
            ci = vector.confidence_interval(response, 0.95)
            run += 1
            print(f"{population_joint.Pr_A_normalized(question.uuid, response):.5f} -> {vector.mean(response):.5f} \u00b1 {vector.margin_of_error(response, 0.95):.5f} ({ci[0]:.5f}, {ci[1]:.5f}) ", end="")
            if ci[0] < population_joint.Pr_A_normalized(question.uuid, response) < ci[1]:
                success += 1
                print("PASS")
            else:
                print("FAIL")
    assert success/run >= 0.75 # at least 9/12

def test_weighting():

    questionA = questions.questions[0]
    questionB = questions.questions[1]
    population_joint = Joint(population_members, questions, population_answers)

    weighted_members = copy.deepcopy(membership_members)
    weights = Weights(weighted_members, questions, membership_answers)
    weights.add_foundational_question(questionA, population_joint.Pr_A_normalized(questionA.uuid))
    weights.add_foundational_question(questionB, population_joint.Pr_A_normalized(questionB.uuid))
    weights.calculate()

    weighted_joint = Joint(weighted_members, questions, membership_answers)
    membership_joint = Joint(membership_members, questions, membership_answers)

    success = run = 0
    for question in questions:
        vector = Vector(weighted_members, question, membership_answers)
        print(f"\n{question.description}: ")
        print(f"Population: {population_joint.Pr_A_normalized(question.uuid)}")
        print(f"Membership: {membership_joint.Pr_A_normalized(question.uuid)}")
        print(f"Weighted:   {weighted_joint.Pr_A_normalized(question.uuid)}")
        for response in question.responses:
            ci = vector.confidence_interval(response, 0.95)
            run += 1
            print(f"{population_joint.Pr_A_normalized(question.uuid, response):.5f} -> {vector.mean(response):.5f} \u00b1 {vector.margin_of_error(response, 0.95):.5f} ({ci[0]:.5f}, {ci[1]:.5f}) ", end="")
            if ci[0] < population_joint.Pr_A_normalized(question.uuid, response) < ci[1]:
                success += 1
                print("PASS")
            else:
                print("FAIL")
    assert success/run >= 0.75 # at least 9/12
