from flask import Flask, jsonify, request, Blueprint
from app.model import User, Post, Community, Comments, Likes, Steps, Challenge
import re
import datetime
from app.helper import response, response_auth, token_required
from app import bcrypt

# app = Flask(__name__)

routes = Blueprint('routes', __name__)


@routes.route("/auth/register", methods=["POST"])
def register():
    values = request.get_json()
    required = ['username', 'last_name', 'first_name', 'password', 'email']
    if not all(k in values for k in required):
        return 'Missing values', 400
    email = values.get('email')
    username = values.get('username')
    last_name = values.get('last_name')
    first_name = values.get('first_name')
    password = values.get('password')

    if re.match(r"[^@]+@[^@]+\.[^@]+", email) and len(password) > 4:
        user = User.get_by_email(email)
        user_name = User.get_by_username(username)
        if user_name:
            return response('failed', 'Failed, username already exists', 202)
        if not user:
            token = User(email=email, password=password, first_name=first_name, last_name=last_name,
                         username=username).save()
            return response_auth('success', 'Successfully registered', token, 201)
        else:
            return response('failed', 'Failed, User already exists, Please sign In', 202)
    return response('failed', 'Missing or wrong email format or password is less than four characters', 202)


@routes.route("/auth/login", methods=["POST"])
def login():
    values = request.get_json()
    required = ['password', 'email']
    if not all(k in values for k in required):
        return 'Missing values', 400
    email = values.get('email')
    password = values.get('password')
    if re.match(r"[^@]+@[^@]+\.[^@]+", email) and len(password) > 4:
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return response_auth(User.getusername(user.id), 'Successfully logged In', user.encode_auth_token(user.id),
                                 200)
        return response('failed', 'User does not exist or password is incorrect', 401)
    return response('failed', 'Missing or wrong email format or password is less than four characters', 401)


@routes.route('/getuser', methods=['POST'])
def getuser():
    values = request.get_json()
    required = ['user_id']
    if not all(k in values for k in required):
        return 'Missing values', 400
    user = User.get_by_id(values.get('user_id'))
    count = Community.get_community_count(values.get('user_id'))
    post_count = Post.get_post_count(values.get('user_id'))
    if user:
        data = {
            'user_id': user.id,
            'username': user.username,
            'community': count,
            'posts': post_count
        }
    else:
        return response('failed', 'User Does not exist', 401)
    return jsonify(data), 200


@routes.route('/getuserprofile', methods=['POST'])
@token_required
def getuserprofile(current_user):
    count = Community.get_community_count(current_user.id)
    post_count = Post.get_post_count(current_user.id)
    data = {
        'user_id': current_user.id,
        'username': current_user.username,
        'community': count,
        'posts': post_count
    }

    return jsonify(data), 200


@routes.route('/getuserprofile/<userid>', methods=['POST'])
@token_required
def getuserprofileid(current_user, userid):
    isFollowing = False
    community = Community.get_community(current_user.id)
    for person in community:
        if person.community_id == userid:
            isFollowing = True
    count = Community.get_community_count(userid)
    post_count = Post.get_post_count(userid)

    data = {
        'user_id': userid,
        'username': User.getusername(userid),
        'community': count,
        'posts': post_count,
        'isFollowing': isFollowing
    }

    return jsonify(data), 200


@routes.route('/search', methods=['POST'])
@token_required
def search(current_user):
    isFollowing = False
    values = request.get_json()
    required = ['username']
    if not all(k in values for k in required):
        return 'Missing values', 400
    user = User.get_by_username(values.get('username'))
    if user:
        community = Community.get_community(current_user.id)
        for person in community:
            if person.community_id == user.id:
                isFollowing = True

        data = {
            'user_id': user.id,
            'username': user.username,
            'community': isFollowing
        }
    else:
        return response('failed', 'User Does not exist', 401)

    return jsonify(data), 200


@routes.route('/posts', methods=['POST'])
@token_required
def post(current_user):
    """
       create a post
    :return:
    """
    values = request.get_json()
    required = ['description', 'image_url']
    if not all(k in values for k in required):
        return 'Missing values', 400
    description = values.get('description')

    image_url = values.get('image_url')
    userid = current_user.id

    post_item = Post(description, image_url, userid)
    post_id = post_item.save()
    temp = description.lower()
    data = {}
    for word in temp.split():
        if word.startswith("#"):
            if "challenge" in word:
                data['challenge'] = word[1:]
            elif word[1:].startswith("d"):
                data['date'] = word[2:]
            elif word[1:].startswith("g"):
                data['goal'] = word[2:]

    required = ['challenge', 'date', 'goal']
    if all(k in data for k in required):
        end_date = {}
        date = data["date"].split('-')
        end_date['year'] = date[0]
        end_date['month'] = date[1]
        end_date['day'] = date[2]
        challenge = Challenge(user_id=current_user.id, goal=data["goal"], challenge_name=data["challenge"],
                              challenge_description=description, end_date=end_date, post_id=post_id)
        challenge.save()
    return response('success', 'Successfully posted', 200)


@routes.route('/getuserposts', methods=['GET'])
@token_required
def getuserpostid(current_user):
    """
    get posts
    :return:
    """
    posts = []
    post = Post.get_posts(current_user.id)
    comments = []

    for item in post:

        comments.clear()
        comment = Comments.getcomments(item.id)

        for c in comment:
            comments.append({
                'comment': c.comment,
                'username': User.getusername(c.user_id),
                'create_at': c.create_at
            })

        posts.append({
            'post_id': item.id,
            'description': item.description,
            'image_url': item.image_url,
            'create_at': item.create_at,
            'user_id': item.user_id,
            'username': User.getusername(item.user_id),
            'likes': item.likes,
            'comments': comments
        })
    return jsonify(posts), 200


@routes.route('/getuserposts/<user_id>', methods=['GET'])
def getuserpost(user_id):
    """
    get posts
    :return:
    """
    posts = []
    post = Post.get_posts(user_id)
    comments = []

    for item in post:

        comments.clear()
        comment = Comments.getcomments(item.id)

        for c in comment:
            comments.append({
                'comment': c.comment,
                'username': User.getusername(c.user_id),
                'create_at': c.create_at
            })

        posts.append({
            'post_id': item.id,
            'description': item.description,
            'image_url': item.image_url,
            'create_at': item.create_at,
            'user_id': item.user_id,
            'username': User.getusername(item.user_id),
            'likes': item.likes,
            'comments': comments
        })
    return jsonify(posts), 200


@routes.route('/getposts', methods=['GET'])
@token_required
def getpost(current_user):
    """
    get posts
    :return:
    """
    posts = []
    comments = []
    post = Post.get_posts(current_user.id)
    community = Community.get_community(current_user.id)
    for item in post:

        comments.clear()
        comment = Comments.getcomments(item.id)

        for c in comment:
            comments.append({
                'comment': c.comment,
                'username': User.getusername(c.user_id),
                'create_at': c.create_at
            })

        posts.append({
            'post_id': item.id,
            'description': item.description,
            'image_url': item.image_url,
            'create_at': item.create_at,
            'user_id': item.user_id,
            'username': User.getusername(item.user_id),
            'likes': item.likes,
            'comments': comments
        })
    for person in community:
        data = Post.get_posts(person.community_id)
        for i in data:

            comments.clear()
            comment = Comments.getcomments(i.id)

            for c in comment:
                comments.append({
                    'comment': c.comment,
                    'username': User.getusername(c.user_id),
                    'create_at': c.create_at
                })

            posts.append({
                'post_id': i.id,
                'description': i.description,
                'image_url': i.image_url,
                'create_at': i.create_at,
                'user_id': i.user_id,
                'username': User.getusername(i.user_id),
                'likes': i.likes,
                'comments': comments
            })

    return jsonify(posts), 200


@routes.route('/community/request/<user_id>', methods=['POST'])
@token_required
def community_request(current_user, user_id):
    """
    api to request to join community
    :param current_user:
    :param user_id:
    :return:
    """
    community = Community(community_id=user_id, user_id=current_user.id)
    community.save()
    return response('success', 'Successfully joined community', 200)


@routes.route('/community/getcommunity', methods=['GET'])
@token_required
def get_community(current_user):
    response = []
    community = Community.get_community(current_user.id)
    for person in community:
        response.append({
            'user_id': person.user_id,
            'community_id': person.community_id
        })
    return jsonify(response), 200


@routes.route('/like/<post_id>', methods=['POST'])
@token_required
def like(current_user, post_id):
    like = Likes(user_id=current_user.id, post_id=post_id)
    like.save()
    return response('success', 'Successfully liked post', 200)


@routes.route('/comment', methods=['POST'])
@token_required
def comment(current_user):
    values = request.get_json()
    required = ['comment', 'post_id']
    if not all(k in values for k in required):
        return 'Missing values', 400
    comment = Comments(comment=values.get('comment'), post_id=values.get('post_id'), user_id=current_user.id)
    comment.save()

    message = values.get('comment')
    challenge = Challenge.check_postid(values.get('post_id'))
    if challenge and Challenge.check_join(message, User.getusername(current_user.id)):
        fields = {'user_id': current_user.id,
                  'post_id': values.get('post_id'),
                  'goal': challenge.goal,
                  'start_date': challenge.start_date,
                  'challenge_name': challenge.challenge_name,
                  'challenge_description': challenge.challenge_description,
                  'current_date': datetime.datetime.now().date(),
                  'end_date': challenge.end_date
                  }
        if not Challenge.check_user_joined(current_user.id, values.get('post_id')):
            Challenge.join_challenge(fields)
        else:
            return response('failed', 'already joined', 400)

    return response('success', 'Commented successfully', 200)


@routes.route('/getcomment/<post_id>', methods=['POST'])
def getcomment(post_id):
    comments = []
    commentobj = Comments.getcomments(post_id=post_id)

    for c in commentobj:
        comments.append({
            'comment': c.comment,
            'username': User.getusername(c.user_id),
            'create_at': c.create_at
        })
    return jsonify(comments), 200


@routes.route('/getlikers/<post_id>', methods=['POST'])
def get_likers(post_id):
    response = []
    likers = Likes.getlikers(post_id=post_id)
    for user in likers:
        response.append({
            'username': User.getusername(user.user_id)
        })
    return jsonify(response), 200


@routes.route('/checkliker/<post_id>', methods=['POST'])
@token_required
def check_liker(current_user, post_id):
    likers = Likes.getlikers(post_id=post_id)
    for user in likers:
        if user.user_id == current_user.id:
            return "LIKED", 200
    return "NOT LIKED", 401


@routes.route('/storesteps/<steps>', methods=['POST'])
@token_required
def store_steps(current_user, steps):
    step = Steps(user_id=current_user.id, steps_no=steps)
    if not Steps.update_if_instance_exist(datetime.datetime.now().date(), current_user.id, steps):
        step.save()
    """challenges = Challenge.get_challenge_within_date_by_user_id(current_user.id, datetime.datetime.now())
    if challenges:
        for challenge in challenges:
            Challenge.update_challenge_steps(challenge.id, steps)"""

    return response('success', 'Steps added successfully', 200)


@routes.route('/getsteps/<limit>', methods=['GET'])
@token_required
def get_steps(current_user, limit):
    steps = Steps.get_steps(current_user.id, limit)
    resp = []
    for data in steps:
        resp.append({
            'date': data.date,
            'steps': data.steps_no
        })
    return jsonify(resp), 200


@routes.route('/challenge/getchallenges', methods=['GET'])
@token_required
def get_all_challenges(current_user):
    #challenges = Challenge.get_challenge_by_user_id(current_user.id)
    challenges = Challenge.get_challenge_within_date_by_user_id(current_user.id, datetime.datetime.now())
    resp = []
    for challenge in challenges:
        user = Challenge.get_creator(challenge.id)
        username = User.getusername(user.user_id)
        my_format = "%Y-%m-%d %H:%M:%S"
        start_date = datetime.datetime.strptime(str(challenge.start_date), my_format).date()
        new_date = datetime.datetime.strptime(str(challenge.end_date), my_format).date()
        users = Challenge.get_users_performance(challenge.post_id)
        challenge_users = []
        for user in users:
            user_name = User.getusername(user.user_id)
            challenge_users.append({
                'username': user_name,
                'steps': Challenge.get_user_steps_by_challenge(datetime.datetime.now().date(),
                                                               start_date, user.user_id),
                'role': user.role
            })
        resp.append({
            'steps': Challenge.get_user_steps_by_challenge(datetime.datetime.now().date(), start_date, current_user.id),
            'start_date': challenge.start_date,
            'goal': challenge.goal,
            'role': challenge.role,
            'challenge_name': challenge.challenge_name,
            'challenge_description': challenge.challenge_description,
            'end_date': str(new_date),
            'creator': username,
            'image_url': Post.get_post_image_url(challenge.post_id),
            'challenge_id': challenge.id,
            'users': challenge_users
        })
    return jsonify(resp), 200


"""@routes.route('/notification/save', methods=['POST'])
@token_required
def save_notification(current_user):
    values = request.get_json()
    required = ['message']
    if not all(k in values for k in required):
        return 'Missing values', 400
    user_id = values.get("user_id")
    message = values.get("message")
    is_post_related = "False"
    is_community_request = "False"
    community_invitee = None
    post_id = None

    if values.get("is_post_related"):
        is_post_related = values.get("is_post_related")
    if values.get("is_community_request"):
        is_community_request = values.get("is_community_request")
    if values.get("community_invitee"):
        community_invitee = current_user.id
    if values.get("post_id"):
        post_id = values.get("post_id")

    notification = Notification(user_id=user_id, message=message,
                                is_post_related=is_post_related,
                                community_invitee=community_invitee, post_id=post_id,
                                is_community_request=is_community_request)
    notification.save()
    return response('success', 'notification sent successfully', 200)


@routes.route('/notification/get', methods=['GET'])
@token_required
def get_notification(current_user):
    notifications = Notification.get_notifications(current_user.id)
    response = []
    for notification in notifications:
        response.append({
            "id": notification.id,
            "user_id": notification.user_id,
            "create_at": notification.create_at,
            "message": notification.message,
            "is_post_related": notification.is_post_related,
            "is_community_request": notification.is_community_request,
            "community_invitee": notification.community_invitee,
            "post_id": notification.post_id
        })
    return jsonify(response), 200


@routes.route('/notification/update', methods=['POST'])
@token_required
def update_community_request(current_user):
    values = request.get_json()
    required = ['community_id', 'is_accepted', 'notification_id']
    if not all(k in values for k in required):
        return 'Missing values', 400
    is_accepted = values.get("is_accepted")
    if is_accepted == "True" and not Community.already_community(community_id=current_user.id,
                                                                 user_id=values.get("community_id")):
        community = Community(community_id=values.get("community_id"), user_id=current_user.id)
        community.save()
        community = Community(community_id=current_user.id, user_id=values.get("community_id"))
        community.save()
    Notification.request_answered(values.get("notification_id"))
"""