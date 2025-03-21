import os
import pandas as pd
import numpy as np
import tensorflow as tf
import mysql.connector
from flask import Flask, request, render_template, send_from_directory,flash
from tensorflow.keras.preprocessing import image
from keras.models import load_model

app=Flask(__name__)
app.config['SECRET_KEY'] = 'the random string'

Disease = ['Actinic keratoses', 'Basal cell carcinoma', 'Benign keratosis-like lesions', 'Dermatofibroma', 'Melanocytic nevi', 'Melanoma', 'Vascular lesions']

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/reg")
def reg():
    return render_template("ureg.html")
@app.route('/regback',methods = ["POST"])
def regback():
    if request.method=='POST':
        name=request.form['name']
        email=request.form['email']
        pwd=request.form['pwd']
        cpwd=request.form['cpwd']
        pno=request.form['pno']

        #email = request.form["email"]

        print("**************")
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="skin"
        )
        mycursor = mydb.cursor()
        print("**************")
        sql = "select * from ureg"
        result = pd.read_sql_query(sql, mydb)
        email1 = result['email'].values
        print(email1)
        if email in email1:
            flash("email already exists","warning")
            return render_template('ureg.html')
        if(pwd==cpwd):
            sql = "INSERT INTO ureg (name,email,pwd,pno) VALUES(%s,%s,%s,%s)"
            val = (name, email, pwd, pno)
            mycursor.execute(sql, val)
            mydb.commit()
            flash("You registered successfully", "success")

            return render_template('user.html')
        else:
            flash("Password and Confirm Password are not same", "danger")
            return render_template('ureg.html')
    flash("Something wrong", "danger")
    return render_template('user.html')

@app.route('/userlog',methods=['POST', 'GET'])
def userlog():
    global name, name1
    global user
    if request.method == "POST":

        username = request.form['email']
        password1 = request.form['pwd']
        print('p')
        mydb = mysql.connector.connect(host="localhost", user="root", passwd="", database="skin")
        cursor = mydb.cursor()
        sql = "select * from ureg where email='%s' and pwd='%s'" % (username, password1)
        print('q')
        x = cursor.execute(sql)
        print(x)
        results = cursor.fetchall()
        print(results)
        if len(results) > 0:
            print('r')
            flash("Welcome to website", "success")
            return render_template('userhome.html', msg=results[0][1])
        else:
            flash("Invalid Email/password", "danger")
            return render_template('user.html')

    return render_template('user.html')
@app.route("/userhome")
def userhome():
    return render_template("userhome.html")

@app.route("/upload",methods=["POST","GET"])
def upload():
    if request.method=='POST':
        print("hdgkj")
        m = int(request.form["alg"])
        acc = pd.read_csv("D:\CODE\Accuracy.csv")

        myfile = request.files['file']
        fn = myfile.filename
        mypath = os.path.join("images/", fn)
        myfile.save(mypath)

        print("{} is the file name", fn)
        print("Accept incoming file:", fn)
        print("Save it to:", mypath)

        if m == 1:
            print("bv1")
            new_model = load_model(r'model/CNN.h5')
            test_image = image.load_img(mypath, target_size=(128, 128))
            test_image = image.img_to_array(test_image)
            a = acc.iloc[m - 1, 1]

        elif m == 2:
            print("bv2")
            new_model = load_model(r'model/ResNet.h5')
            test_image = image.load_img(mypath, target_size=(128, 128))
            test_image = image.img_to_array(test_image)
            a = acc.iloc[m - 1, 1]

        else:
            print("bv3")
            new_model = load_model(r'model/Xception.h5')
            test_image = image.load_img(mypath, target_size=(128, 128))
            test_image = image.img_to_array(test_image)
            a = acc.iloc[m - 1, 1]

        test_image = np.expand_dims(test_image, axis=0)
        result = new_model.predict(test_image)
        preds = Disease[np.argmax(result)]

        if preds == "Actinic keratoses":
            msg = "5% fluorouracil cream is the best first-line treatment for actinic keratosis skin lesions. Comparison of four common treatment regimens for actinic keratosis found that twice daily 5% fluorouracil cream was the most effective and least expensive."

        elif preds == "Basal cell carcinoma":
            msg = "Basal cell carcinoma is most often treated with surgery to remove all of the cancer and some of the healthy tissue around it. Options might include: Surgical excision. In this procedure, your doctor cuts out the cancerous lesion and a surrounding margin of healthy skin"

        elif preds == "Benign keratosis-like lesions":
            msg = "it is hard to distinguish from skin cancer, or if the diagnosis is uncertain the patient does not like it, and wants it removed"

        elif preds == "Dermatofibroma":
            msg = "Most dermatofibromas do not require treatment. A person can safely leave them alone, and they will usually cause no symptoms aside from their appearance on the skin"


        elif preds == "Melanocytic nevi":
            msg = "Melanocytic nevi can be surgically removed for cosmetic considerations or because of concern regarding the biological potential of a lesion. Melanocytic nevi removed for cosmesis are often removed by tangential or shave excision."

        elif preds == "Melanoma":
            msg = "Metastases that cause symptoms but cannot be removed may be treated with radiation, immunotherapy, targeted therapy, or chemotherapy."

        else:
            msg = "Laser treatment is usually the best option for vascular lesions of the face. On the legs, injection of a medication to destroy the blood vessel (sclerotherapy) can be a better option for spider veins. Deeper veins may need treatment with surgery or very small lasers that are inserted into larger blood vessels."



        return render_template("template.html", text=preds, msg=msg, image_name=fn,a=round(a*100,3))
    return render_template("upload.html")

@app.route("/upload1")
def upload1():
    return render_template("upload.html")

@app.route("/upload/<filename>")
def send_image(filename):
    return send_from_directory("images",filename)


if __name__=="__main__":
    app.run(debug=True)