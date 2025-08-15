from uuid import uuid4
import random
import csv
from uuid import UUID

class Member:
  def __init__(self, member_uuid=None):
    if member_uuid is None:
      self.uuid = uuid4()
    else:
      self.uuid = member_uuid
    self.weight = 1.0

  def __str__(self):
    return self.__dict__.__str__()
    
class Members:
  def __init__(self):
    self.members = []

  def addMember(self, member : Member):
    if isinstance(member, Member):
      self.members.append(member)
      return member
    else:
      return None
  
  def getMember(self, uuid):
    for member in self.members:
      if member.uuid == uuid:
        return member          
    return None
  
  def numMembers(self):
    return len(self.members)
  
  def sampleMembers(self, p):
    samples = Members()
    for member in [member for member in self.members if random.random() < p]:
      samples.addMember(member)
    return samples

  def save(self, filename):
    with open(filename, 'w', newline='') as csvfile:
      fieldnames = ['uuid', 'weight']
      writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONNUMERIC)

      writer.writeheader()
      for member in self:
        writer.writerow({'uuid': member.uuid, 'weight': member.weight})

  def load(self, filename):
    self.members = []

    with open(filename, newline='') as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        self.addMember(Member(UUID(row['uuid'])))

  def __iter__(self):
    self.n = 0
    return self

  def __next__(self):
    if self.n < len(self.members):
      result = self.members[self.n]
      self.n += 1
      return result
    else:
      raise StopIteration
    