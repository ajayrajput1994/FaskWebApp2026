# run.py
from flask import render_template
from app import create_app
# from app.extensions import db
# from app.model import User

app = create_app('development')


@app.route("/")
def home():
    # user = User(username='editor', email='editor@example.com', role='editor')
    # user.set_password('Editor123')
    # db.session.add(user)
    # db.session.commit()
    # print('editor user created.')
    return render_template("base.html")


if __name__ == '__main__':
    app.run(debug=True)
