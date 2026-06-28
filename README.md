# Follow basic steps to run this app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
python run.py