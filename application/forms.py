# application/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    FloatField,
    IntegerField,
    BooleanField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Email, Length, EqualTo

# ---- Static choices taken from the HDB resale dataset ----
HDB_TOWNS = [
    ("ANG MO KIO", "Ang Mo Kio"),
    ("BEDOK", "Bedok"),
    ("BISHAN", "Bishan"),
    ("BUKIT BATOK", "Bukit Batok"),
    ("BUKIT MERAH", "Bukit Merah"),
    ("BUKIT PANJANG", "Bukit Panjang"),
    ("BUKIT TIMAH", "Bukit Timah"),
    ("CENTRAL AREA", "Central Area"),
    ("CHOA CHU KANG", "Choa Chu Kang"),
    ("CLEMENTI", "Clementi"),
    ("GEYLANG", "Geylang"),
    ("HOUGANG", "Hougang"),
    ("JURONG EAST", "Jurong East"),
    ("JURONG WEST", "Jurong West"),
    ("KALLANG/WHAMPOA", "Kallang / Whampoa"),
    ("MARINE PARADE", "Marine Parade"),
    ("PASIR RIS", "Pasir Ris"),
    ("PUNGGOL", "Punggol"),
    ("QUEENSTOWN", "Queenstown"),
    ("SEMBAWANG", "Sembawang"),
    ("SENGKANG", "Sengkang"),
    ("SERANGOON", "Serangoon"),
    ("TAMPINES", "Tampines"),
    ("TOA PAYOH", "Toa Payoh"),
    ("WOODLANDS", "Woodlands"),
    ("YISHUN", "Yishun"),
    ("LIM CHU KANG", "Lim Chu Kang"),
]

FLAT_TYPES = [
    ("1 ROOM", "1 ROOM"),
    ("2 ROOM", "2 ROOM"),
    ("3 ROOM", "3 ROOM"),
    ("4 ROOM", "4 ROOM"),
    ("5 ROOM", "5 ROOM"),
    ("EXECUTIVE", "Executive"),
    ("MULTI-GENERATION", "Multi-Generation"),
]

FLAT_MODELS = [
    ("2-room", "2-room"),
    ("Adjoined flat", "Adjoined flat"),
    ("Apartment", "Apartment"),
    ("DBSS", "DBSS"),
    ("Improved", "Improved"),
    ("Improved-Maisonette", "Improved-Maisonette"),
    ("Maisonette", "Maisonette"),
    ("Model A", "Model A"),
    ("Model A-Maisonette", "Model A-Maisonette"),
    ("Model A2", "Model A2"),
    ("Multi Generation", "Multi Generation"),
    ("New Generation", "New Generation"),
    ("Premium Apartment", "Premium Apartment"),
    ("Premium Apartment Loft", "Premium Apartment Loft"),
    ("Premium Maisonette", "Premium Maisonette"),
    ("Simplified", "Simplified"),
    ("Standard", "Standard"),
    ("Terrace", "Terrace"),
    ("Type S1", "Type S1"),
    ("Type S2", "Type S2"),
]

# Ranged distance bands – these are human-friendly labels
AMENITY_BANDS = [
    ("typical", "Not sure (use typical)"),
    ("lt_0_3", "< 0.3 km"),
    ("b_0_3_0_8", "0.3 – 0.8 km"),
    ("b_0_8_1_5", "0.8 – 1.5 km"),
    ("b_1_5_3_0", "1.5 – 3.0 km"),
    ("gt_3_0", "> 3.0 km"),
]


class HDBPriceForm(FlaskForm):
    # --- Core flat attributes ---
    town = SelectField(
        "Town",
        choices=HDB_TOWNS,
        validators=[DataRequired()],
    )

    flat_type = SelectField(
        "Flat type",
        choices=FLAT_TYPES,
        validators=[DataRequired()],
    )

    flat_model = SelectField(
        "Flat model",
        choices=FLAT_MODELS,
        validators=[DataRequired()],
    )

    floor_area_sqm = FloatField(
        "Floor area (sqm)",
        validators=[DataRequired(), NumberRange(min=10, max=300)],
    )

    storey_mid = IntegerField(
        "Storey (approximate floor)",
        validators=[DataRequired(), NumberRange(min=1, max=50)],
    )

    remaining_lease_years = FloatField(
        "Remaining lease (years)",
        validators=[DataRequired(), NumberRange(min=0, max=99)],
    )

    year = IntegerField(
        "Resale year",
        validators=[DataRequired(), NumberRange(min=2017, max=2030)],
        default=2024,
    )

    # --- Amenity access controls ---
    use_amenity_distances = BooleanField(
        "Use amenity distances in prediction",
        default=True,
    )

    dist_mrt_band = SelectField(
        "Nearest MRT",
        choices=AMENITY_BANDS,
        default="typical",
        validators=[DataRequired()],
    )

    dist_school_band = SelectField(
        "Nearest school",
        choices=AMENITY_BANDS,
        default="typical",
        validators=[DataRequired()],
    )

    dist_supermarket_band = SelectField(
        "Nearest supermarket",
        choices=AMENITY_BANDS,
        default="typical",
        validators=[DataRequired()],
    )

    dist_health_band = SelectField(
        "Nearest healthcare",
        choices=AMENITY_BANDS,
        default="typical",
        validators=[DataRequired()],
    )

    submit = SubmitField("Predict resale price")


# Backwards compatibility with your older name (if any)
ResalePriceForm = HDBPriceForm


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=30)],
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )
    submit = SubmitField("Login")
