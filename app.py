from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    best_score = db.Column(db.Integer, default=0)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for('register'))
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('quiz'))
        else:
            flash("Invalid credentials")
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for('login'))

# Example quiz questions
quiz_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Rome"],
        "answer": "Paris",
        "explanation": "Paris is the capital and most populous city of France."
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer": "Mars",
        "explanation": "Mars is called the Red Planet because of its reddish appearance due to iron oxide on its surface."
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Mark Twain", "William Shakespeare", "Charles Dickens", "Jane Austen"],
        "answer": "William Shakespeare",
        "explanation": "'Romeo and Juliet' is a famous tragedy written by William Shakespeare."
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"],
        "answer": "Pacific Ocean",
        "explanation": "The Pacific Ocean is the largest and deepest of Earth's oceanic divisions."
    },
    {
        "question": "In what year did the first man land on the moon?",
        "options": ["1969", "1959", "1979", "1989"],
        "answer": "1969",
        "explanation": "Neil Armstrong landed on the moon in 1969 during the Apollo 11 mission."
    },
    {
        "question": "What is the powerhouse of the cell?",
        "options": ["Nucleus", "Ribosome", "Mitochondria", "Chloroplast"],
        "answer": "Mitochondria",
        "explanation": "Mitochondria are known as the powerhouse of the cell because they generate most of the cell's energy."
    },
    {
        "question": "Which language is primarily spoken in Brazil?",
        "options": ["Spanish", "Portuguese", "French", "English"],
        "answer": "Portuguese",
        "explanation": "Portuguese is the official and most widely spoken language in Brazil."
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Leonardo da Vinci", "Pablo Picasso", "Michelangelo"],
        "answer": "Leonardo da Vinci",
        "explanation": "The Mona Lisa was painted by Leonardo da Vinci in the early 16th century."
    },
    {
        "question": "Which gas do plants absorb from the atmosphere?",
        "options": ["Oxygen", "Nitrogen", "Carbon Dioxide", "Hydrogen"],
        "answer": "Carbon Dioxide",
        "explanation": "Plants absorb carbon dioxide from the atmosphere for use in photosynthesis."
    },
    {
        "question": "What is the freezing point of water?",
        "options": ["0°C", "32°C", "100°C", "212°C"],
        "answer": "0°C",
        "explanation": "Water freezes at 0 degrees Celsius (32 degrees Fahrenheit) under standard conditions."
    }
]

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'POST':
        score = 0
        results = []
        for i, q in enumerate(quiz_questions):
            selected = request.form.get(f'question-{i}')
            correct = selected == q['answer']
            if correct:
                score += 1
            results.append({
                'question': q['question'],
                'selected': selected,
                'correct_answer': q['answer'],
                'is_correct': correct,
                'explanation': q.get('explanation', '')
            })
        # Update best score
        if score > current_user.best_score:
            current_user.best_score = score
            db.session.commit()
        return render_template('quiz_result.html', results=results, score=score, total=len(quiz_questions), best_score=current_user.best_score)
    return render_template('quiz.html', questions=quiz_questions)

@app.route('/faq')
def faq():
    return render_template('faq.html')

# Ensure tables are created before the app runs
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)