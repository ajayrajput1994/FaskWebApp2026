# run.py
from flask import render_template, request, flash
from app import create_app
from app.extensions import db
from app.model import User

app = create_app('development')


@app.route("/")
def home():
    if request.args.get('create-admin'):
      user = User.query.filter_by(email='admin@example.com').first() 
      if not user:
        user = User(username='admin', email='admin@example.com', role='admin')
        user.set_password('Admin123')
        db.session.add(user)
        db.session.commit()
        print('admin user created.')
        flash(f'{user.role} role created now .', 'success')
      else:
        flash(f'{user.username} already exist in your db.', 'info')
    return render_template("base.html")


if __name__ == '__main__':
    app.run(debug=True)
