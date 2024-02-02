from flask import Flask,render_template, redirect, abort
import subprocess, jsonify, requests, json
from data import verify_secret,init_db, get_posts
from random import randint

app = Flask(__name__)

@app.route('/')
def home():
    global configs
    posts=get_posts(configs["database"])
    print(posts)
    return render_template('home.html', title='__init__', posts=posts, random_number=randint(0,100))

@app.route('/about')
def about():
    about_content = "Lorem Ipsium"
    return render_template('about.html', title='Whoami', about_content=about_content,  random_number=randint(0,100))

@app.route('/cv')
def cv():
    return 404

@app.route('/github')
def github():
    global configs
    return redirect(configs["github_link"], code=302)


@app.route("/post/<int:post_id>")
def post(post_id):
    global configs
    for p in get_posts(configs["database"]):
        if post["id"]==post_id:
            post=p
    if not post:
        return 404
    return render_template('post.html', post=post)

@app.route("/notes")
def notes():
    global configs
    return redirect(configs["site_url"], code=302)

@app.route('/webhook', methods=['POST'])
def webhook():
    request=request # to lie to the IDE
    if not verify_secret(1,request):
        abort(400, 'Invalid signature')
    
    data = request.json

    # Verify if the webhook is from GitHub
    if 'github' in request.headers.get('User-Agent', ''):
        # Update the path to your local repository
        repo_path = '/var/www/absidian_notes'
        
        # Pull the latest changes using subprocess
        subprocess.run(['git', '-C', repo_path, 'pull', 'origin', 'master'])

        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid webhook'}), 400

if __name__=="__main__":
    with open("setup.json") as f:
        configs= json.load(f)

    init_db(configs["database"])
    app.run(host="0.0.0.0",port=8010,debug=True)