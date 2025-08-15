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
import numpy as np
import os

@pytest.fixture(autouse=True)
def configure():

    global joint, members, questions, answers

    # Pre-test setup
    members = Members()
    for i in range(90):
        members.addMember(Member())

    questions = Questions()
    questions.addQuestion(Question("Question #0", 2))
    questions.addQuestion(Question("Question #1", 3))
    questions.addQuestion(Question("Extra Question #2", 4))

    answers = Answers()
    for i, member in enumerate(members):
        for question in questions:
            answers.addAnswer(Answer(member.uuid, question.uuid, i % len(question.responses) + 1))

    joint = Joint(members, questions, answers)

    # Run the test
    yield

    # Post-test Teardown
    pass

def test_joint():
    
    global joint

    print("\njoint:\n", joint.matrix)

    expected =  [[[0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0]],
                 [[0, 0, 0, 0, 0],
                  [0, 8, 0, 7, 0],
                  [0, 8, 0, 7, 0],
                  [0, 7, 0, 8, 0]],
                 [[0, 0, 0, 0, 0],
                  [0, 0, 7, 0, 8],
                  [0, 0, 8, 0, 7],
                  [0, 0, 8, 0, 7]]]

    assert (joint.matrix == expected).all()

def test_dim_sum():

    global joint

    print("\n joint.dim_sum(0):\n", joint.dim_sum(0))
    print("\n joint.dim_sum(1):\n", joint.dim_sum(1))

    assert (joint.dim_sum(0) == [0, 45, 45]).all()
    assert (joint.dim_sum(1) == [0, 30, 30, 30]).all()

def test_Pr_A():

    global joint

    question0 = joint.questions.questions[0]
    question1 = joint.questions.questions[1]

    print("\njoint.Pr_A(question1):\n", joint.Pr_A(question1.uuid))

    assert np.allclose(joint.Pr_A(question0.uuid), [0., 1/2, 1/2])
    assert np.allclose(joint.Pr_A(question1.uuid), [0., 1/3, 1/3, 1/3])

    assert np.allclose(joint.Pr_A_normalized(question1.uuid), [1/3, 1/3, 1/3])
    assert np.isclose(joint.Pr_A_normalized(question1.uuid, 0), 1/3)
    
def test_Pr_AB():

    global joint

    question0 = joint.questions.questions[0]
    question1 = joint.questions.questions[1]

    print("\njoint.Pr_AB(question0, question1):\n", joint.Pr_AB(question0.uuid, question1.uuid))

    expected =  [[0.,  0.,  0.,  0.],
                 [0.,  1/6, 1/6, 1/6],
                 [0.,  1/6, 1/6, 1/6]]
    
    assert np.allclose(joint.Pr_AB(question0.uuid, question1.uuid), expected)

def test_Pr_AgB():

    global joint

    question0 = joint.questions.questions[0]
    question1 = joint.questions.questions[1]

    print("\njoint.Pr_AgB(question0, question1):\n", joint.Pr_AgB(question0.uuid, question1.uuid))

    expected = [[0.0, 0.0, 0.0, 0.0],
                [0.0, 1/2, 1/2, 1/2],
                [0.0, 1/2, 1/2, 1/2]]

    assert np.allclose(joint.Pr_AgB(question0.uuid, question1.uuid), expected)

def test_saveLoad():

    global joint

    joint.save('test.json')
    joint2 = Joint()
    joint2.load('test.json')

    for i in range(len(joint.questions.questions)):
        assert joint.questions.questions[i].uuid == joint2.questions.questions[i].uuid
        assert joint.questions.questions[i].responses == joint2.questions.questions[i].responses

    assert (joint.matrix == joint2.matrix).all()
    
def test_is_independent():
    
    global joint

    question0 = joint.questions.questions[0]
    question1 = joint.questions.questions[1]

    assert joint.is_independent(question0.uuid, question1.uuid) == True