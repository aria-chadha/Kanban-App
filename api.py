from zoneinfo import ZoneInfo
import datetime
import jwt
import uuid

from flask import  request, jsonify
from functools import wraps

from models import User, List, Card, card_schema,cards_schema, list_schema, lists_schema, user_schema,users_schema  
from main import app, db

#<------------------------------------------Decorator------------------------------------------------>

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Internal server error!'}),401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'],algorithms=["HS256"])
            current_user = User.query.filter_by(user_id=data['user_id']).first()
        except:
            return jsonify({'message' : 'User not logged in!'}),401

        current_user = User.query.filter_by(user_id=data['user_id']).first()
        return f(current_user, *args, **kwargs)

    return decorated
#<------------------------------------------Auth------------------------------------------------>

@app.route('/api/login', methods=['POST'])
def api_login(): # login to account
    content = request.json
    username= content['username']
    password= content['password']

    user=User.query.filter_by(username=username).first()
    if user==None:
            return jsonify({"message": "User does not exist."}),400
    user=User.query.filter_by(username=username,password=password).first()
    if user:  
        token = jwt.encode({'user_id' : user.user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token , 'message':'login successful!'}),200
    else:
        return jsonify({"message": "Password not correct."}),400

@app.route('/api/register', methods=['POST'])
def api_register():  #create user
    content = request.json

    username= content['username']
    password= content['password']
    if username == ""  or password == "":
        return jsonify({'message':'Username or password cannot be empty. Please try again.'}),400
    
    user=User.query.filter_by(username=username).first()
    if user:
        return jsonify({'message':'User already exists.'}),400
    new_user = User(
        user_id=str(uuid.uuid4()),
        username=username,
        password=password,
    )
    db.session.add(new_user)
    db.session.commit()
    
    user=User.query.filter_by(username=username,password=password).first()
    token = jwt.encode({'user_id' : user.user_id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(hours=3)}, app.config['SECRET_KEY'])
    return jsonify({'token' : token , 'message':'New User created, login successful!'}),200


#<------------------------------------------User------------------------------------------------>
   
@app.route('/api/users')
@token_required
def api_users(current_user): #get all users - for admin
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'}),403
    users = User.query.all()
    return jsonify(users_schema.dump(users))

@app.route('/api/user')
@token_required    
def api_user(current_user): #get one user - for admin
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'}),403
    username = request.form.get('username')
    user=User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'message':'User does not exist'}),400

    return jsonify(user_schema.dump(user))

@app.route('/api/promotion', methods=['PUT'])    
@token_required
def api_promotion(current_user): #promotion - for admin
    if not current_user.admin:
        return jsonify({'message' : 'Cannot perform that function!'}),403
    username=request.form.get('username')
    user=User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message':'User does not exist'}),400
    user.admin=True
    db.session.commit()
    return jsonify({'message':'User has been promoted'}),200

#<------------------------------------------Lists----------------------------------------------->
@app.route('/api/lists')
@token_required
def api_lists(current_user): #get all lists of user
    lists = List.query.filter_by(creator=current_user.username).all()
    if lists:
        return jsonify(lists_schema.dump(lists))
    return jsonify({"message":"No lists to display. Create a new one."}),400


@app.route('/api/list', methods=['POST'])
@token_required
def api_newlist(current_user): #create list
    list_name=request.form.get('list_name')
    if list_name == "":
        return jsonify({'message':'list name cannot be empty. Please try again.'}),400

    list = List.query.filter_by(list_name=list_name, creator_id=current_user.user_id).first()
    if list:
        return jsonify({'message':'list already exists'}),400
    
    new_list = list(
        list_id=str(uuid.uuid4()),
        list_name=request.form.get('list_name'),
        creator_id=current_user.user_id,
        updated_on=datetime.now(),
    )
    db.session.add(new_list)
    db.session.commit()
    return_list = List.query.filter_by(list_name=list_name, creator_id=current_user.user_id).first()

    return jsonify({'deck_id':return_list.list_id}),200

@app.route('/api/list/<list_id>', methods=['PUT'])
@token_required
def api_editlist(current_user,list_id): #edit list
    new_list_name=request.form.get('new_list_name')
    
    if new_list_name == "":
        return jsonify({'message':'list cannot be empty. Please try again.'}),400

    list = List.query.filter_by(list_name=new_list_name,creator=current_user.username).first()
    if list:
        return jsonify({'message':'list already exists'}),400
    
    List.query.filter_by(list_id=list_id).update(
    dict(list_name=new_list_name))
    List.query.filter_by(list_id=list_id).update(
    dict(updated_on=datetime.now()))
    db.session.commit()
    list = List.query.filter_by(list_name=new_list_name,creator=current_user.username).first()

    return jsonify({'message':'List updated'}),200

@app.route('/api/list/<list_id>', methods=['DELETE'])
@token_required
def api_dellist(current_user, list_id): # delete list
    cards = Card.query.filter_by(list_id=list_id).all()
    for card in cards:
        db.session.delete(card)
    list = list.query.filter_by(list_id=list_id).first()
    db.session.delete(list)
    db.session.commit()
    return jsonify({'message':'Deck has been deleted'}),200
 
@app.route('/api/<list_id>')
@token_required
def api_return_list_name(current_user, list_id):
    list = list.query.filter_by(list_id=list_id,creator=current_user.user_id).first()
    listname=list.list_name
    return jsonify({"listname": listname})

#<------------------------------------------Cards------------------------------------------------>


@app.route('/api/cards/<list_id>')    
@token_required
def api_cards(current_user,list_id): # get all cards 
    cards = Card.query.filter_by(list_id=list_id).all()
    if cards:    
            return jsonify(cards_schema.dump(cards))
    return jsonify({"message":"No cards in list. Create a new one."}),400

@app.route('/api/card/<card_id>')    
@token_required
def api_get_card(current_user,card_id): # get one card 
    card = Card.query.filter_by(card_id=card_id).first()
    if card:    
            return jsonify(card_schema.dump(card))
    return jsonify({"message":"No cards found."}),400


@app.route('/api/newcard/<list_id>', methods=['POST'])
@token_required   
def api_newcard(current_user,list_id): # create new card
    title = request.form.get('title')
    content = request.form.get('content')
    deadline = request.form.get('deadline')

    if title == "" or content == "":
        return jsonify({'message':'Card cannot be empty. Please try again.'}),400
    
    card = Card.query.filter_by(title=title, content=content, list_id=list_id).first()
    if card:
        return jsonify({'message':'Card already exists in list.'}),400
    
    new_card = Card(
        creator_id= current_user.user_id,
        card_id=str(uuid.uuid4()),
        list_id=list_id,
        title=title,
        content=content,
        deadline=deadline,
        created_on=datetime.now()
    )
    db.session.add(new_card)
    db.session.commit()
    return jsonify({'message':'Card created'}),200

@app.route('/api/card/<card_id>', methods=['PUT'])
@token_required    
def api_editcard(current_user,card_id): #edit card
    card = Card.query.get_or_404(card_id)
    if card:
        return jsonify({'message':'Card not found.'}),200

    title = request.form.get('title')
    content = request.form.get('content')
    deadline = request.form.get('deadline')

    if title == "" and content == "" and deadline=="":
        return jsonify({'message':'No changes made, card remains same.'}),200

    card = Card.query.filter_by(title=title, content=content, list_id=card.list_id).first()
    if card:
        return jsonify({'message':'Card already exists in list.'}),400

    card = Card.query.get_or_404(card_id)
    Card.query.filter_by(card_id=card_id,
                     list_id=card.list_id).update(dict(title=title))
    Card.query.filter_by(card_id=card_id,
                     list_id=card.list_id).update(dict(content=content))
    Card.query.filter_by(card_id=card_id,
                     list_id=card.list_id).update(dict(deadline=deadline))
    db.session.commit()
    return jsonify({'message':'Card has been updated', 'list_id':card.list_id}),200

@app.route('/api/card/<card_id>', methods=['DELETE'])
@token_required
def api_delcard(current_user,card_id): #delete card
    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return jsonify({'message':'Card has been deleted'}),200


#<------------------------------------------Review and Time Update------------------------------------------------>

@app.route('/api/begin/<list_id>')
@token_required
def api_begin(current_user,list_id): # update last reviewd
    t = datetime.now()
    list = list.query.filter_by(list_id=list_id,creator=current_user.username).first()
    list.last_reviewed = t
    db.session.commit()
    return jsonify({'message':'Last reviewed updated'}),200

@app.route('/api/review/<card_id>', methods=["POST"])
@token_required
def api_review_next(current_user, card_id): #scoring 
    partialscore = request.form.get('partialscore') 
    card = Card.query.filter_by(card_id=card_id).first()
    card.partial = int(partialscore)
    db.session.commit() 
    cards = Card.query.filter_by(part_of_list=card.part_of_list).all()
    total = 0
    for cd in cards:
      if cd.partial== None:
        break
      else:
        total = total + cd.partial  
    count = Card.query.filter_by(part_of_list=card.part_of_list).count()
    new_score = int(total / count)  
    list.query.filter_by(list_id=card.part_of_list).update( dict(score=new_score))
    t =  datetime.datetime.now(tz=ZoneInfo('Asia/Kolkata')).strftime("%I:%M %p %d %b, %Y")
    list.query.filter_by(list_id=card.part_of_list).update( dict(last_reviewed=t))
    db.session.commit() 
    return jsonify({'message':'Partial Score and list Score Updated'}),200

#<------------------------------------------------------------------------------------------>

