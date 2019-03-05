from flask import Flask, jsonify, request, Blueprint
from app.model import User, Post, Community, BlackListToken, Comments, Likes
import re
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
            return response_auth('success', 'Successfully logged In', user.encode_auth_token(user.id), 200)
        return response('failed', 'User does not exist or password is incorrect', 401)
    return response('failed', 'Missing or wrong email format or password is less than four characters', 401)


@routes.route("/auth/logout", methods=["POST"])
def logout():
    """
        Try to logout a user using a token
        :return:
     """
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            return response('failed', 'Provide a valid auth token', 403)
        else:
            decoded_token_response = User.decode_auth_token(auth_token)
            if not isinstance(decoded_token_response, str):
                token = BlackListToken(auth_token)
                token.blacklist()
                return response('success', 'Successfully logged out', 200)
            return response('failed', decoded_token_response, 401)
    return response('failed', 'Provide an authorization header', 403)


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
    post_item.save()
    return response('success', 'Successfully posted', 200)


@routes.route('/getuserposts', methods=['GET'])
@token_required
def getuserpost(current_user):
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
    return response('success', 'Commented successfully', 200)


@routes.route('/getcomment/<post_id>', methods=['POST'])
@token_required
def getcomment(post_id):
    comments = []
    comment = Comments.getcomments(post_id=post_id)

    for c in comment:
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
