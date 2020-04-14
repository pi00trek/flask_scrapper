from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class AddressForm(FlaskForm):
    person_url = StringField('person_url', validators=[DataRequired()])