
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)



from views import views as views_blueprint
app.register_blueprint(views_blueprint)

login_manager = LoginManager()
login_manager.login_view = 'views.login'
login_manager.init_app(app)

from models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

if __name__ == '__main__':
    app.run(debug=True, port= 8080)