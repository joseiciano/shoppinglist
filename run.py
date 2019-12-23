from pricechecker import app

if __name__ == '__main__':
    app.run(debug=True)


# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_bcrypt import Bcrypt
# from flask_login import LoginManager

# app = Flask(__name__)
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# loginManager = LoginManager(app)
# loginManager.login_view = "login"
# loginManager.login_message_category = "info"

# from pricechecker import routes

# if __name__ == '__main__':
#     app.run(debug=True)
