import os

from dotenv import load_dotenv


# ==================================
# LOAD LOCAL ENVIRONMENT VARIABLES
# ==================================

load_dotenv()


class Config:

    # ==================================
    # SECURITY
    # ==================================

    SECRET_KEY = os.environ.get(
        "YPTSC_SECRET_KEY"
    )


    # ==================================
    # DATABASE
    # ==================================

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get(
            "DATABASE_URL"
        )
    )


    SQLALCHEMY_TRACK_MODIFICATIONS = (
        False
    )


    # ==================================
    # FLASK
    # ==================================

    TEMPLATES_AUTO_RELOAD = True


    # ==================================
    # SESSION
    # ==================================

    SESSION_PERMANENT = False


    SESSION_COOKIE_HTTPONLY = True


    SESSION_COOKIE_SAMESITE = "Lax"


    # False locally
    # True when deployed with HTTPS

    SESSION_COOKIE_SECURE = (
        os.environ.get(
            "RENDER"
        ) == "true"
    )