from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:@localhost/marketdb?charset=utf8mb4&connect_timeout=10'
db=SQLAlchemy(app)


@app.route('/')
@app.route('/home')
def homepage():
  return render_template('homepage.html')

class Items(db.Model):
  id=db.Column(db.Integer,primary_key=True)
  name=db.Column(db.String(50),unique=True,nullable=False)
  barcode=db.Column(db.String(12),unique=True,nullable=False)
  price=db.Column(db.Integer,nullable=False)


@app.route('/market')
def marketpage():
  items=Items.query.all()
  return render_template('market.html',item=items)

if __name__=='__main__':
  app.run(debug=True)
