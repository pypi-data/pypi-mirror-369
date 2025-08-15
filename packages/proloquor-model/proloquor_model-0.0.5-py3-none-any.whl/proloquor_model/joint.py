from proloquor_model.answers import Answer
from proloquor_model.answers import Answers
from proloquor_model.questions import Question
from proloquor_model.questions import Questions
from proloquor_model.members import Member
from proloquor_model.members import Members
from scipy.stats import chi2
import numpy as np
from uuid import UUID
import json

class Joint:
    def __init__(self, members = None, questions = None, answers = None):
        if questions is not None:
            self.questions = questions
            self.matrix = np.zeros((np.array([len(question.responses)+1 for question in questions])))

        if members is not None and answers is not None:
            for member in members:
                cell = np.zeros(len(questions.questions), dtype=np.int64) 
                member_answers = answers.findAnswers(member.uuid) 

                for answer in member_answers:
                    for i, question in enumerate(questions):
                        if question.uuid == answer.question:
                            cell[i] = answer.response

                self.matrix[tuple(cell)] += member.weight
    
    def load(self, filename):
        with open(filename, 'r') as json_file:
            js = json.load(json_file)

        self.questions = Questions()
        for question in js['proloquor']['questions']:
            self.questions.addQuestion(Question(question['description'], len(question['responses']), UUID(question['uuid'])))

        self.matrix = np.array(js['proloquor']['answers'])

    def save(self, filename):

        js = {}
        proloquor_js = js['proloquor'] = {}

        questions_js = proloquor_js['questions'] = []
        for question in self.questions:
            question_js = {}
            question_js['uuid'] = str(question.uuid)
            question_js['link'] = "https://proloquor.net/questions/%s" % (question.uuid)
            question_js['index'] = self.question_index(question.uuid)
            question_js['description'] = question.description
            question_js['query'] = "What is your quest?"
 
            responses_js = question_js['responses'] = []
            for response in question.responses:
                response_js = {'index': response, 'value': "Response #%d" % (response)}
                responses_js.append(response_js)
                    
            questions_js.append(question_js)

        answers_js = proloquor_js['answers'] = self.matrix.tolist()

        with open(filename, 'w') as json_file:
            json.dump(js, json_file)

    def dim_sum(self, *dims):
        ndim = self.matrix.ndim

        dims = np.sort(dims)

        if(np.max(dims) >= ndim):
            return None

        sum = np.copy(self.matrix)
        for i in range(ndim-1, -1, -1):
            if i not in dims:
                sum = sum.sum(axis=i)

        return sum

    def question_index(self, question_uuid):
        for i, question in enumerate(self.questions):
            if question.uuid == question_uuid:
                return i
        return None

    def Pr_A(self, question_uuid, r = None):
        index = self.question_index(question_uuid)
        if index == None:
            return None
        
        sum = self.dim_sum(index) / np.sum(self.matrix)
        if r == None:
            return sum
        
        return sum[r]

    def Pr_A_normalized(self, question_uuid, r = None):
        prob = self.Pr_A(question_uuid)[1:]
        sum = np.sum(prob)

        if sum == 0.0:
            raise Exception("The distribution is empty.")
        ratio = prob / sum

        if r == None:
            return ratio
        else:
            return ratio[r-1]
        
    def Pr_AB(self, questionA_uuid, questionB_uuid, r = None):
        indexA = self.question_index(questionA_uuid)
        indexB = self.question_index(questionB_uuid)
        if indexA == None or indexB == None:
            return None
        
        sum = self.dim_sum(indexA, indexB) / np.sum(self.matrix)

        if type(r) is not tuple or len(r) != 2:
            return sum
        
        ra, rb = r
        return sum[ra][rb]
        
    def Pr_AgB(self, questionA_uuid, questionB_uuid, r = None):
        indexA = self.question_index(questionA_uuid)
        indexB = self.question_index(questionB_uuid)
        if indexA == None or indexB == None:
            return None
        
        with np.errstate(divide='ignore', invalid='ignore'):  # Could return nan's
            sum = self.dim_sum(indexA, indexB) / self.dim_sum(indexB)
            sum = np.nan_to_num(sum)

        if type(r) is not tuple or len(r) != 2:
            return sum
    
        ra, rb = r
        return sum[ra][rb]
    
    def is_independent(self, questionA_uuid, questionB_uuid):
        indexA = self.question_index(questionA_uuid)
        indexB = self.question_index(questionB_uuid)

        if indexA is None or indexB is None:
            return None
        
        o = self.dim_sum(indexA, indexB)
        o = np.delete(o, 0, 0)
        o = np.delete(o, 0, 1)

        e = np.zeros((o.shape))
        for i, s1 in enumerate(self.dim_sum(indexA)[1:]):
            for j, s2 in enumerate(self.dim_sum(indexB)[1:]):
                e[i][j] = s1*s2 / np.sum(self.matrix)

        with np.errstate(divide='ignore', invalid='ignore'):
            chi2_statistic = np.sum(np.nan_to_num(np.square(o - e) / e))

        alpha = 0.05
        dof = (o.shape[0] - 1) * (o.shape[1] - 1)
        num_cells = e.shape[0] * e.shape[1]

        if (dof > 1 and len(e[e < 5]) / num_cells > 0.20) or (len(e[e < 10]) / num_cells > 0.20):
            raise Exception("Test for independence is not be reliable!")

        chi2_critical = chi2.ppf(1-alpha, dof)

        return chi2_statistic <= chi2_critical