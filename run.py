

from flasky.Models import User,Post
from flasky import db,app

db.drop_all()
db.create_all()
user1 = User(username = "darrige",email = "darrige@gmail.com",password = "123")
db.session.add(user1)
user2 = User(username = "test",email = "test@test.com",password = "123")
db.session.add(user2)
post1  = Post(title = "first post",content =" the content", user_id = 1)
db.session.add(post1)
db.session.commit()
#

app.run(host = "0.0.0.0", port =5000, debug = True)



# print(User.query.all())
# print(Post.query.all())

