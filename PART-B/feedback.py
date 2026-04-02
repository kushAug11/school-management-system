from flask import Flask, render_template,request,redirect,url_for

proj=Flask(__name__)
@proj.route("/order",methods=["GET","POST"])
def order():
    if request.method=="POST":
        return redirect(url_for("order"))
    return render_template("order.html")

if __name__ == "__main__":
    proj.run(debug=True,port=5001)
