from app import app, db, bcrypt
from sqlalchemy import and_
import datetime
import jwt
import uuid


class User(db.Model):
    """table schema"""
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    post = db.relationship('Post', backref='post', lazy='dynamic')
    community = db.relationship('Community', backref='community', lazy='dynamic')
    steps = db.relationship('Steps', backref='step', lazy='dynamic')

    def __init__(self, email, password, first_name, last_name, username):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')) \
            .decode('utf-8')
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.registered_on = datetime.datetime.now()
        self.id = uuid.uuid4().__str__()

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

    @staticmethod
    def getusername(user_id):
        """
        Check a user by their email address
        :param user_id:
        :return:
        """
        user = User.query.filter_by(id=user_id).first()

        return user.username


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String, primary_key=True)
    # firebase storage
    image_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    create_at = db.Column(db.DateTime, nullable=False)
    likes = db.Column(db.Integer, nullable=True)
    comments = db.relationship('Comments', backref='comments', lazy='dynamic')
    challenge = db.relationship('Challenge', backref='challenges', lazy='dynamic')

    def __init__(self, description, image_url, user_id):
        self.image_url = image_url
        self.description = description
        self.user_id = user_id
        self.create_at = datetime.datetime.now()
        self.likes = 0
        self.id = uuid.uuid4().__str__()

    def save(self):
        """
        Persist a post in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()
        db.session.refresh(self)
        return self.id

    @staticmethod
    def like(post_id):
        post = Post.query.filter_by(id=post_id).first()
        post.likes = post.likes + 1
        return post.likes

    @staticmethod
    def get_posts(user_id):
        post = Post.query.filter_by(user_id=user_id).all()
        return post

    @staticmethod
    def get_post_count(user_id):
        post = Post.query.filter_by(user_id=user_id).all()
        post_count = 0
        for p in post:
            post_count = post_count + 1
        return post_count

    @staticmethod
    def get_post_image_url(post_id):
        post = Post.query.filter_by(id=post_id).first()
        return post.image_url


class Comments(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.String, primary_key=True)
    comment = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    post_id = db.Column(db.String, db.ForeignKey('posts.id'))
    create_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, comment, post_id, user_id):
        self.user_id = user_id
        self.comment = comment
        self.post_id = post_id
        self.create_at = datetime.datetime.now()
        self.id = uuid.uuid4().__str__()

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getcomments(post_id):
        return Comments.query.filter_by(post_id=post_id).all()

    @staticmethod
    def getallcomments():
        return Comments.query.all()


class Likes(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    post_id = db.Column(db.String, db.ForeignKey('posts.id'))
    create_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id
        self.create_at = datetime.datetime.now()
        self.id = uuid.uuid4().__str__()

    def save(self):
        Post.like(post_id=self.post_id)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def getlikers(post_id):
        return Likes.query.filter_by(post_id=post_id).all()

    @staticmethod
    def getlikers_count(post_id):
        likes = Likes.query.filter_by(post_id=post_id).all()
        likes_count = 0
        for l in likes:
            likes_count = likes_count + 1
        return likes_count


class Community(db.Model):
    __tablename__ = 'community'

    user_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    community_id = db.Column(db.String, primary_key=True)

    def __init__(self, user_id, community_id):
        self.user_id = user_id
        self.community_id = community_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_community(user_id):
        return Community.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_community_count(user_id):
        community = Community.query.filter_by(user_id=user_id).all()
        community_count = 0
        for c in community:
            community_count = community_count + 1
        return community_count


class Steps(db.Model):
    """
    Table to store user's steps
    """
    __tablename__ = 'steps'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    steps_no = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, steps_no):
        self.user_id = user_id
        self.steps_no = steps_no
        self.date = datetime.datetime.now().date()
        self.id = uuid.uuid4().__str__()

    def save(self):
        """
        Persist the steps in the database
        :param steps:
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def update_if_instance_exist(current_date, user_id, steps):
        instance = Steps.query.filter(
            and_(Steps.user_id == user_id, Steps.date == current_date)).first()
        if instance:
            instance.steps_no = steps
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_steps(user_id, limit):
        return Steps.query.filter_by(user_id=user_id).limit(limit)


class Challenge(db.Model):
    """
    Table to store challenges
    """
    __tablename__ = 'challenges'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    role = db.Column(db.String(10), nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    steps = db.Column(db.Integer, nullable=False)
    challenge_name = db.Column(db.String(255), nullable=False)
    challenge_description = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    post_id = db.Column(db.String, db.ForeignKey('posts.id'))

    def __init__(self, user_id, post_id, goal, challenge_name, challenge_description, end_date: dict,
                 steps=0, role="creator", start_date=datetime.datetime.now().date()):
        self.user_id = user_id
        self.steps = steps
        self.start_date = start_date
        self.goal = goal
        self.role = role
        self.challenge_name = challenge_name
        self.challenge_description = challenge_description
        self.end_date = datetime.date(int(end_date['year']), int(end_date['month']), int(end_date['day']))
        self.post_id = post_id
        self.id = uuid.uuid4().__str__()

    def save(self):
        """
        Persist the steps in the database
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def join_challenge(fields: dict):
        # method for joining challenge
        user_id = fields['user_id']
        post_id = fields['post_id']
        start_date = fields['start_date']
        # start_date = datetime.date(int(date1[0]), int(date1[1]), int(date1[2]))
        goal = fields['goal']
        challenge_name = fields['challenge_name']
        challenge_description = fields['challenge_description']
        end_date = {}
        current_date = fields['current_date']
        truncate_space = str(fields['end_date']).split(' ')
        date2 = truncate_space[0].split('-')
        end_date['year'] = date2[0]
        end_date['month'] = date2[1]
        end_date['day'] = date2[2]
        # e_date = datetime.date(int(current_date[0]), int(current_date[1]), int(current_date[2]))
        record = Steps.query.filter(and_(Steps.date <= current_date, Steps.date >= start_date,
                                         Steps.user_id == user_id))
        steps = 0
        for item in record:
            steps += item.steps_no
        Challenge(user_id=user_id, post_id=post_id, goal=goal, challenge_name=challenge_name,
                  challenge_description=challenge_description,
                  end_date=end_date, steps=steps, role="challenger", start_date=start_date).save()

    @staticmethod
    def get_users_performance(challenge_id):
        return Challenge.query.filter(Challenge.id == challenge_id).order_by(Challenge.steps.desc()).all()

    @staticmethod
    def get_challenge_by_user_id(user_id):
        return Challenge.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_creator(challenge_id):
        return Challenge.query.filter(
            and_(Challenge.id == challenge_id, Challenge.role == "creator")).first()

    @staticmethod
    def check_postid(post_id):
        return Challenge.query.filter_by(post_id=post_id).first()

    @staticmethod
    def check_join(message, username):
        check_username = message[1:]
        return True if '@' in message and check_username == username else False

    @staticmethod
    def get_all():
        return Challenge.query.order_by(Challenge.steps.desc()).all()


"""class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_deleted = db.Column(db.String, nullable=False)
    message = db.Column(db.String, nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)
    community_invitee = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenge.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    is_challenge = db.Column(db.String, nullable=False)
    is_post_related = db.Column(db.String, nullable=False)
    is_community_request = db.Column(db.String, nullable=False)

    def __init__(self, user_id, is_deleted="False", message=None, community_invitee=None, challenge_id=None,
                 post_id=None, is_challenge="False", is_post_related="False", is_community_request="False"):
        self.user_id = user_id
        self.is_deleted = is_deleted
        self.create_at = datetime.datetime.now()
        self.message = message
        self.is_challenge = is_challenge
        self.is_post_related = is_post_related
        self.is_community_request = is_community_request
        if community_invitee:
            self.community_invitee = community_invitee
        if challenge_id:
            self.challenge_id = challenge_id
        if post_id:
            self.post_id = post_id

    def save(self):
        
        Persist the steps in the database
        :param notifications:
        :return:
        
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_notifications(user_id):
        return Notification.query.filter(
            and_(Notification.user_id == user_id, Notification.is_deleted == "False")).all()"""
