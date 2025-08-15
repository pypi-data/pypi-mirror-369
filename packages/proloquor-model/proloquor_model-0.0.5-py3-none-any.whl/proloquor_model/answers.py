from proloquor_model.questions import Question
from proloquor_model.members import Member
from uuid import UUID
from uuid import uuid4
import numpy as np
import random as rd
import csv

class Answer:
    def __init__(self, member_uuid, question_uuid, response, answer_uuid=None):
        if answer_uuid is None:
          self.uuid = uuid4()
        else:
          self.uuid = answer_uuid
        self.member = member_uuid
        self.question = question_uuid
        self.response = response

    def __str__(self):
        return self.__dict__.__str__()    
    
class Answers:
    def __init__(self):
        self.answers = []

    def addAnswer(self, answer):
        if isinstance(answer, Answer):
            self.answers.append(answer)
            return answer
        else:
            return None

    def generateAnswer(self, member : Member, question : Question, dist=None):
        if dist is None:
            return self.addAnswer(Answer(member.uuid, question.uuid, np.random.choice(question.responses)))
        else:
            if len(question.responses) == len(dist) and np.isclose(np.sum(dist), 1.0):
                return self.addAnswer(Answer(member.uuid, question.uuid, np.random.choice(question.responses, p=dist)))

    def getAnswer(self, uuid):
        for answer in self.answers:
            if answer.uuid == uuid:
                return answer
        return None
    
    def numAnswers(self):
        return len(self.answers)

    def findAnswers(self, member_uuid=None, question_uuid=None, response=None):
        found = Answers()
        for answer in self:
            if (member_uuid is None or answer.member == member_uuid):
                if (question_uuid is None or answer.question == question_uuid):
                    if (response is None or answer.response == response):
                        found.addAnswer(answer)
        return found

    def countAnswers(self, question_uuid, response=None):
        if response is not None:
            return self.findAnswers(question_uuid=question_uuid, response=response).numAnswers()
        return self.findAnswers(question_uuid=question_uuid).numAnswers()
    
    def sampleAnswers(self, p, question_uuid=None):
        if question_uuid == None:
            samples = [answer for answer in self.answers if rd.random() < p]
        else:
            samples = [answer for answer in self.answers if answer.question == question_uuid and rd.random() < p]

        sampleAnswers = Answers()
        for sample in samples:
            sampleAnswers.addAnswer(sample)

        return sampleAnswers
    
    def save(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['uuid', 'member', 'question', 'response']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for answer in self:
              writer.writerow({'uuid': answer.uuid, 'member': answer.member, 'question': answer.question, 'response': answer.response})

    def load(self, filename):
        self.answers = []

        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.addAnswer(Answer(UUID(row['member']), UUID(row['question']), int(row['response']), UUID(row['uuid'])))

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.answers):
            result = self.answers[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration