from flask import Flask, render_template, url_for, redirect
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)


class Base(DeclarativeBase):
    pass
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafes.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(500), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
    
with app.app_context():
    db.create_all()

class CreateCafeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    map_url = StringField("Location Link", validators=[DataRequired(), URL()])
    img_url = StringField("Image Link", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired()])
    seats = StringField("Seats", validators=[DataRequired()])
    has_toilet = BooleanField("Has Toilet")
    has_wifi = BooleanField("Has Wifi")
    has_sockets = BooleanField("Has Sockets")
    can_take_calls = BooleanField("Has Take Calls")
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    return render_template("cafes.html", all_cafes=all_cafes)

@app.route("/cafe/<int:cafe_id>")
def show_cafe(cafe_id):
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    return render_template("cafe.html", cafe=requested_cafe)

@app.route("/add", methods=["GET", "POST"])
def add_new_cafe():
    form = CreateCafeForm()
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("get_all_cafes"))
    return render_template("add-cafe.html", form=form)

@app.route("/update/<int:cafe_id>", methods=["GET", "POST"])
def update_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    update = CreateCafeForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        has_sockets=cafe.has_sockets,
        has_toilet=cafe.has_toilet,
        has_wifi=cafe.has_wifi,
        can_take_calls=cafe.can_take_calls,
        seats=cafe.seats,
        coffee_price=cafe.coffee_price,
    )
    if update.validate_on_submit():
        cafe.name=update.name.data
        cafe.map_url=update.map_url.data
        cafe.img_url=update.img_url.data
        cafe.location=update.location.data
        cafe.has_sockets=update.has_sockets.data
        cafe.has_toilet=update.has_toilet.data
        cafe.has_wifi=update.has_wifi.data
        cafe.can_take_calls=update.can_take_calls.data
        cafe.seats=update.seats.data
        cafe.coffee_price=update.coffee_price.data
        db.session.commit()
        return redirect(url_for("show_cafe", cafe_id=cafe_id))
    return render_template("update-cafe.html", form=update, is_edit=True)
    

if __name__ == '__main__':
    app.run(debug=True)