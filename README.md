# Navigate to your project folder first
mkdir my_flask_app
cd my_flask_app

# Create the virtual environment
# "venv" at the end is the folder name — you can name it anything,
# but "venv" is the universal convention
python -m venv venv
# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
# set virtual inviroment if not work abvoe commands
1. pip install virtualenv
2. virtualenv env
   if error:
   virtualenv : The term 'virtualenv' is not recognized as the name of a cmdlet, function, script file, or operable program. Check the spelling
   of the name, or if a path was included, verify that the path is correct and try again.
   then :
   2.1 python -m virtualenv env
   2.2 python -m venv env
   2.3 .\env\Scripts\activate

pip install flask
pip install flask-sqlalchemy flask-login flask-mail
pip list          # shows only packages in this venv
which python      # Mac/Linux: shows path inside venv/
where python      # Windows: shows path inside venv\
pip freeze > requirements.txt

# Teammate clones your repo and runs:
python -m venv venv
source venv/bin/activate        # or venv\Scripts\activate on Windows
pip install -r requirements.txt # installs everything from requirements.txt
deactivate
#=============================
mkdir app\auth
mkdir app\dashboard
mkdir app\templates\auth
mkdir app\templates\dashboard
mkdir app\static

cd FlaskWebApp
touch run.py
touch app/__init__.py app/extensions.py app/config.py
touch app/auth/__init__.py app/auth/routes.py app/auth/forms.py
touch app/dashboard/__init__.py app/dashboard/routes.py
touch app/templates/base.html app/templates/auth/login.html app/templates/dashboard/index.html


# Make sure your venv is active, then:
pip install flask flask-sqlalchemy flask-login flask-mail flask-wtf python-dotenv

python run.py

# upgrade your pip 
python.exe -m pip install --upgrade pip
# =======================tseting===========================
# Run all tests with verbose output
pytest -v
# Run only one file
pytest tests/test_auth.py -v
# Run one specific test function
pytest tests/test_auth.py::test_login_success -v
# Show print() output during tests (useful for debugging)
pytest -v -s
# Show a coverage report
pip install pytest-cov
pytest --cov=app --cov-report=term-missing
# ========================testing end=================

# ========================Query reference start=================
# ── Basic fetch ──────────────────────────────────────────────────
User.query.get(1)                           # by primary key (fastest)
User.query.all()                            # all rows as a list
User.query.first()                          # first row or None
User.query.count()                          # COUNT(*) — efficient

# ── Filtering ────────────────────────────────────────────────────
User.query.filter_by(email='a@b.com').first()    # exact match, keyword arg
User.query.filter(User.email == 'a@b.com').first() # same, expression style
User.query.filter(User.age > 18).all()           # comparison
User.query.filter(User.role.in_(['admin','editor'])).all()  # IN list
User.query.filter(User.username.like('%ali%')).all()        # LIKE
User.query.filter(User.bio.ilike('%flask%')).all()          # case-insensitive
User.query.filter(User.deleted_at == None).all()            # IS NULL

# ── Chaining filters (AND) ───────────────────────────────────────
User.query.filter(User.is_active == True,
                  User.role == 'admin').all()
# or:
User.query.filter_by(is_active=True, role='admin').all()

# ── OR / NOT ─────────────────────────────────────────────────────
from sqlalchemy import or_, and_, not_
User.query.filter(or_(User.role == 'admin',
                      User.role == 'editor')).all()

# ── Ordering ─────────────────────────────────────────────────────
Post.query.order_by(Post.created_at.desc()).all()     # newest first
Post.query.order_by(Post.title.asc()).all()            # A→Z

# ── Limiting / pagination ────────────────────────────────────────
Post.query.limit(10).all()                             # first 10
Post.query.offset(20).limit(10).all()                  # rows 21-30
page = Post.query.order_by(Post.created_at.desc()) \
              .paginate(page=2, per_page=10)
# page.items  → list of posts for this page
# page.total  → total count
# page.pages  → total page count
# page.has_next, page.has_prev → booleans

# ── Create, update, delete ───────────────────────────────────────
# Create
user = User(username='ali', email='ali@x.com')
user.set_password('secret')
db.session.add(user)
db.session.commit()

# Update — modify attributes, then commit
user = User.query.get(1)
user.bio = 'Updated bio'
db.session.commit()           # no db.session.add() needed for existing rows

# Delete
user = User.query.get(1)
db.session.delete(user)
db.session.commit()
# If cascade='all, delete-orphan' is set on relationships,
# their posts, profile, etc. are deleted automatically.
# ========================Query reference end=================

# ================usefull commands for daily needs=================
# See exactly where your DB currently is
flask db current
# See the full history of migrations
flask db history --verbose
# Check what would change WITHOUT applying it
flask db migrate -m "test" --sql     # prints SQL to stdout, doesn't run it
# Roll back one step
flask db downgrade
# Roll back to a specific version (copy the hash from flask db history)
flask db downgrade a3f9c1
# After git pull — always run this to apply teammates' new migrations
flask db upgrade
# If your DB is out of sync with migration history (rare, happens after manual edits)
flask db stamp head     # tells Alembic "this DB is already at latest, trust me"

pip install flask-wtf email-validator

======================jinja2 start====================================
-------------Template inheritance — {% extends %} + {% block %}---------------
{# Parent defines placeholders: #}
{% block title %}Default title{% endblock %}
{% block content %}{% endblock %}

{# Child fills them in: #}
{% extends 'base.html' %}
{% block title %}My page{% endblock %}
{% block content %}
  <p>My content here.</p>
{% endblock %}

------------Macros — {% macro %} + {% from ... import %}--------------------
{# Define once in macros/forms.html: #}
{% macro alert(message, type='info') %}
  <div class="alert alert-{{ type }}">{{ message }}</div>
{% endmacro %}

{# Import and call anywhere: #}
{% from 'macros/forms.html' import alert %}
{{ alert('Saved!', type='success') }}
{{ alert('Error occurred.', type='danger') }}

--------------Built-in filters — {{ value|filter }}-------------------
{# String filters #}
{{ user.username|upper }}           {# ALI_DEV #}
{{ user.username|lower }}           {# ali_dev #}
{{ user.username|capitalize }}      {# Ali_dev #}
{{ user.username|truncate(20) }}    {# ali_dev_with_lon... #}
{{ post.body|striptags }}           {# removes all HTML tags #}
{{ post.body|safe }}                {# renders HTML — only use on trusted content! #}

{# Number filters #}
{{ price|round(2) }}                {# 19.99 #}
{{ count|default(0) }}             {# 0 if count is None #}

{# Date filter (needs Flask-Moment or strftime) #}
{{ user.created_at.strftime('%d %b %Y') }}   {# 01 Jan 2025 #}

{# List filters #}
{{ items|length }}                  {# 5 #}
{{ items|first }}                   {# first item #}
{{ items|last }}                    {# last item #}
{{ items|join(', ') }}              {# a, b, c #}
{{ items|sort }}                    {# sorted list #}
{{ items|reverse|list }}            {# reversed list #}
{{ user.created_at|time_ago }} custom filter

-----------------Control flow — {% if %}, {% for %}, {% set %}------------
{# Conditional with role check #}
{% if current_user.is_authenticated %}
  {% if current_user.has_role('admin') %}
    <a href="/admin">Admin panel</a>
  {% elif current_user.has_role('editor') %}
    <a href="/editor">Editor panel</a>
  {% else %}
    <p>Welcome, viewer.</p>
  {% endif %}
{% endif %}

{# Loop with loop variable #}
{% for user in users %}
  <tr class="{{ 'row--even' if loop.even else 'row--odd' }}">
    <td>{{ loop.index }}</td>        {# 1-based position #}
    <td>{{ user.username }}</td>
    {% if loop.last %}
      <td>← last row</td>
    {% endif %}
  </tr>
{% else %}
  <tr><td colspan="3">No users found.</td></tr>
{% endfor %}

{# Set a variable #}
{% set page_title = 'Admin Panel' %}
{% set user_count = users|length %}
==========================jinja2 end===========================

=====================pytest=============================
# Run all tests with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing -v

# Run one specific file
pytest tests/test_auth.py -v

# Run one specific class
pytest tests/test_dashboard.py::TestAdminActions -v

# Run one specific test
pytest tests/test_auth.py::TestLogin::test_login_success -v

# Stop after first failure (useful while fixing bugs)
pytest -x -v
====================pytest end====================
gunicorn
psycopg2-binary
redis
flask-bcrypt