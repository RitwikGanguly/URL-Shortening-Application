from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import string
import validators
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:cse204003@localhost/url_shortener'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(1000))
    short_url = db.Column(db.String(10), unique=True)

    def __init__(self, original_url, short_url):
        self.original_url = original_url
        self.short_url = short_url

def generate_short_url():
    characters = string.ascii_letters + string.digits
    while True:
        short_url = ''.join(random.choice(characters) for i in range(7))
        url = URL.query.filter_by(short_url=short_url).first()
        if not url:
            return short_url

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        original_url = request.form.get('url1')
        print("hi")
        if validators.url(original_url):
            existing_url = URL.query.filter_by(original_url=original_url).first()
            if existing_url:
                return render_template("error.html", existing_url=existing_url.original_url, short_url=existing_url.short_url)
            else:
                short_url = generate_short_url()
                new_url = URL(original_url=original_url, short_url=short_url)
                db.session.add(new_url)
                db.session.commit()
                return render_template('success.html', short_url=short_url)
        else:
            flash('Invalid URL. Please try again.', 'error')

        return redirect(url_for('home'))

    return render_template('home.html')

# @app.route('/shorten', methods=['POST'])
# def shorten():
#     original_url = request.form.get('url')
#     short_url = generate_short_url()
#     new_url = URL(original_url=original_url, short_url=short_url)
#     db.session.add(new_url)
#     db.session.commit()
#     return render_template('success.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    url = URL.query.filter_by(short_url=short_url).first_or_404()
    return redirect(url.original_url)

@app.route('/history')
def history():
    urls = URL.query.all()
    return render_template('history.html', urls=urls)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
