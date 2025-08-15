import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from uuid import uuid4
import tempfile
import os

def test_question():
    question = Question("Sample Question", 3)
    assert question.uuid is not None
    assert question.description == "Sample Question"

    uuid = uuid4()
    question = Question("Another Sample Question", 4, uuid)
    assert question.uuid == uuid

def test_questions():
    questions = Questions()
    assert questions.numQuestions() == 0

    for i in range(100):
        questions.addQuestion(Question("Sample Question No. %d" % (i), 3))

    question = Question("Another Sample Question.", 4)
    questions.addQuestion(question)

    assert questions.numQuestions() == 101

    assert questions.getQuestion(question.uuid).uuid == question.uuid

def test_saveLoad():
    filename = tempfile.NamedTemporaryFile(delete=False).name

    questions = Questions()
    for i in range(100):
        questions.addQuestion(Question("Sample Question No. %d" % (i), 3))

    questions.save(filename)
    questions2 = Questions()
    questions2.load(filename)

    assert questions.numQuestions() == questions2.numQuestions()

    os.remove(filename)