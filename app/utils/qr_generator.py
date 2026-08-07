import os

import qrcode

from flask import current_app


# ==================================================
# GENERATE QR CODE
# ==================================================

def generate_qr(
    data,
    filename
):

    # ==================================
    # QR FOLDER
    # ==================================

    qr_folder = os.path.join(

        current_app.root_path,

        "..",

        "static",

        "qr_codes"

    )


    # Create the folder if it does not exist

    os.makedirs(

        qr_folder,

        exist_ok=True

    )


    # ==================================
    # CLEAN FILE NAME
    # ==================================

    filename = (

        str(filename)

        .strip()

        .replace("/", "_")

        .replace("\\", "_")

    )


    # ==================================
    # QR IMAGE PATH
    # ==================================

    file_path = os.path.join(

        qr_folder,

        f"{filename}.png"

    )


    # ==================================
    # GENERATE QR
    # ==================================

    qr_image = qrcode.make(

        data

    )


    # ==================================
    # SAVE QR IMAGE
    # ==================================

    qr_image.save(

        file_path

    )


    # ==================================
    # RETURN DATABASE PATH
    # ==================================

    return (

        f"qr_codes/{filename}.png"

    )