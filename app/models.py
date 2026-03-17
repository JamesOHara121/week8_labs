from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy.orm as so
import sqlalchemy as sa
from flask_login import UserMixin
from app import db, login
from datetime import datetime

# ADD ALL REQUIRED RELATIONSHIPS
# YOU MAY ADD ANY FIELDS YOU NEED
# YOU MAY ADD ANY TABLES YOU NEED


class Student(db.Model, UserMixin):
    __tablename__ = 'student'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    username: so.Mapped[str] = so.mapped_column(db.String, index= True, unique=True)
    email: so.Mapped[str] = so.mapped_column(db.String, index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    groups: so.Mapped[list["StudentGroup"]] = so.relationship(back_populates="student",
                                                              cascade="all, delete-orphan")
    groups_leading: so.Mapped[list["Group"]] = so.relationship(back_populates="group_leader",
                                                               cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"{self.id}. {self.username} ({self.email})"


class Topic(db.Model):
    __tablename__ = 'topic'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    def __repr__(self):
        return f"{self.id}. {self.name}"


class Group(db.Model):
    __tablename__ = 'group'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)

    group_leader_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    topic_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("topic.id"), nullable=False)

    students: so.Mapped[list["StudentGroup"]] = so.relationship(back_populates="group",
                                                                cascade="all, delete-orphan")
    group_leader: so.Mapped[Student] = so.relationship(back_populates="groups_leading")
    booking: so.Mapped[list["Booking"]] = so.relationship(back_populates="group",
                                                  cascade="all, delete-orphan")

    def __repr__(self):
        return f"{self.id}. {self.name} ({self.group_leader_id}, {self.topic_id}) {[student for student in self.students]}"


class StudentGroup(db.Model):
    __tablename__ = 'student_group'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    student_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("group.id", ondelete="CASCADE"), nullable=False)

    student: so.Mapped[Student] = so.relationship(back_populates="groups")
    group: so.Mapped[Group] = so.relationship(back_populates="students")

    def __repr__(self):
        return f"{self.id}: student {self.student_id}, group {self.group_id}"


class Venue(db.Model):
    __tablename__ = 'venue'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(db.String, unique=True)
    is_booked: so.Mapped[bool] = so.mapped_column(db.Boolean, default=False)

    booking: so.Mapped[list["Booking"]] =  so.relationship(back_populates="venue",
                                                           cascade="all, delete-orphan")


class Booking(db.Model):
    __tablename__ = 'booking'

    id: so.Mapped[int] = so.mapped_column(db.Integer, primary_key=True)
    booking_date: so.Mapped[datetime] = so.mapped_column(db.Date, nullable=False)

    group_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("group.id", ondelete="CASCADE"), nullable=False)
    venue_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False)

    group: so.Mapped[Group] = so.relationship(back_populates="booking")
    venue: so.Mapped[Venue] = so.relationship(back_populates="booking")


@login.user_loader
def load_user(id):
    return db.session.get(Student, int(id))