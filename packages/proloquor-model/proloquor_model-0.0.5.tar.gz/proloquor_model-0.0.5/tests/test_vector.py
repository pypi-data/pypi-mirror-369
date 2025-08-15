import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

import pytest
from proloquor_model.members import Member
from proloquor_model.members import Members
from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from proloquor_model.answers import Answer
from proloquor_model.answers import Answers
from proloquor_model.joint import Joint
from proloquor_model.vector import Vector
import numpy as np

@pytest.fixture(autouse=True)
def configure():

    global joint, members, questions, answers, sampled_answers

    # Pre-test setup
    members = Members()
    for i in range(90):
        members.addMember(Member())

    questions = Questions()
    questions.addQuestion(Question("Question #0", 2))
    questions.addQuestion(Question("Question #1", 3))
    questions.addQuestion(Question("Extra Question #2", 5))

    answers = Answers()
    for i, member in enumerate(members):
        for question in questions:
            answers.addAnswer(Answer(member.uuid, question.uuid, i % len(question.responses) + 1))

    joint = Joint(members, questions, answers)

    sampled_answers = Answers()
    for i, member in enumerate(members):
        for question in questions:
            if i % 7 != 0:
                sampled_answers.addAnswer(Answer(member.uuid, question.uuid, i % len(question.responses) + 1))

    # Run the test
    yield

    # Post-test Teardown
    pass

def test_mean():
    vector = Vector(members, questions.questions[0], answers)
    assert vector.mean(1) == np.sum(vector.vector[:,1]) / np.sum(vector.vector) == 1/2

    vector = Vector(members, questions.questions[1], answers)
    assert vector.mean(2) ==np.sum(vector.vector[:,2]) / np.sum(vector.vector) == 1/3

    vector = Vector(members, questions.questions[2], answers)
    assert vector.mean(3) == np.sum(vector.vector[:,3]) / np.sum(vector.vector) == 1/5

def test_std():
    vector = Vector(members, questions.questions[0], answers)
    assert np.isclose(vector.stdev(1), 0.5028)

def test_moe():
    vector = Vector(members, questions.questions[0], answers)
    assert np.isclose(vector.margin_of_error(1, 0.95), 0.10387788)

def test_ci():
    vector = Vector(members, questions.questions[0], answers)
    ci = vector.confidence_interval(1, 0.95)
    assert np.isclose(ci[0], 0.396122117)
    assert np.isclose(ci[1], 0.603877883)
    
def test_sample():
    vector = Vector(members, questions.questions[0], sampled_answers)
    assert np.isclose(vector.mean(1), 0.49351)
    assert np.isclose(vector.stdev(1), .50324)
    assert np.isclose(vector.margin_of_error(1, 0.95), 0.1124022)
    assert np.allclose(vector.confidence_interval(1, 0.95), (0.38110433, 0.60590866))
