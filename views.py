from crypt import methods
from flask import Blueprint, render_template, request, flash,  redirect , url_for, jsonify
from flask_login import login_user, login_required, current_user, logout_user


from models import User,List,Card
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()
views = Blueprint('views', __name__)

#<------------------------------------------Auth------------------------------------------------>

@views.route('/')
def home():
    return render_template('index.html')

@views.route('/about')
def about():
    return render_template('about.html')

@views.route('/login')
def login():
    return render_template('login.html')

@views.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@views.route('/summary')
def summary():
    lists = db.session.query(List).filter_by(creator_id=current_user.id).all()
    cards = db.session.query(Card).filter_by(creator_id=current_user.id).all()
    date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    lists=len(lists)
    tasks=len(cards)
    past_deadline=0
    list=[]
    data=[0,0,0,0,0,0,0,0,0,0,0,0]
    strdata=''
    completed=0
    for card in cards:
        if (card.deadline) and (date>card.deadline.strftime("%Y/%m/%d %H:%M:%S")) and (card.complete_flag==False):
            past_deadline=past_deadline+1
        if (card.completed_on) and (card.complete_flag==True):
            completed=completed+1
            list.append(card.completed_on.strftime("%B"))
    for month in list:
        if month=="January": data[1]=data[1]+1
        if month=="February": data[2]=data[2]+1
        if month=="March": data[3]=data[3]+1
        if month=="April": data[4]=data[4]+1
        if month=="May": data[5]=data[5]+1
        if month=="June": data[6]=data[6]+1
        if month=="July": data[7]=data[7]+1
        if month=="August": data[8]=data[8]+1
        if month=="September": data[9]=data[9]+1
        if month=="October": data[10]=data[10]+1
        if month=="November": data[11]=data[11]+1
        if month=="December": data[12]=data[12]+1
    for ele in data:
        strdata=strdata+','+str(ele)
    return render_template('summary.html', data=strdata[1:], past_deadline=past_deadline, completed=completed, lists=lists,tasks=tasks)

@views.route('/login', methods=["POST"])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True

    user=db.session.query(User).filter_by(username=username).first()
    if user==None:
        flash("User does not exist.")
        return redirect(url_for('views.login'))
    user=db.session.query(User).filter_by(username=username,password=password).first()
    if user:
        login_user(user, remember=remember)  
        return redirect(url_for('views.dashboard'))
    else:
        flash("Password not correct.")
        return redirect(url_for('views.login'))


@views.route('/register')
def register():
    return render_template('register.html')

@views.route('/register', methods=["POST"])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == ""  or password == "":
        flash('Username or password cannot be empty. Please try again.')
        return redirect(url_for('views.register'))
    user=db.session.query(User).filter_by(username=username).first()
    if user:
        flash('User already exists.')
        return redirect(url_for('views.register'))

    new_user = User(
        id=str(uuid.uuid4()),
        username=username,
        password=password,
    )
    db.session.add(new_user)
    db.session.commit()
    
    user=db.session.query(User).filter_by(username=username,password=password).first()
    return render_template("dashboard.html")

#<------------------------------------------Lists------------------------------------------------>

@views.route('/dashboard')
@login_required
def dashboard(): #send lists and cards
    lists = db.session.query(List).filter_by(creator_id=current_user.id).all()
    cards = db.session.query(Card).filter_by(creator_id=current_user.id).all()
    date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    if lists==[]:
        flash("Create a list to get started -->")
        return render_template("dashboard.html")
    return render_template("dashboard.html", lists=lists, cards=cards, date=date)
    
@views.route('/list')
@login_required
def list():
    return render_template('list.html')

@views.route('/list', methods=['POST'])
@login_required
def newlist(): #create list
    list_name=request.form.get('list_name')
    if list_name == "":
        flash("list name cannot be empty. Please try again.")
        return redirect(url_for('views.dashboard'))
    print(list_name)
    list = db.session.query(List).filter_by(list_name=list_name, creator_id=current_user.id).first()
    if list:
        flash("List already exists")
        return redirect(url_for('views.dashboard'))

    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    
    new_list = List(
        list_id=str(uuid.uuid4()),
        list_name=request.form.get('list_name'),
        creator_id=current_user.id,
        updated_on=converted_date,
    )
    db.session.add(new_list)
    db.session.commit()
    return redirect(url_for('views.dashboard'))

@views.route('/edit/list/<list_id>')
def edit_list_name(list_id):
    list = db.session.query(List).filter_by(list_id=list_id,creator_id=current_user.id).first()
    list_name=list.list_name
    return render_template('editlist.html',list_id=list_id,list_name= list_name)

@views.route('/list/<list_id>', methods=['POST'])
@login_required
def editlist(list_id): #edit list
    new_list_name=request.form.get('new_list_name')
    print(new_list_name)
    if new_list_name == "":
        flash("list name cannot be empty. Please try again.")
        return redirect(url_for('views.dashboard'))

    list = db.session.query(List).filter_by(list_name=new_list_name,creator_id=current_user.id).first()
    if list:
        flash("List already exists")
        return redirect(url_for('views.dashboard'))
    list=db.session.query(List).get(list_id)
    list.list_name=new_list_name
    db.session.commit()
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    list.updated_on=converted_date    
    db.session.commit()
    return redirect(url_for('views.dashboard'))

@views.route('/delete/list/<list_id>')
@login_required
def dellist(list_id): # delete list
    cards = db.session.query(Card).filter_by(list_id=list_id).all()
    if cards!=[]:
        for card in cards:
            db.session.delete(card)
    list = db.session.query(List).filter_by(list_id=list_id).first()
    db.session.delete(list)
    db.session.commit()
    return redirect(url_for('views.dashboard'))

#<------------------------------------------Cards------------------------------------------------>



@views.route('/card/<card_id>')    
@login_required
def api_get_card(card_id): # get one card 
    card = db.session.query(Card).filter_by(card_id=card_id).first()
    if card:    
        return render_template("card.html", card=card)
    flash("No card found.")
    return redirect(url_for('views.list'))

@views.route('/newcard/<list_id>')
@login_required
def card(list_id):
    return render_template('card.html',list_id=list_id)

@views.route('/newcard/<list_id>', methods=['POST'])
@login_required   
def newcard(list_id): # create new card

    title = request.form.get('title')
    content = request.form.get('content')
    deadline = request.form.get('deadline')

    if title == "":
        flash("Title cannot be empty. Please try again.")
        return redirect(url_for('views.newcard'))

    
    if content==None:
        content=''
    card = db.session.query(Card).filter_by(title=title, content=content, list_id=list_id).first()
    if card:
        flash("Card already exists in list.")
        return redirect(url_for('views.new'))
    if deadline == "":
        deadline=None
    else:    
        deadline = deadline.replace("T", " ")
        deadline = deadline.replace("-", "/")
        deadline=deadline+":00"

        deadline= datetime.strptime(deadline, '%Y/%m/%d %H:%M:%S')
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    new_card = Card(
        creator_id= current_user.id,
        card_id=str(uuid.uuid4()),
        list_id=list_id,
        title=title,
        content=content,
        deadline=deadline,
        created_on=converted_date
    )
    db.session.add(new_card)
    db.session.commit()

    list=db.session.query(List).get(list_id)
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    list.updated_on=converted_date
    db.session.commit()
    return redirect(url_for('views.dashboard'))

@views.route('/edit/card/<card_id>')
def edit_card_name(card_id):
    card = db.session.query(Card).filter_by(card_id=card_id,creator_id=current_user.id).first()
    title=card.title
    content=card.content
    deadline=card.deadline
    return render_template('editcard.html',card_id=card_id,title=title,content=content,deadline=deadline)

@views.route('/edit/card/<card_id>', methods=['POST'])
@login_required    
def editcard(card_id): #edit card
    card = db.session.query(Card).get(card_id)

    title = request.form.get('title')
    content = request.form.get('content')
    deadline = request.form.get('deadline')
    if deadline=='':
        deadline=None
    else:
        deadline = deadline.replace("T", " ")
        deadline = deadline.replace("-", "/")
        deadline=deadline+":00"
        deadline= datetime.strptime(deadline, '%Y/%m/%d %H:%M:%S')
    print(type(deadline))
    if title == "" and content == "":
        flash("Please fill in details")
        return redirect(url_for('views.editcard'))
    
    card = db.session.query(Card).filter_by(title=title, content=content, list_id=card.list_id, deadline=deadline).first()
    if card:
        flash("Card already exists in list.")
        return redirect(url_for('views.dashboard'))

    card=db.session.query(Card).get(card_id)
    card.title=title
    card.content=content
    card.deadline=deadline
    list=db.session.query(List).get(card.list_id)
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S')
    list.updated_on=converted_date
    db.session.commit()
    return redirect(url_for('views.dashboard'))

@views.route('/delete/card/<card_id>')
@login_required
def delcard(card_id): #delete card
    card = db.session.query(Card).get(card_id)
    db.session.delete(card)
    list=db.session.query(List).get(card.list_id)
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    list.updated_on=converted_date
    db.session.commit()
    return redirect(url_for('views.dashboard'))

@views.route('/completed/card/<card_id>')
@login_required
def complete_card(card_id): #mark card as complete
    card=db.session.query(Card).get(card_id)
    card.complete_flag=True
    converted_date=datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    converted_date=datetime.strptime(converted_date, '%Y/%m/%d %H:%M:%S') 
    card.completed_on=converted_date
    db.session.commit()
    return redirect(url_for('views.dashboard'))


@views.route('/incompleted/card/<card_id>')
@login_required
def incomplete_card(card_id): #mark card as incomplete
    card=db.session.query(Card).get(card_id)
    card.complete_flag=False
    card.completed_on=None
    db.session.commit()
    return redirect(url_for('views.dashboard'))

