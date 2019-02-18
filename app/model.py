from app import app, db, bcrypt
import datetime
import jwt


class User(db.Model):
    """table schema"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    post = db.relationship('Post', backref='post', lazy='dynamic')
    community = db.relationship('Community', backref='community', lazy='dynamic')

    def __init__(self, email, password, first_name, last_name, username):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')) \
            .decode('utf-8')
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.registered_on = datetime.datetime.now()

    def save(self):
        """
        Persist the user in the database
        :param user:
        :return:
        """
        db.session.add(self)
        db.session.commit()
        return self.encode_auth_token(self.id)

    def encode_auth_token(self, user_id):
        """
        Encode the Auth token
        :param user_id: User's Id
        :return:
        """
        try:
            payload = {
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config['SECRET_KEY'],
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(token):
        """
        Decoding the token to get the payload and then return the user Id in 'sub'
        :param token: Auth Token
        :return:
        """
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
            is_token_blacklisted = BlackListToken.check_blacklist(token)
            if is_token_blacklisted:
                return 'Token was Blacklisted, Please login In'
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired, Please sign in again'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please sign in again'

    @staticmethod
    def get_by_id(user_id):
        """
        Filter a user by Id.
        :param user_id:
        :return: User or None
        """
        return User.query.filter_by(id=user_id).first()

    @staticmethod
    def get_by_email(email):
        """
        Check a user by their email address
        :param email:
        :return:
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username):
        """
        Check a user by their email address
        :param email:
        :return:
        """
        return User.query.filter_by(username=username).first()


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # firebase storage
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    create_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, description, image_url, user_id):
        self.image_url = image_url
        self.description = description
        self.user_id = user_id
        self.create_at = datetime.datetime.now()

    def save(self):
        """
        Persist a post in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_posts(user_id):
        post = Post.query.filter_by(user_id=user_id).all()

        return post


class Community(db.Model):
    __tablename__ = 'community'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    community_id = db.Column(db.Integer, primary_key=True)

    def __init__(self, user_id, community_id):
        self.user_id = user_id
        self.community_id = community_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_community(user_id):
        return Community.query.filter_by(user_id=user_id).all()


class BlackListToken(db.Model):
    """
    Table to store blacklisted/invalid auth tokens
    """
    __tablename__ = 'blacklist_token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(255), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def blacklist(self):
        """
        Persist Blacklisted token in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklist(token):
        """
        Check to find out whether a token has already been blacklisted.
        :param token: Authorization token
        :return:
        """
        response = BlackListToken.query.filter_by(token=token).first()
        if response:
            return True
        return False
