from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app
from flask_login import login_required, current_user
from . import main
from .. import db
from ..models import Doctor,Patient,Registrar,Admin,Departments, Registration
from ..decorators import admin_required, patient_required,doctor_required,registrar_required
from flask import jsonify
from .forms import AddDoctorForm, AddDepartmentForm, \
    AddPatientForm, BookingForm, BookingDoctorForm, \
    AddRegistrarForm,HelpRegistrationForm,HelpRegistrationDoctorForm,\
    ChangeDepartmentForm, ChangeDoctorForm
import datetime

'''
@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('index.html', users=users, pagination=pagination)


@main.route('/deleteuser', methods = ['POST'])
@login_required
@admin_required
def delete_user():
    id = request.form.get('uid', 0, type=int)
    user = User.query.get_or_404(id)
    db.session.delete(user)
    return jsonify({'ok': True})

'''
@main.route('/')
def index():
    return render_template('index.html')

@main.route('/patient', methods= ['GET', 'POST'])
@login_required
@patient_required
def patient():
    return render_template('patient.html')


@main.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar():
    return render_template('registrar.html')

@main.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin():
    return render_template('admin.html')

@main.route('/admin/adddoctor', methods=['GET', 'POST'])
@login_required
@admin_required
def add_doctor():
    form = AddDoctorForm()
    form.depart_id.choices = [(d.id, d.name) for d in Departments.query.order_by('id')]
    if form.validate_on_submit():
        user = Doctor(workcard=form.workcard.data,
                      idcard=form.idcard.data,
                      name=form.name.data,
                      password=form.password.data,
                      depart_id=form.depart_id.data)
        db.session.add(user)
        db.session.commit()
        flash('You have added a doctor!')
        return redirect(url_for('.add_doctor'))
    return render_template('add_doctor.html', form=form)

@main.route('/admin/doctorlist', methods=['GET', 'POST'])
@login_required
@admin_required
def doctor_list():
    page = request.args.get('page', 1, type=int)
    pagination = Doctor.query.order_by(Doctor.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('doctorlist.html', doctors=users, pagination=pagination)

@main.route('/admin/deletedoctor', methods=['GET','POST'])
@login_required
@admin_required
def delete_doctor():
    doctorid = int(request.form.get('doctorid', 0))
    user = Doctor.query.filter_by(id=doctorid).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = 'You have deleted doctor '+username
        flash(info)
        return jsonify({'ok': True})

@main.route('/admin/changedoctor/<dname>/<dpartname>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_doctor(dname,dpartname):
    form = ChangeDoctorForm()
    form.depart_id.choices = [(d.id, d.name) for d in Departments.query.order_by('id')]
    if form.validate_on_submit():
        Doctor.query.filter_by(name=dname).update({
            'name': form.name.data,
            'depart_id':form.depart_id.data
        })
        db.session.commit()
        flash('You have changed the doctor!')
        return redirect(url_for('.doctor_list'))
    dpart = Departments.query.filter_by(name=dpartname).first()
    form.name.data = dname
    if dpart:
        form.depart_id.data = dpart.id
    return render_template('change_doctor.html', form=form)



@main.route('/admin/adddepartment', methods=['GET', 'POST'])
@login_required
@admin_required
def add_department():
    form = AddDepartmentForm()
    if form.validate_on_submit():
        dpart = Departments(name=form.name.data)
        db.session.add(dpart)
        db.session.commit()
        flash('You have added a department!')
        return redirect(url_for('.add_department'))
    return render_template('add_department.html', form=form)

@main.route('/admin/departmentlist', methods=['GET', 'POST'])
@login_required
@admin_required
def department_list():
    page = request.args.get('page', 1, type=int)
    pagination = Departments.query.order_by(Departments.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    dparts = pagination.items
    return render_template('departmentlist.html', departments=dparts, pagination=pagination)

@main.route('/admin/deletedepartment', methods=['GET','POST'])
@login_required
@admin_required
def delete_department():
    dpartid = int(request.form.get('dpartid', 0))
    user = Departments.query.filter_by(id=dpartid).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = 'You have deleted department '+username
        flash(info)
        return jsonify({'ok': True})

@main.route('/admin/changedepartment/<dname>', methods=['GET', 'POST'])
@login_required
@admin_required
def change_department(dname):
    form = ChangeDepartmentForm()
    if form.validate_on_submit():
        dpartname = form.name.data
        dpart = Departments.query.filter_by(name=dpartname).first()
        if dpart and not dpart.name == dname:
            flash('The department name '+dpart.name+' already in use.')
            return redirect(url_for('main.change_department',dname=dname))
        Departments.query.filter_by(name=dname).update({
            'name':dpartname
        })
        db.session.commit()
        flash('You have changed the department!')
        return redirect(url_for('.department_list'))
    form.name.data = dname
    return render_template('change_department.html', form=form)

@main.route('/admin/addpatient', methods=['GET', 'POST'])
@login_required
@admin_required
def add_patient():
    form = AddPatientForm()
    form.gender.choices = [(1, 'male'), (2, 'female')]
    if form.validate_on_submit():
        user = Patient(medcard=form.medcard.data,
                       idcard=form.idcard.data,
                       birthday=form.birthday.data,
                       gender=form.gender.data,
                       phone=form.phone.data,
                       address=form.address.data,
                       name=form.name.data,
                       password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have added a patient!')
        return redirect(url_for('.add_patient'))
    return render_template('add_patient.html', form=form)

@main.route('/admin/patientlist', methods=['GET', 'POST'])
@login_required
@admin_required
def patient_list():
    page = request.args.get('page', 1, type=int)
    pagination = Patient.query.order_by(Patient.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('patientlist.html', patients=users, pagination=pagination)

@main.route('/admin/deletepatient', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_patient():
    patientid = int(request.form.get('patientid', 0))
    user = Patient.query.filter_by(id=patientid).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = 'You have deleted patient '+username
        flash(info)
        return jsonify({'ok': True})


@main.route('/admin/addregistrar', methods=['GET', 'POST'])
@login_required
@admin_required
def add_registrar():
    form = AddRegistrarForm()
    if form.validate_on_submit():
        user = Registrar(workcard=form.workcard.data,
                         idcard=form.idcard.data,
                         name=form.name.data,
                         password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You have added a registrar!')
        return redirect(url_for('.add_registrar'))
    return render_template('add_registrar.html', form=form)

@main.route('/admin/registrarlist', methods=['GET', 'POST'])
@login_required
@admin_required
def registrar_list():
    page = request.args.get('page', 1, type=int)
    pagination = Registrar.query.order_by(Registrar.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('registrarlist.html', registrars=users, pagination=pagination)

@main.route('/admin/deleteregistrar', methods=['GET','POST'])
@login_required
@admin_required
def delete_registrar():
    registrarid = int(request.form.get('registrarid', 0))
    user = Registrar.query.filter_by(id=registrarid).first()
    username = user.name
    if user:
        db.session.delete(user)
        db.session.commit()
        info = 'You have deleted registrar ' + username
        flash(info)
        return jsonify({'ok': True})



@main.route('/patient/booking', methods=['GET', 'POST'])
@login_required
@patient_required
def booking():
    form = BookingForm()
    form.depart_id.choices = [(d.id, d.name) for d in Departments.query.order_by('id')]
    if form.validate_on_submit():
        flash('Please choose a doctor!')
        return redirect(url_for('.booking_doctor', depart_id=form.depart_id.data, date=form.bookingday.data))
    return render_template('booking.html', form=form)

@main.route('/patient/booking_doctor/<depart_id>/<date>', methods=['GET', 'POST'])
@login_required
@patient_required
def booking_doctor(depart_id, date):
    form = BookingDoctorForm()
    form.doctor_id.choices = [(d.id, d.name) for d in Doctor.query.filter_by(depart_id=depart_id).all()]
    if form.validate_on_submit():
        tdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        check =  Registration.query.filter_by(patient_id=current_user.id,
                                              doctor_id=form.doctor_id.data,
                                              handled=False,
                                              registration_date=tdate).first()
        if check:
            flash('You already booked this doctor!')
            return render_template('booking_doctor.html', form=form)
        regi = Registration(doctor_id=form.doctor_id.data,
                             patient_id=current_user.id,
                             registration_date=tdate)
        flash('Your booking was commited.')
        db.session.add(regi)
        db.session.commit()
        return redirect(url_for('.booking'))
    return render_template('booking_doctor.html', form=form)

@main.route('/patient/booking_list', methods=['GET', 'POST'])
@login_required
@patient_required
def booking_list():
    page = request.args.get('page', 1, type=int)
    today = datetime.datetime.now().date()
    pagination = Registration.query.filter_by(patient_id=current_user.id,handled=False)\
        .filter(Registration.registration_date >= today).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    registrations = pagination.items
    return render_template('bookinglist.html', registrations=registrations, pagination=pagination)

@main.route('/doctor', methods=['GET', 'POST'])
@login_required
@doctor_required
def doctor():
    return render_template('doctor.html')

@main.route('/doctor/waiting_patients', methods=['GET','POST'])
@login_required
@doctor_required
def waiting_patients():
    page = request.args.get('page', 1, type=int)
    today = datetime.datetime.now().date()
    pagination = Registration.query.filter_by(doctor_id=current_user.id,
                                              registration_date=today,
                                              handled=False).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    registrations = pagination.items
    return render_template('waiting_patients.html', registrations=registrations, pagination=pagination)

@main.route('/doctor/complete_see_patient/<int:patient_id>/<int:doctor_id>/<date>', methods=['GET', 'POST'])
@login_required
@doctor_required
def complete_see_patient(patient_id, doctor_id, date):
    tdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    Registration.query.filter_by(patient_id=patient_id,
                                 doctor_id=doctor_id,
                                 registration_date=tdate).update({
        'handled':True
    })
    page = request.args.get('page', 1, type=int)
    today = datetime.datetime.now().date()
    pagination = Registration.query.filter_by(doctor_id=current_user.id,
                                              registration_date=today,
                                              handled=False).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    registrations = pagination.items

    return render_template('waiting_patients.html', registrations=registrations, pagination=pagination)

@main.route('/doctor/handled_patient_list', methods=['GET', 'POST'])
@login_required
@doctor_required
def handled_patient_list():
    page = request.args.get('page', 1, type=int)
    today = datetime.datetime.now().date()
    pagination = Registration.query.filter_by(doctor_id=current_user.id,
                                          registration_date=today,
                                          handled=True).paginate(
    page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    error_out=False)
    registrations = pagination.items
    return render_template('handled_patient_list.html', registrations=registrations, pagination=pagination)

@main.route('/registrar/help_add_patient', methods=['GET', 'POST'])
@login_required
@registrar_required
def help_add_patient():
    form = AddPatientForm()
    form.gender.choices = [(1, 'male'), (2, 'female')]
    if form.validate_on_submit():
        user = Patient(medcard=form.medcard.data,
                       idcard=form.idcard.data,
                       birthday=form.birthday.data,
                       gender=form.gender.data,
                       phone=form.phone.data,
                       address=form.address.data,
                       name=form.name.data,
                       password=form.password.data)
        flash('You have added a patient successfully.')
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.help_add_patient'))
    return render_template('help_add_patient.html', form=form)


@main.route('/registrar/help_registration', methods=['GET', 'POST'])
@login_required
@registrar_required
def help_registration():
    form = HelpRegistrationForm()
    form.depart_id.choices = [(d.id, d.name) for d in Departments.query.order_by('id')]
    if form.validate_on_submit():
        user = Patient.query.filter_by(medcard=form.patient_medcard.data).first()
        if user is not None and user.verify_password(form.password.data):
            return redirect(url_for('.help_registration_doctor', depart_id=form.depart_id.data, date=form.bookingday.data, user_id=user.id))
        else:
            flash('Something wrong with password or medcard.')
            return render_template('help_registration.html', form=form)
    return render_template('help_registration.html', form=form)

@main.route('/registrar/help_registration_doctor/<depart_id>/<date>/<user_id>', methods=['GET', 'POST'])
@login_required
@registrar_required
def help_registration_doctor(depart_id, date, user_id):
    form = BookingDoctorForm()
    form.doctor_id.choices = [(d.id, d.name) for d in Doctor.query.filter_by(depart_id=depart_id).all()]
    if form.validate_on_submit():
        tdate = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        check = Registration.query.filter_by(patient_id=user_id,
                                             doctor_id=form.doctor_id.data,
                                             handled=False,
                                             registration_date=tdate).first()
        if check:
            flash('You already booked this doctor!')
            return render_template('help_registration_doctor.html', form=form)
        regi = Registration(doctor_id=form.doctor_id.data,
                            patient_id=user_id,
                            registration_date=tdate)
        flash('Your booking was commited.')
        db.session.add(regi)
        db.session.commit()
        return redirect(url_for('.help_registration'))
    return render_template('help_registration_doctor.html', form=form)

@main.route('/registrar/help_patient_list', methods=['GET', 'POST'])
@login_required
@registrar_required
def help_patient_list():
    page = request.args.get('page', 1, type=int)
    pagination = Patient.query.order_by(Patient.id.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('help_patientlist.html', patients=users, pagination=pagination)

@main.route('/registrar/help_registration_list', methods=['GET', 'POST'])
@login_required
@registrar_required
def help_registration_list():
    page = request.args.get('page', 1, type=int)
    today = datetime.datetime.now().date()
    pagination = Registration.query.filter(Registration.registration_date >= today).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    registrations = pagination.items
    return render_template('help_registration_list.html', registrations=registrations, pagination=pagination)
