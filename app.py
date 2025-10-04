import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from ai_core.rag_pipeline import create_rag_chain

load_dotenv()

app = Flask(__name__)

# Database Configuration (no changes)
db_url = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Initialize RAG Chain (no changes)
print("Initializing RAG chain... This may take a moment.")
rag_chain = create_rag_chain()
print("RAG chain initialized successfully.")

# Database Model (no changes)
class DiagnosticRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_query = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Request ID: {self.id}>'

# --- UPDATED MAIN ROUTE ---
@app.route("/")
def hello_world():
    # Fetch all history from the database, newest first.
    history = DiagnosticRequest.query.order_by(DiagnosticRequest.id.desc()).all()
    # Pass the history to the template
    return render_template('index.html', history=history)

# --- UPDATED DIAGNOSE ROUTE ---
@app.route('/diagnose', methods=['POST'])
def diagnose():
    question = request.form['symptom']
    answer = rag_chain.invoke(question)

    # --- NEW: SAVE TO DATABASE ---
    try:
        new_request = DiagnosticRequest(user_query=question, ai_response=answer)
        db.session.add(new_request)
        db.session.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
        db.session.rollback() # Roll back the session in case of error
    # --- END SAVE TO DATABASE ---

    return render_template('result.html', question=question, answer=answer)

# ... (You can now safely delete the old @app.route("/test-db") function if you haven't already) ...

if __name__ == '__main__':
    app.run(debug=True)