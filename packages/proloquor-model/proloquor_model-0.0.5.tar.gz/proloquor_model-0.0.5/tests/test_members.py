import sys
if 'src' not in sys.path:
    sys.path.insert(0, 'src')

from proloquor_model.members import Member
from proloquor_model.members import Members
from uuid import uuid4
import tempfile
import os

def test_member():
    member = Member()
    assert member.weight == 1.0
    assert member.uuid is not None

def test_memberWithUuid():
    uuid = uuid4()
    member = Member(uuid)
    assert member.uuid == uuid

def test_addMember():
    members = Members()
    member = Member()
    assert members.numMembers() == 0

    members.addMember(member)
    assert members.numMembers() == 1

    members.addMember(1)
    assert members.numMembers() == 1

def test_getMember():
    members = Members()
    member = Member()
    members.addMember(member)
    members.addMember(Member())
    members.addMember(Member())

    assert members.getMember(member.uuid).uuid == member.uuid

def test_sampleMembers():
    members = Members()
    for i in range(100):
        members.addMember(Member())
    sample = members.sampleMembers(0.6)
    assert sample.numMembers() > 0 and sample.numMembers() < 100

def test_saveLoad():
    filename = tempfile.NamedTemporaryFile(delete=False).name

    members = Members()
    for i in range(100):
        members.addMember(Member())

    members.save(filename)
    members2 = Members()
    members2.load(filename)

    assert members.numMembers() == members2.numMembers()
    assert members2.getMember(members.members[0].uuid).uuid == members.members[0].uuid

    os.remove(filename)
