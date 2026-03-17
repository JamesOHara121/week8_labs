from app import db
from app.models import *


def setup():
    db.create_all()

    s1 = Student(username="Bob",
                 email="bob@bob.com")
    s1.set_password("hello")

    s2 = Student(username="Jim",
                 email="jim@jim.com")
    s2.set_password("hello")

    s3 = Student(username="Jeff",
                 email="jeff@jeff.com")
    s3.set_password("hello")

    t1 = Topic(name="Cheese")
    t2 = Topic(name="Potatoes")
    t3 = Topic(name="Pie")
    t4 = Topic(name="Beef")

    g1 = Group(name="Bob\'s cheese study group",
               group_leader_id=1,
               topic_id=1)

    g2 = Group(name="Jeff\'s potato study group",
               group_leader_id=3,
               topic_id=2)

    g3 = Group(name="Jeff\'s beefy group",
               group_leader_id=3,
               topic_id=4)

    g4 = Group(name="Jim\'s pie group",
               group_leader_id=2,
               topic_id=3)

    sg1 = StudentGroup(student_id=1, group_id=3)
    sg2 = StudentGroup(student_id=1, group_id=2)
    sg3 = StudentGroup(student_id=2, group_id=1)
    sg4 = StudentGroup(student_id=2, group_id=2)
    sg5 = StudentGroup(student_id=2, group_id=3)
    sg6 = StudentGroup(student_id=3, group_id=1)

    instances = [s1, s2, s3, t1, t2, t3, t4, g1, g2, g3, g4, sg1, sg2, sg3, sg4, sg5, sg6]

    db.session.add_all(instances)
    db.session.commit()