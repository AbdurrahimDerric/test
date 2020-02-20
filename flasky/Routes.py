from flask import render_template,url_for,request,escape,flash,redirect,abort
from flasky.forms import Regitration_form, Login_form,Update_info_form, Post_form, Reset_password_form,Reset_request_form,Submit_form
from flasky import app,db,bcrypt, mail
from flasky.Models import User,Post
from flasky.test1 import write_enumerator,read_enumerator
from flask_login import login_user,current_user,login_required,logout_user
import os
import base64
from PIL import Image
from flask_mail import Message
from flask_cors import CORS, cross_origin
from flask import Flask, Response, json, render_template,jsonify
from werkzeug.utils import secure_filename
from flask import request
from os import path, getcwd
import time
import os
import cv2
from flasky.camera import VideoCamera
from flasky.faceReco import recognize_face
app.config['file_allowed'] = ['image/png', 'image/jpeg']
app.config['train_img'] = path.join(getcwd(), 'train_img')
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})
CORS(app)

app.debug = True
enumerator = read_enumerator()


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/gallery')
def get_gallery():
   images = os.listdir(os.path.join(app.static_folder, "capture_image"))
   return render_template('gallery.html', images=images)


@app.route('/upload_image/<string:name>',methods = ["GET","POST"])
def upload_image(name="login"):
    return render_template("upload_image.html", name = name)


@app.route('/api',methods = ["GET","POST","OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])

def api():
    if request.method == "GET":
       print("get entered")
       return "no pic"
    elif request.method == "POST":
        image_data = request.form.get("content").split(",")[1]
        name = request.form.get("label")
        print("name" ,name)
        with open("flasky/static/database/" + name +"/" + name +".png","wb") as f:
            f.write(base64.b64decode(image_data))
        return "pic saved"
    return "done"


@app.route('/api_login',methods = ["GET","POST","OPTIONS"])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def api_login():
    if request.method == "GET":
       print("get entered")
       return redirect(url_for("login"))
    elif request.method == "POST":
        image_data = request.form.get("content").split(",")[1]
        name = request.form.get("label")

        print("name" ,name)
        with open("flasky/static/login/blog_user.png","wb") as f:
            f.write(base64.b64decode(image_data))
    return "ok"

@app.route('/wait',methods = ["GET","POST","OPTIONS"])
def wait():
    image = cv2.imread("flasky/static/login/blog_user.png")
    print(image)
    name = recognize_face(image)
    print("reco ", name)
    if name == "unknown":
        flash("Your face wasnt reconized, please log in with your email!", "danger")
        return redirect(url_for("login"))
    else:
        flash("We know you, you look great today!", "success")
        return redirect(url_for("pass_login", name=name))

    return render_template("wait.html")


@app.route('/pass_login/<string:name>',methods = ["GET","POST","OPTIONS"])
def pass_login(name):
    form = Submit_form()
    if form.validate_on_submit():
        user = User.query.filter_by(username=name.lower()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'welcome {user.username}!', "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("hello"))
        else:
            flash("wrong password!", "danger")
    return render_template("pass_login.html",form = form,name=name)


app.route('/save_image')
def save_image():
    save_picture()

# 111111111111111111111111111111111111111111111111


@app.route('/')
def hello():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)
    return render_template("main_page.html",posts=posts)



@app.route('/about')
def about():
    name = request.args.get("name", "abdo again")
    return f'Hello, {escape(name)}!'

@app.route("/register",methods = ["GET","POST"])
def register():
    if current_user.is_authenticated:
        redirect(url_for("hello"))
    form = Regitration_form()
    if form.validate_on_submit():
        print(form.username.data.lower())
        hashed =  bcrypt.generate_password_hash(form.password.data)
        user = User(username= form.username.data.lower(), email = form.email.data,password = hashed)
        db.session.add(user)
        db.session.commit()
        os.mkdir(os.path.join(app.root_path, "static/database", form.username.data) )
        flash(f"account created for {form.username.data}, you can now upload a face picture of yourself ",category="success")
        return redirect(url_for("upload_image", name=form.username.data))
    return render_template("register.html",form = form)

@app.route("/face_login/<string:name>",methods = ["GET","POST"])
def face_login(name = "Blog User"):
    return render_template("face_login.html",name=name)

@app.route("/login",methods = ["GET","POST"])
def login():
    if current_user.is_authenticated:
        redirect(url_for("hello"))
    form = Login_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember= form.remember.data)
            flash(f'welcome {user.username}!',"success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("hello"))
        else:
            flash("wrong email or password!","danger")
    return render_template("login.html",form = form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("hello"))


def save_picture(form_picture):
    _,extension = os.path.splitext(form_picture.filename)
    picture_name =  current_user.username + "_pp" + extension
    target_path = os.path.join(app.root_path, "static/profile_pics", picture_name)

    thumbnail_size = (250,250)
    i = Image.open(form_picture)
    i.thumbnail(thumbnail_size)
    i.save(target_path)

    # form_picture.save(target_path)

    return picture_name


@app.route("/account",methods = ["GET","POST"])
@login_required
def account():
    image_file = url_for("static", filename='profile_pics/' + current_user.image_file)
    form = Update_info_form()
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            current_user.image_file = picture_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your info was updated!","success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template("account.html", image_file = image_file,form  = form)


@app.route("/create_post", methods = ["GET","POST"])
@login_required
def create_post():
    form = Post_form()
    if form.validate_on_submit():
        post = Post(title= form.title.data, content = form.content.data, author= current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post was created!","success")
        return redirect(url_for("hello"))
    return render_template("create_post.html", form = form, legend = "Update post")


@app.route("/create_post/<int:post_id>", methods = ["GET","POST"])
@login_required
def post(post_id):
    post = Post.query.get(post_id)
    return render_template("post.html", post = post)

@app.route("/create_post/<int:post_id>/update", methods = ["GET","POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = Post_form()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        return  redirect(url_for('post', post_id = post.id))
    if request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", form= form, legend = "Update post")

@app.route("/create_post/<int:post_id>/delete", methods = ["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Your post was deleted successfully", "success")
    return redirect(url_for("hello"))

@app.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get("page", 1, type=int)
    user = User.query.filter_by(username= username).first_or_404()
    posts = Post.query.filter_by(author = user).order_by(Post.date_posted.desc()).paginate(page = page, per_page=5)

    return render_template("user_posts.html",posts=posts,user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Flasky Bolg,Reset password",sender ="darrige@gmail.om",recipients=["darrige@gmail.com"])
    msg.body = f" the link for reset" \
               f"{url_for('reset_request',token = token)}" \
               f" ignore"
    mail.send(msg)

@app.route("/reset_request",methods = ["GET","POST"])
def reset_request():
    if current_user.is_authenticated:
        redirect(url_for("hello"))
    form = Reset_request_form()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        send_reset_email(user)
        flash("an Email was sent to you","success")
        return redirect(url_for("login"))
    return render_template("reset_request.html",form = form)

@app.route("/reset_request/<token>",methods = ["GET","POST"])
def reset_password(token):
    if current_user.is_authenticated:
        redirect(url_for("hello"))
    form = Reset_password_form()
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    if form.validate_on_submit():
        flash("your password was reset!","success")
        return redirect(url_for("login"))
    return render_template("reset_password.html",form = form)

