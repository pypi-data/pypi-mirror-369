import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.members import Member
from proloquor_model.members import Members
from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from proloquor_model.answers import Answer
from proloquor_model.answers import Answers
from uuid import uuid4
import tempfile
import os

def test_answer():
    member = Member()
    question = Question("Sample Question.", 3)
    answer = Answer(member.uuid, question.uuid, 1)

    assert answer.question == question.uuid
    assert answer.uuid is not None

    uuid = uuid4()
    answer = Answer(member.uuid, question.uuid, 2, uuid)
    assert answer.uuid == uuid

def test_answers():
    questions = Questions()
    for i in range(6):
        question = questions.addQuestion(Question("Question #%d" % (i), 5))

    members = Members()
    for i in range(10):
        members.addMember(Member())

    answers = Answers()
    for question in questions:
        for m, member in enumerate(members):
            answer = answers.addAnswer(Answer(member.uuid, question.uuid, (m % 5) + 1))

    assert answers.numAnswers() == 10 * 6
    assert answers.getAnswer(answer.uuid).uuid == answer.uuid 

    assert answers.countAnswers(None) == 10 * 6    
    assert answers.countAnswers(question.uuid) == 10
    
    assert answers.countAnswers(question.uuid, 1) == 2
    assert answers.countAnswers(question.uuid, 2) == 2
    assert answers.countAnswers(question.uuid, 3) == 2
    assert answers.countAnswers(question.uuid, 4) == 2
    assert answers.countAnswers(question.uuid, 5) == 2
    assert answers.countAnswers(question.uuid, 6) == 0

def test_generateAnswer():
    members = Members()
    for i in range(100):
        members.addMember(Member())

    questions = Questions()
    question = Question("Sample Question", 4)
    questions.addQuestion(question)

    answers = Answers()
    for member in members:
        new_answer = answers.generateAnswer(member, question, [0.10, 0.20, 0.30, 0.40])
        assert new_answer.response > 0 and new_answer.response <= len(question.responses)

    assert answers.countAnswers(question.uuid, 1) < answers.countAnswers(question.uuid, 4)

def test_sampleAnswers():
    question = Question("Sample Question", 3)
    answers = Answers()
    for i in range(100):
        answers.addAnswer(Answer(uuid4(), question.uuid, 1))

    sampleAnswers = answers.sampleAnswers(0.5)
    assert sampleAnswers.numAnswers() > 0 and sampleAnswers.numAnswers() < answers.numAnswers()

    sampleAnswers = answers.sampleAnswers(0.5, question.uuid)
    assert sampleAnswers.numAnswers() > 0 and sampleAnswers.numAnswers() < answers.numAnswers()

    sampleAnswers = answers.sampleAnswers(0.5, uuid4())
    assert sampleAnswers.numAnswers() == 0

def test_saveLoad():
    filename = tempfile.NamedTemporaryFile().name
    
    answers = Answers()
    for i in range(100):
        answers.addAnswer(Answer(uuid4(), uuid4(), (i % 3) + 1))
    
    answers.save(filename)
    answers2 = Answers()
    answers2.load(filename)

    assert answers.numAnswers() == answers2.numAnswers()

    os.remove(filename)