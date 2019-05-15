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
    profile_pic = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    post = db.relationship('Post', backref='post', lazy='dynamic')
    community = db.relationship('Community', backref='community', lazy='dynamic')
    steps = db.relationship('Steps', backref='step', lazy='dynamic')
    usersetting = db.relationship('UserSetting', backref='usersetting', lazy='dynamic')
    foodhistory = db.relationship('FoodHistory', backref='foodhistory', lazy='dynamic')

    def __init__(self, email, password, first_name, last_name, username, gender, age, profile_pic):
        self.email = email
        self.password = bcrypt.generate_password_hash(password, app.config.get('BCRYPT_LOG_ROUNDS')) \
            .decode('utf-8')
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.registered_on = datetime.datetime.now()
        self.age = age
        self.gender = gender
        self.profile_pic = profile_pic
        self.id = uuid.uuid4().__str__()

    def save(self):
        """
        Persist the user in the database
        :param user:
        :return:
        """
        db.session.add(self)
        db.session.commit()
        settings = UserSetting(self.id)
        settings.save()
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

    @staticmethod
    def get_profile_pic(user_id):
        user = User.query.filter_by(id=user_id).first()
        return user.profile_pic


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
        post = Post.query.filter_by(user_id=user_id).order_by(Post.create_at.desc()).all()
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

    @staticmethod
    def already_community(community_id, user_id):
        instance = Community.query.filter(
            and_(Community.user_id == user_id, Community.community_id == community_id)).first()
        return instance


class Steps(db.Model):
    """
    Table to store user's steps
    """
    __tablename__ = 'steps'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    steps_no = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, user_id, steps_no, date):
        self.user_id = user_id
        self.steps_no = steps_no
        self.date = date
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
        return Steps.query.filter_by(user_id=user_id).order_by(Steps.date.desc()).limit(limit)


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
    def get_users_performance(post_id):
        return Challenge.query.filter(Challenge.post_id == post_id).order_by(Challenge.steps.desc()).all()

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

    @staticmethod
    def check_user_joined(user_id, post_id):
        return Challenge.query.filter(
            and_(Challenge.user_id == user_id, Challenge.post_id == post_id)).first()

    @staticmethod
    def get_challenge_within_date_by_user_id(user_id, date_now):
        return Challenge.query.filter(and_(Challenge.end_date >= date_now, Challenge.user_id == user_id)).all()

    @staticmethod
    def update_challenge_steps(challenge_id, steps):
        instance = Challenge.query.filter_by(id=challenge_id).first()
        instance.steps = int(instance.steps) + int(steps)
        db.session.commit()

    @staticmethod
    def get_user_steps_by_challenge(current_date, start_date, user_id):
        record = Steps.query.filter(and_(Steps.date <= current_date, Steps.date >= start_date,
                                         Steps.user_id == user_id))
        steps = 0
        for item in record:
            steps += int(item.steps_no)
        return steps


class UserSetting(db.Model):
    __tablename__ = "usersetting"
    user_id = db.Column(db.String(255), primary_key=True, foreign_key=True, required=True)
    average_weight = db.Column(db.String, nullable=False)
    height = db.Column(db.String, nullable=False)
    goal_weight = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    daily_calorie_goal = db.Column(db.String, nullable=False)
    weekly_calorie_goal = db.Column(db.Integer, nullable=False)
    goal_calorie = db.Column(db.Integer, nullable=False)
    is_diabetic = db.Column(db.String, nullable=False)
    activity_level = db.Column(db.String, nullable=False)

    def __init__(self, user_id):
        self.user_id = user_id
        """self.average_weight = average_weight
        self.goal_weight = goal_weight
        self.weekly_goal = weekly_goal
        self.net_calorie_goal = net_calorie_goal
        self.is_diabetic = is_diabetic
        self.image_url = image_url"""

    def save(self):
        db.session.add(self)
        db.session.commit()


    @staticmethod
    def get_user_settings(user_id):
        return UserSetting.query.filterby(user_id=user_id).first()

    @staticmethod
    def update(user_id, average_weight, goal_weight, is_diabetic, height, activity_level):

        instance = UserSetting.query.filter(UserSetting.user_id == user_id).first()
        if instance:
            instance.average_weight = average_weight
            instance.goal_weight = goal_weight
            instance.is_diabetic = is_diabetic
            instance.height = height
            instance.activity_level = activity_level
            instance.duration = goal_weight - average_weight
            instance.daily_calorie_goal = UserSetting.get_net_calorie(user_id, goal_weight, average_weight)
            instance.weekly_calorie_goal = UserSetting.get_net_calorie(user_id, goal_weight, average_weight) * 7

            db.session.commit()
            return True
        return False

    @staticmethod
    def centimetertoinches(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        inches = user_setting.height / 2.54
        return inches

    @staticmethod
    def kgtopounds(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        pounds = user_setting.average_weight * 2.205
        return pounds

    @staticmethod
    def calculate_bmr(user_id):
        height = UserSetting.centimetertoinches(user_id)
        average_weight = UserSetting.kgtopounds(user_id)
        user = User.query.filter_by(id=user_id).first()
        user_gender = user.gender
        user_age = user.age

        if user_gender == 'M':
            bmr = (12.7 * height) + (6.23 * average_weight) - (6.8 * user_age)
            total_bmr = bmr + 66
            return total_bmr

        else:
            bmr = (4.7 * height) + (4.35 * average_weight) - (4.7 * user_age)
            total_bmr = bmr + 655
            return total_bmr

    @staticmethod
    def calorie_needs(user_id):
        required_bmr = UserSetting.calculate_bmr(user_id)
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        activity_level = user_setting.actvity_level

        if activity_level == "Low":
            total_bmr = required_bmr * 1.2
            return total_bmr

        elif activity_level == "Lightly active":
            total_bmr = required_bmr * 1.375
            return total_bmr

        elif activity_level == "moderately active":
            total_bmr = required_bmr * 1.55
            return total_bmr

        elif activity_level == "very active":
            total_bmr = required_bmr * 1.725
            return total_bmr
        else:
            total_bmr = required_bmr * 1.9
            return total_bmr

    @staticmethod
    # daily calorie goal Implementation
    def get_net_calorie(user_id, goal_weight, average_weight):
        average_calorie = UserSetting.calorie_needs(user_id)
        # user_setting = UserSetting.query.filter_by(id=user_id).first()
        # goal_weight = goal_weight
        # average_weight = average_weight
        if goal_weight == average_weight:
            goal_calorie = average_calorie
            return goal_calorie

        elif goal_weight > average_weight:
            required_calorie_goal = UserSetting.gainbyakg(user_id)
            required_calorie = required_calorie_goal / (goal_weight - average_weight)
            goal_calorie = average_calorie + required_calorie / 7
            return goal_calorie

        else:
            required_calorie_goal = UserSetting.losebyakg(user_id)
            required_calorie = required_calorie_goal / (average_weight - goal_weight)
            goal_calorie = average_calorie + (required_calorie / 7)
            return goal_calorie

    @staticmethod
    def gainbyakg(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        goal_weight = user_setting.goal_weight
        average_weight = user_setting.average_weight
        weight_gain = goal_weight - average_weight
        calorie_required = weight_gain * 7700
        user_setting.goal_calorie = calorie_required
        db.session.commit()

    @staticmethod
    def losebyakg(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        goal_weight = user_setting.goal_weight
        average_weight = user_setting.average_weight
        weight_loss = goal_weight - average_weight
        calorie_required = weight_loss * 7700
        return calorie_required


class Meal_table(db.Model):
    __tablename__ = "mealtable"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name_of_food = db.Column(db.String(255), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    is_diabetic = db.Column(db.String, nullable=False)
    breakfast = db.Column(db.String, nullable=False)
    lunch = db.Column(db.String, nullable=False)
    dinner = db.Column(db.String, nullable=False)

    # def __init__(self, id, name_of_food, calories, is_diabetic, breakfast, lunch, dinner):
    #     self.id = id
    #     self.name_of_food = name_of_food
    #     self.calories = calories
    #     self.is_diabetic = is_diabetic
    #     self.breakfast = breakfast
    #     self.lunch = lunch
    #     self.dinner = dinner
    #
    # def save(self):
    #     db.Session.add(self)
    #     db.Session.commit()

    @staticmethod
    def compare_time():
        today_date = datetime.datetime.today()
        morning = 11
        afternoon = 17
        if today_date.hour <= morning:
            meal_time = 'Breakfast'
            return meal_time
        elif (today_date.hour > morning) and (today_date.hour <= afternoon):
            meal_time = 'Lunch'
            return meal_time
        else:
            meal_time = 'Dinner'
            return meal_time

    """
    Checks the time of the day and classifies the time in breakfast lunch and dinner
    """

    @staticmethod
    def calculate_calorie_meal_requirement(user_id):
        type_of_meal = Meal_table.compare_time()
        user_setting = UserSetting.query.filter_by(id=user_id)
        net_calorie_goal = user_setting.daily_calorie_goal
        if type_of_meal == "Breakfast":
            calorie_limit = 0.2 * net_calorie_goal
            return calorie_limit

        elif type_of_meal == "Lunch":
            calorie_limit = 0.4 * net_calorie_goal
            return calorie_limit
        else:
            calorie_limit = 0.4 * net_calorie_goal
            return calorie_limit

    """
    calculates the calorie limit for breakfast, lunch and dinner
    """

    @staticmethod
    def recommendation_algorithm(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        health_condition = user_setting.is_diabetic
        calories = Meal_table.calculate_calorie_meal_requirement(user_id)
        type_of_meal = Meal_table.compare_time()

        if health_condition == "True" and type_of_meal == "Breakfast":
            return Food.query.filter(
                and_(Meal_table.is_diabetic == "True", Meal_table.breakfast == "True",
                     Meal_table.calories <= calories)).all()
        elif health_condition == "False" and type_of_meal == "Breakfast":
            return Food.query.filter(
                and_(Meal_table.is_diabetic == "False", Meal_table.breakfast == "True",
                     Meal_table.calories <= calories)).all()
        elif health_condition == "True" and type_of_meal == "Lunch":
            return Food.query.filter(and_(Meal_table.is_diabetic == "True", Meal_table.lunch == "True",
                                          Meal_table.calories <= calories)).all()
        elif health_condition == "False" and type_of_meal == "Lunch":
            return Food.query.filter(and_(Meal_table.is_diabetic == "False", Meal_table.lunch == "True",
                                          Meal_table.calories <= calories)).all()
        elif health_condition == "True" and type_of_meal == "Dinner":
            return Food.query.filter(and_(Meal_table.is_diabetic == "True", Meal_table.dinner == "True",
                                          Meal_table.calories <= calories)).all()
        elif health_condition == "False" and type_of_meal == "Dinner":
            return Food.query.filter(and_(Meal_table.is_diabetic == "False", Meal_table.dinner == "True",
                                          Meal_table.calories <= calories)).all()


class Food(db.Model):
    __tablename__ = "food"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name_of_food = db.Column(db.String(255), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    breakfast = db.Column(db.String, nullable=False)
    lunch = db.Column(db.String, nullable=False)
    dinner = db.Column(db.String, nullable=False)
    is_diabetic = db.Column(db.String, nullable=False)

    # def __init__(self, id, name_of_food, grammes):
    #     self.id = id
    #     self.name_of_food = name_of_food
    #     self.grammes = grammes

    @staticmethod
    def get_all_meals():
        return Food.query.filter_by(id=id).all()

    @staticmethod
    def sort_food(user_id):
        user_setting = UserSetting.query.filter_by(id=user_id).first()
        is_diabetic = user_setting.is_diabetic
        type_of_meal = Meal_table.compare_time()
        if is_diabetic == "True" and type_of_meal == "Breakfast":
            return Food.query.filter(and_(Food.is_diabetic == "True", Food.breakfast == "True")).all()
        elif is_diabetic == "False" and type_of_meal == "Breakfast":
            return Food.query.filter(and_(Food.is_diabetic == "False", Food.breakfast == "True")).all()
        elif is_diabetic == "True" and type_of_meal == "Lunch":
            return Food.query.filter(and_(Food.is_diabetic == "True", Food.lunch == "True")).all()
        elif is_diabetic == "False" and type_of_meal == "Lunch":
            return Food.query.filter(and_(Food.is_diabetic == "False", Food.lunch == "True")).all()
        elif is_diabetic == "True" and type_of_meal == "Dinner":
            return Food.query.filter(and_(Food.is_diabetic == "True", Food.dinner == "True")).all()
        elif is_diabetic == "False" and type_of_meal == "Dinner":
            return Food.query.filter(and_(Food.is_diabetic == "False", Food.dinner == "True")).all()

    """used to implement the list of foods of calorie calculator"""
    @staticmethod
    def getCalories(food):
        meal = Food.query.filter_by(name_of_food=food).first()
        calories = int(meal.calories)
        return calories


class FoodHistory(db.Model):
    __tablename__ = "foodhistory"
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'))
    breakfast = db.Column(db.String(255), nullable=True)
    lunch = db.Column(db.String(255), nullable=True)
    dinner = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    calorie_deficit = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, breakfast, lunch, dinner, date, calorie_deficit):
        self.user_id = user_id
        self.breakfast = breakfast
        self.lunch = lunch
        self.dinner = dinner
        self.date = date
        self.calorie_deficit = calorie_deficit
        self.id = uuid.uuid4().__str__()

    def save(self):
        """
        Persist the foodhistory in the database
        :param :
        :return:
        """
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_user_food_history(user_id):
        return FoodHistory.query.filter(FoodHistory.user_id == user_id).all()


