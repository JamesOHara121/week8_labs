from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app import app, db, mail
from flask import redirect, url_for, flash, render_template, request
from app.forms import *
from app.models import *
from app.emails import send_email
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit


@app.route("/")
@login_required
def index():
    return redirect(url_for("topic"))


@app.route("/topic", methods=["GET", "POST"])
@login_required
def topic():
    form = TopicForm()
    topics = Topic.query.all()
    if form.validate_on_submit():
        new_topic = Topic(name=form.topic.data)
        try:
            db.session.add(new_topic)
            db.session.commit()
            flash("Topic successfully added!")
            return redirect(url_for("topic"))
        except IntegrityError:
            db.session.rollback()
            flash("This topic already exists!")
    return render_template("topic.html", form=form, topics=topics)


@app.route("/edit_topic/<int:topic_id>", methods=["GET", "POST"])
@login_required
def edit_topic(topic_id):
    topic_to_edit = Topic.query.get(topic_id)
    form = TopicForm(topic=topic_to_edit.name)
    if form.validate_on_submit():
        topic_to_edit.name = form.topic.data
        db.session.commit()
        flash("Topic has been successfully updated!")
        return redirect(url_for("topic"))
    return render_template("update.html", form=form)


@app.route("/delete_topic/<int:topic_id>", methods=['GET', 'POST'])
@login_required
def delete_topic(topic_id):
    topic_to_delete = Topic.query.get(topic_id)
    db.session.delete(topic_to_delete)
    db.session.commit()
    flash("Topic has been deleted!")
    return redirect(url_for("topic"))


@app.route("/add_group", methods=["GET", "POST"])
@login_required
def add_group():
    form = AddGroupForm()
    form.topic.choices = [
        (t.id, t.name) for t in Topic.query.order_by(Topic.name).all()
    ]

    if form.validate_on_submit():
        new_group = Group(
            name=form.group_name.data,
            group_leader_id = current_user.id,
            topic_id = form.topic.data
        )
        try:
            db.session.add(new_group)
            db.session.commit()
            flash("Group successfully created!")
            return redirect(url_for("add_group"))
        except IntegrityError:
            db.session.rollback()
            flash("This group already exists!")

    return render_template("add_group.html", form=form)


@app.route("/manage_groups", methods=["GET", "POST"])
@login_required
def manage_groups():
    groups = Group.query.filter(Group.group_leader_id == current_user.id)
    return render_template("manage_groups.html", groups=groups)


@app.route("/manage_group/<int:group_id>", methods=["GET", "POST"])
@login_required
def manage_group(group_id):

    # check current_user is the group leader
    group = Group.query.get(group_id)
    if group.group_leader_id != current_user.id:
        flash("You do not have access to this page!")
        return redirect(url_for("groups"))

    # FORM SETUP
    form = ManageGroupForm(group_name=group.name)
    # get list of student id's assigned to this group from StudentGroup
    student_group_list = StudentGroup.query.filter(StudentGroup.group_id == group_id)
    # get list of usernames from Student corresponding to the selected id's
    student_list = [
        (sg.student_id, Student.query.get(sg.student_id).username) for sg in student_group_list
    ]
    # add the students to the dropdown menu choices
    form.remove_student.choices.extend(student_list)

    if form.validate_on_submit():

        # CHANGE GROUP NAME
        group.name = form.group_name.data

        # ADD A STUDENT TO THE GROUP
        add_student_username = form.add_student.data
        student_to_add = Student.query.filter_by(username=add_student_username).first()
        # case 1: add student box is left blank
        if not add_student_username:
            pass
        # case 2: username not recognised
        elif not student_to_add:
            flash("Username not recognised!")
            return redirect(url_for("manage_group", group_id=group.id))
        # case 3: group leader tries to add themselves
        elif current_user.id == student_to_add.id:
            flash("You cannot add yourself to this group!")
            return redirect(url_for("manage_group", group_id=group.id))
        # case 4: student already exists in the group
        elif StudentGroup.query.filter(
            StudentGroup.student_id == student_to_add.id,
            StudentGroup.group_id == group_id
        ).first():
            flash("Student is already a part of this group!")
            return redirect(url_for("manage_group", group_id=group.id))
        # case 5: all requirements are met - successfully add student
        else:
            student_group = StudentGroup(
                student_id=student_to_add.id,
                group_id=group.id
            )
            db.session.add(student_group)
            send_email(
                subject="You have been added to a group!",
                sender=app.config['ADMINS'][0],
                recipients=[student_to_add.email],
                text_body=render_template('email/add_student.txt',
                                          student=student_to_add,
                                          group=group),
                html_body=render_template('email/add_student.html',
                                          student=student_to_add,
                                          group=group)
            )

        # REMOVE A STUDENT FROM THE GROUP
        remove_student_id = form.remove_student.data
        if remove_student_id != "None":
            student_to_remove = StudentGroup.query.filter(
                StudentGroup.student_id == remove_student_id,
                StudentGroup.group_id == group_id
            ).first()
            db.session.delete(student_to_remove)
            student_to_email = Student.query.get(remove_student_id)
            send_email(
                subject="You have been removed from a group",
                sender=app.config['ADMINS'][0],
                recipients=[student_to_email.email],
                text_body=render_template('email/remove_student.txt',
                                          student=student_to_email,
                                          group=group),
                html_body=render_template('email/remove_student.html',
                                          student=student_to_email,
                                          group=group)
            )

        db.session.commit()
        flash("Group successfully updated!")
        return redirect(url_for("manage_group", group_id=group.id))

    return render_template("manage_group.html", form=form, group_id=group.id)


@app.route("/groups", methods=["GET", "POST"])
@login_required
def groups():

    # find group names
    group_names = [group.name for group in Group.query.all()]

    # find group leader usernames
    stmt = (
        select(
            Student.username
        )
        .join(Group, Group.group_leader_id == Student.id)
    )
    group_leaders = [student.username for student in db.session.execute(stmt).all()]

    # find topics
    stmt2 = (
        select(
            Topic.name
        )
        .join(Group, Group.topic_id == Topic.id)
    )
    topics = [topic.name for topic in db.session.execute(stmt2).all()]

    all_groups = {
        "group_names": group_names,
        "group_leaders": group_leaders,
        "topics": topics
    }
    return render_template("groups.html", all_groups=all_groups)


@app.route("/booking", methods=["GET", "POST"])
@login_required
def booking():
    form = BookingForm()
    return render_template("booking.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(Student).where(Student.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Student(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)