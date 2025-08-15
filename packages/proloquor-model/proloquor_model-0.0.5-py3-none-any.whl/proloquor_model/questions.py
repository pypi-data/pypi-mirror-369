from uuid import uuid4
import csv
from uuid import UUID

class Question:
    def __init__(self, description, numResponses, question_uuid=None):
        if question_uuid is None:
            self.uuid = uuid4()
        else:
          self.uuid = question_uuid
        self.responses = [i for i in range(1, numResponses + 1)]
        self.type = self.__class__.__name__
        self.description = description

    def __str__(self):
        return self.__dict__.__str__()
    
class Questions:
    def __init__(self):
        self.questions = []

    def addQuestion(self, question):
        if isinstance(question, Question):
            self.questions.append(question)
            return question
        else:
            return None
        
    def getQuestion(self, uuid):
        for question in self.questions:
            if question.uuid == uuid:
                return question
        return None

    def numQuestions(self):
        return len(self.questions)
    
    def save(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['uuid', 'description', 'type', 'responses']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for question in self:
              writer.writerow(question.__dict__)

    def load(self, filename):
        self.questions = []

        with open(filename, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.addQuestion(Question(row['description'], len(row['responses'].split(',')), UUID(row['uuid'])))

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.questions):
            result = self.questions[self.n]
            self.n += 1
            return result

        else:
            raise StopIteration