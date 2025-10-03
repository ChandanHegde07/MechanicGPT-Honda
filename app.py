import os                                       
from dotenv import load_dotenv                  
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

load_dotenv()                            

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db = SQLAlchemy(app)

class DiagnosticRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Request ID: {self.id}>'
    

@app.route("/")
def hello_world(name=None):
    return render_template('index.html', person=name)

@app.route("/test-db")
def test_db():
    try:
        new_request = DiagnosticRequest(
            user_query="This is a test query.",
            ai_response="This is a test response from the AI."
        )
        
        db.session.add(new_request)
        
        db.session.commit()
        
        return "<h1>Success: A new entry was added to the database.</h1>"
    except Exception as e:
        return f"<h1>Error: Could not add entry to database.</h1><p>{e}</p>"


if __name__ == '__main__':
    app.run(debug=True)