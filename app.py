import os, datetime, re, stripe, math, requests, random
from dhooks import Webhook
from discord_webhook import DiscordWebhook, DiscordEmbed
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, send_file, url_for, jsonify, session, flash
from flask_login import current_user, login_user, LoginManager, UserMixin, login_required, login_user, logout_user
from device_detector import DeviceDetector
from flask_sslify import SSLify
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
from random import randint
from shutil import copyfile


#inits
app = Flask(__name__)
sslify = SSLify(app)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'hidden_for_github'
)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User(userid)

def get_username(self):
    return self.username

# success kolage stuff functions:

UPLOAD_FOLDER = 'success_kolage/data'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# END success kollage functions

@app.route('/collage', methods=['GET', 'POST'])
def collage_upload_file():
    if request.remote_addr == "149.224.144.236": #banning a friend that spammed xD
        return("banned")
    else:
        if request.method == 'POST':
            int_list = [1,2,3,4,5,6,7,8,9,0]

            original_user_now_b_ip = request.remote_addr
            user_now_b = request.remote_addr.replace(".","")

            image_list_all_count_bla_COUNT_neinnn_shishabar = 0
            rfuuruhuheuerueufrufr = os.listdir(f'success_kolage/data/{user_now_b}/')
            for i in rfuuruhuheuerueufrufr:
                image_list_all_count_bla_COUNT_neinnn_shishabar = image_list_all_count_bla_COUNT_neinnn_shishabar + 1

            if os.path.exists(f"success_kolage/data/{user_now_b}"):
                images_list = os.listdir(f'success_kolage/data/{user_now_b}/')
                for image_item in images_list:
                    os.remove(f'success_kolage/data/{user_now_b}/{image_item}')
            else:
                os.mkdir(f"success_kolage/data/{user_now_b}")

            parse_color_Hex = request.form['color_hex'].replace("#","")
            parse_foreground_img_url = request.form['foreground_img']
            if parse_foreground_img_url == "":
                parse_foreground_img_url = "none"
                
            overlay_opacity_durchsichtigkeit_var = request.form['opacity']

            if 'files[]' not in request.files:
                print('No file part')
                return redirect(request.url)

            files = request.files.getlist('files[]')

            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(f"success_kolage/data/{user_now_b}", filename))

            print('File(s) successfully uploaded')

            images_list = os.listdir(f'success_kolage/data/{user_now_b}/')

            overlayColor = getOverlayColor(parse_color_Hex=parse_color_Hex)
            foregroundImgUrl = getForegroundImageUrl(parse_foreground_img_url=parse_foreground_img_url)
            images = parseImages(user_now_b=user_now_b)

            #print('Creating collage...')

            background_color = request.form['background_color']

            createCollage(images, overlayColor, foregroundImgUrl, overlay_opacity_durchsichtigkeit_var, image_list_all_count_bla_COUNT_neinnn_shishabar, background_color)
            #make_collage(images=images_list, filename="success_kolage/output.png", width=1920, init_height=1080,user_now_b=user_now_b)

            random_nr = f'{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}{random.choice(int_list)}'

            copyfile("success_kolage/output.png", f"static/sc/output_{user_now_b}_{random_nr}.png")

            webhook = DiscordWebhook(url=ai_collage_webhook_url)
            embed= DiscordEmbed(Title="New Collage created!", color=4886754)
                
            embed.add_embed_field(name="User:", value = original_user_now_b_ip, inline=True)
            embed.set_footer(text="asdatindustries.com")
            embed.set_image(url=f"https://asdatindustries.com/static/sc/output_{user_now_b}_{random_nr}.png")
            embed.set_timestamp()
            webhook.add_embed(embed)
            response = webhook.execute() #sending a discord webhook since I want to stalk my users :O

            return send_file("success_kolage/output.png", as_attachment=True)
        elif request.method == 'GET':
            return render_template('success_collage/temp.html')
        else:
            return("HM TF?")

@app.route('/')
def home():
    global server_id_parsing_bla
    if request.headers['Host'] == "asdatindustries.com":
        return render_template("index.html")
    elif request.headers['Host'] == "asdat.me":
        return render_template("indexpersonal.html")
    elif request.headers['Host'] == "kyneticaio.com":
        return render_template("index_kyneticaio.html")
    elif request.headers['Host'] == "retail-cops.com":
        return render_template("ro/index.html")
    elif request.headers['Host'] == "pinger.asdatindustries.com":
        return render_template("pinger_templates/infos_index/index.html")
    elif request.headers['Host'] == "cipher.asdatindustries.com":
        return redirect("/cipher")
    elif request.headers['Host'] == "aurorarobotics.site":
        return render_template("fun/aurora.html")
    elif request.headers['Host'] == "twitter.asdatindustries.com":
        server_id_parsing_bla = ""
        return redirect("/login")
    else:
        return render_template("index.html")


#cust error handlers
@app.errorhandler(401)
def custom_401(error):
    return redirect("401 unauthobums dings alda, du hast einfach keine rechte ende!<br>kein plan was du versucht hast aber lass es bidde einfach<br><br>seriosly if I recognize this again with anything that matches your PC (IP, Mac, userAgent)<br>I´ll permanently ban you!<br>Thankss <3")

@app.errorhandler(404)
def custom_404(error):
    return render_template("page_not_found.html")

#run
if __name__ == '__main__':
    app.run(host='185.78.255.230', port=443, ssl_context=('/etc/letsencrypt/live/asdatindustries.com-0001/fullchain.pem', '/etc/letsencrypt/live/asdatindustries.com-0001/privkey.pem')) #   248422776682053632
