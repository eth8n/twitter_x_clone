import os
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    url_for,
    redirect,
    flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object("project.config.Config")
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Tweet(db.Model):
    __tablename__ = "tweets"

    tweet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    likes_count = db.Column(db.Integer, default=0)
    retweets_count = db.Column(db.Integer, default=0)

    # Relationship with User
    user = db.relationship('User', backref=db.backref('tweets', lazy=True))


@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    # Get paginated tweets with user information
    tweets = Tweet.query\
        .join(User)\
        .order_by(Tweet.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    return render_template('index.html', tweets=tweets)


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('create_account.html')
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('create_account.html')
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('create_account.html')
        # Create new user
        try:
            new_user = User(username=username, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            # Log the user in
            login_user(new_user)
            return redirect(url_for('index'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while creating your account')
            return render_template('create_account.html')
    return render_template('create_account.html')


@app.route("/create_message", methods=["GET", "POST"])
@login_required
def create_message():
    if request.method == "POST":
        content = request.form.get('content')
        if not content:
            flash('Message cannot be empty')
            return render_template('create_message.html')
        if len(content) > 280:
            flash('Message cannot be longer than 280 characters')
            return render_template('create_message.html')
        try:
            new_tweet = Tweet(
                user_id=current_user.user_id,
                content=content
            )
            db.session.add(new_tweet)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while creating your message')
            return render_template('create_message.html')
    return render_template('create_message.html')


@app.route("/search")
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    if query:
        # Use RUM index for fast fulltext search with ordering by rank and then date
        search_query = db.text("""
            SELECT
                t.tweet_id,
                t.user_id,
                t.content,
                t.created_at,
                t.likes_count,
                t.retweets_count,
                u.username,
                u.email,
                u.password_hash,
                ts_headline(
                    'english',
                    t.content,
                    plainto_tsquery('english', :query),
                    'StartSel=<b>,StopSel=</b>,MaxFragments=2,MaxWords=30'
                ) as highlighted_content
            FROM tweets t
            INNER JOIN users u ON t.user_id = u.user_id
            WHERE t.content_tsv @@ plainto_tsquery('english', :query)
            ORDER BY
                ts_rank_cd(t.content_tsv, plainto_tsquery('english', :query)) DESC,
                t.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        # Use a simpler but still accurate count query
        count_query = db.text("""
            SELECT COUNT(*)
            FROM tweets t
            WHERE t.content_tsv @@ plainto_tsquery('english', :query)
        """)

        # Calculate offset
        offset = (page - 1) * per_page

        # Execute queries
        total = db.session.execute(count_query, {'query': query}).scalar()
        results = db.session.execute(search_query, {
            'query': query,
            'limit': per_page,
            'offset': offset
        }).fetchall()
        # Convert results to Tweet objects
        tweets = []
        for row in results:
            tweet = Tweet(
                tweet_id=row.tweet_id,
                user_id=row.user_id,
                content=row.content,
                created_at=row.created_at,
                likes_count=row.likes_count,
                retweets_count=row.retweets_count
            )
            # Create a User object with all required fields
            user = User(
                username=row.username,
                email=row.email,
                password=''  # We don't need the actual password for display
            )
            user.password_hash = row.password_hash  # Set the password hash directly
            tweet.user = user
            tweet.highlighted_content = row.highlighted_content
            tweets.append(tweet)

        # Create a simple pagination object
        class SimplePagination:
            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total + per_page - 1) // per_page

            @property
            def has_prev(self):
                return self.page > 1

            @property
            def has_next(self):
                return self.page < self.pages

            @property
            def prev_num(self):
                return self.page - 1

            @property
            def next_num(self):
                return self.page + 1

            def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
                last = 0
                for num in range(1, self.pages + 1):
                    if (num <= left_edge or (num > self.page - left_current - 1 and num < self.page + right_current) or num > self.pages - right_edge):
                        if last + 1 != num:
                            yield None
                        yield num
                        last = num
        tweets = SimplePagination(tweets, page, per_page, total)
    else:
        tweets = None

    return render_template('search.html', query=query, tweets=tweets)
