from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app, db, model
from app.model import User, Post, Community


# Initializing the manager
manager = Manager(app)

# Initialize Flask Migrate
migrate = Migrate(app, db)

# Add the flask migrate
manager.add_command('db', MigrateCommand)

# Test coverage configuration

@manager.command
def dummy():
    # Create a user if they do not exist.
    user = User.query.filter_by(email="example@bucketmail.com").first()
    if not user:
        user = User("example@bucketmail.com", "123456", "John", "Doe", "JD")
        user.save()

    user = User("jjc@mailinator.com", "123456", "JJc", "JJc", "JJC")
    user.save()

    user1 = User.get_by_email("example@bucketmail.com")
    post = Post("No more insufficient fund", user1.id)
    post.save()

    user2 = User.get_by_email("jjc@mailinator.com")
    community = Community(user1.id, user2.id)
    community.save()


# Run the manager
if __name__ == '__main__':
    #dummy()
    manager.run()
    db.create_all()



