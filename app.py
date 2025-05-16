from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
from dotenv import load_dotenv
from flask_cors import CORS
import smtplib
from email.message import EmailMessage

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# CORS
CORS(app, origins=["http://localhost:3000"])

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# In-memory user store
users = {}

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(user_id):
    user = users.get(user_id)
    if user:
        return User(user_id, user['username'], user['password_hash'])
    return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in [u['username'] for u in users.values()]:
            flash('Username already exists')
            return redirect(url_for('register'))
        user_id = str(len(users) + 1)
        users[user_id] = {
            'username': username,
            'password_hash': generate_password_hash(password)
        }
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user_id, user in users.items():
            if user['username'] == username and check_password_hash(user['password_hash'], password):
                login_user(User(user_id, username, user['password_hash']))
                return redirect(url_for('chat'))
        flash('Invalid credentials')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/account')
@login_required
def account():
    return render_template('account.html', username=current_user.username)

# Lazy-load models and Pinecone
embedding_model = None
pinecone_index = None

@app.route("/")
@login_required
def chat():
    return render_template("chat.html", username=current_user.username)

@app.route("/query", methods=["POST"])
@login_required
def query():
    global embedding_model, pinecone_index
    try:
        data = request.get_json()
        user_question = data.get("query", "")
        print("Received:", user_question)

        # Lazy load embedding model
        if embedding_model is None:
            embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Lazy load Pinecone
        if pinecone_index is None:
            pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            pinecone_index = pc.Index("leo")

        # Step 1: Embed the question
        query_embedding = embedding_model.encode(user_question).tolist()

        # Step 2: Query Pinecone
        results = pinecone_index.query(vector=query_embedding, top_k=3, include_metadata=True)
        matches = results.get("matches", [])

        if not matches:
            return jsonify({"answer": "❌ Sorry, I couldn't find any relevant information."})

        answer = matches[0]["metadata"].get("text", "⚠️ No data found.")
        print("Bot response:", answer)
        return jsonify({"answer": answer})

    except Exception as e:
        print("Error in /query:", str(e))
        return jsonify({"answer": f"⚠️ Internal error: {str(e)}"}), 500

@app.route('/courses')
@login_required
def courses():
    return render_template('courses.html', username=current_user.username)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    try:
        email = request.form.get('email')
        if not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
        
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = 'New Newsletter Subscription'
        msg['From'] = 'noreply@yourdomain.com'  # Replace with your domain
        msg['To'] = 'mohdaibad04@gmail.com'  # This is the recipient email
        msg.set_content(f"New subscription from: {email}")
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            # You'd need to set up an app password for this Gmail account
            # or enable less secure apps (not recommended)
            smtp.login(os.getenv('EMAIL_USER', 'your-email@gmail.com'), 
                      os.getenv('EMAIL_PASSWORD', 'your-app-password'))
            smtp.send_message(msg)
        
        return jsonify({"success": True, "message": "Subscription successful!"})
    except Exception as e:
        print("Error in /subscribe:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if not name or not email or not message:
            return jsonify({"success": False, "message": "Name, email and message are required"}), 400
        
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = f'New Message from {name}'
        msg['From'] = email
        msg['To'] = 'mohdaibad04@gmail.com'
        
        # Email body with sender's information
        email_content = f"""
        Name: {name}
        Email: {email}
        
        Message:
        {message}
        """
        msg.set_content(email_content)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(os.getenv('EMAIL_USER', 'your-email@gmail.com'), 
                      os.getenv('EMAIL_PASSWORD', 'your-app-password'))
            smtp.send_message(msg)
        
        return jsonify({"success": True, "message": "Message sent successfully!"})
    except Exception as e:
        print("Error in /send-message:", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
