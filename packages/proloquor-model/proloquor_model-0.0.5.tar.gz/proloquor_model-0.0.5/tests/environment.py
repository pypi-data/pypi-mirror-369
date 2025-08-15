from proloquor_model.members import Members, Member
from proloquor_model.questions import Questions, Question
from proloquor_model.answers import Answers, Answer

import pytest
import numpy as np
import random as rd

def create_population_members(size=5000):
    population_size =size

    population_members = Members()
    for i in range(population_size):
        population_members.addMember(Member())

    return population_members

def create_questions():
    questions = Questions()
    questions.addQuestion(Question("What is your political affiliation?", 5))
    questions.addQuestion(Question("Do you like tacos?", 3))
    questions.addQuestion(Question("Who would you vote for?", 4))

    return questions

def create_population_answers(population_members: Members, questions: Questions):
    distA = np.array([0.350, 0.330, 0.030, 0.040, 0.250])
    distB = np.array([0.800, 0.150, 0.050])
    distCgA = [[0.45, 0.35, 0.15, 0.05], # For persons who answered Question A with Response 1
               [0.40, 0.30, 0.20, 0.10], # For persons who answered Question A with Response 2
               [0.25, 0.25, 0.25, 0.25], # For persons who answered Question A with Response 3
               [0.10, 0.20, 0.30, 0.40], # For persons who answered Question A with Response 4
               [0.05, 0.15, 0.35, 0.45]] # For persons who answered Question A with Response 5
    
    population_answers = Answers()
    for person in population_members:
        answerA = population_answers.generateAnswer(person, questions.questions[0], distA)
        answerB = population_answers.generateAnswer(person, questions.questions[1], distB)
        answerC = population_answers.generateAnswer(person, questions.questions[2], distCgA[answerA.response - 1])

    return population_answers

def create_membership_members(population_members: Members, questions: Questions, population_answers: Answers):
    member_bias = [
        0.350,  # Probability of a Person becoming a Member if they answer Question A with Response 1
        0.300,  # Probability of a Person becoming a Member if they answer Question A with Response 2
        0.020,  # Probability of a Person becoming a Member if they answer Question A with Response 3
        0.030,  # Probability of a Person becoming a Member if they answer Question A with Response 4
        0.150   # Probability of a Person becoming a Member if they answer Question A with Response 5
    ]

    membership_members = Members()
    for person in population_members:
        member_answers = population_answers.findAnswers(person.uuid, questions.questions[0].uuid)
        if member_answers.numAnswers() == 1:
            if rd.random() < member_bias[member_answers.answers[0].response - 1]:
                membership_members.addMember(person)
        else:
            raise Exception("Can't find a single answer to dependent Question.")
  
    return membership_members

def create_membership_answers(membership_members: Members, questions: Questions, population_answers: Answers):
    answerA_bias = [
        0.80,  # Probability of a Member answering Question A if they answer Question A with Response 1
        0.75,  # Probability of a Member answering Question A if they answer Question A with Response 2
        0.60,  # Probability of a Member answering Question A if they answer Question A with Response 3
        0.55,  # Probability of a Member answering Question A if they answer Question A with Response 4
        0.70   # Probability of a Member answering Question A if they answer Question A with Response 5
    ]

    answerB_bias = [
        0.90,  # Probability of a Member answering Question B if they answer Question A with Response 1
        0.95,  # Probability of a Member answering Question B if they answer Question A with Response 2
        0.60,  # Probability of a Member answering Question B if they answer Question A with Response 3
        0.65,  # Probability of a Member answering Question B if they answer Question A with Response 4
        0.20   # Probability of a Member answering Question B if they answer Question A with Response 5
    ]

    answerC_bias = [
        0.25,  # Probability of a Member answering Question C if they answer Question A with Response 1
        0.85,  # Probability of a Member answering Question C if they answer Question A with Response 2
        0.55,  # Probability of a Member answering Question C if they answer Question A with Response 3
        0.60,  # Probability of a Member answering Question C if they answer Question A with Response 4
        0.90   # Probability of a Member answering Question C if they answer Question A with Response 5
    ]

    membership_answers = Answers()
    for member in membership_members:
        member_answers = population_answers.findAnswers(member.uuid)

        answerA = member_answers.findAnswers(question_uuid=questions.questions[0].uuid).answers[0]
        answerB = member_answers.findAnswers(question_uuid=questions.questions[1].uuid).answers[0]
        answerC = member_answers.findAnswers(question_uuid=questions.questions[2].uuid).answers[0]

        if rd.random() < answerA_bias[answerA.response - 1]:
            membership_answers.addAnswer(answerA)
        if rd.random() < answerB_bias[answerA.response - 1]:
            membership_answers.addAnswer(answerB)
        if rd.random() < answerC_bias[answerA.response - 1]:
            membership_answers.addAnswer(answerC)

    return membership_answers
