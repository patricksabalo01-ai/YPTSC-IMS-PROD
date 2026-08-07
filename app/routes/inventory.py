from sqlalchemy import func

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from datetime import datetime

from app import db

from app.models import (
    UnitInventory,
    PartInventory,
)

from app.decorators import login_required

from app.utils.qr_generator import generate_qr

# ==================================================
# INVENTORY BLUEPRINT
# ==================================================

inventory_bp = Blueprint(
    "inventory",
    __name__,
)


# ==================================================
# UNITS INVENTORY
# ==================================================


@inventory_bp.route("/inventory/units")
@login_required
def units_inventory():

    units = UnitInventory.query.order_by(UnitInventory.id.desc()).all()

    inventory_data = {
        "title": "Units Inventory",
        "module": "units",
        "units": units,
    }

    return render_template(
        "inventory/units_inventory.html",
        inventory_data=inventory_data,
    )


# ==================================================
# REGISTER UNIT PAGE
# ==================================================


@inventory_bp.route("/inventory/unit-register")
@login_required
def unit_register():

    register_data = {
        "title": "Register Unit",
        "module": "units",
    }

    return render_template(
        "inventory/unit_register.html",
        register_data=register_data,
    )


# ==================================================
# ASSET CODE GENERATOR
# ==================================================


def generate_asset_code():

    last_unit = UnitInventory.query.order_by(UnitInventory.id.desc()).first()

    if not last_unit:

        return "YPTSC-UNIT-00001"

    return f"YPTSC-UNIT-" f"{last_unit.id + 1:05d}"


# ==================================================
# REGISTER UNIT PROCESS
# ==================================================


@inventory_bp.route(
    "/inventory/register-unit",
    methods=["POST"],
)
@login_required
def register_unit():

    # ==================================
    # GET FORM DATA
    # ==================================

    unit_category = (request.form.get("unit_category") or "").strip()

    brand = (request.form.get("brand") or "").strip()

    model = (request.form.get("model") or "").strip()

    serial_number = (request.form.get("serial_number") or "").strip()

    ownership_type = (request.form.get("ownership_type") or "").strip()

    supplier = (request.form.get("supplier") or "").strip()

    warranty = (request.form.get("warranty") or "").strip()

    status = (request.form.get("status") or "Available").strip()

    # ==================================
    # CHECK SERIAL NUMBER
    # ==================================

    existing_unit = UnitInventory.query.filter_by(serial_number=serial_number).first()

    if existing_unit:

        flash(
            "Serial number already exists.",
            "danger",
        )

        return redirect(url_for("inventory.unit_register"))

    # ==================================
    # GENERATE ASSET CODE
    # ==================================

    asset_code = generate_asset_code()

    # ==================================
    # UNIT QR DATA
    # QR CONTAINS ASSET CODE ONLY
    # ==================================

    unit_qr_data = asset_code

    # ==================================
    # GENERATE UNIT QR
    # ==================================

    qr_code = generate_qr(
        data=unit_qr_data,
        filename=asset_code,
    )

    # ==================================
    # CREATE UNIT
    # ==================================

    unit = UnitInventory(
        asset_code=asset_code,
        qr_code=qr_code,
        unit_category=unit_category,
        brand=brand,
        model=model,
        serial_number=serial_number,
        ownership_type=ownership_type,
        supplier=(supplier or None),
        purchase_date=(request.form.get("purchase_date") or None),
        date_delivered=(request.form.get("date_delivered") or None),
        purchase_price=(
            request.form.get(
                "purchase_price",
                type=float,
            )
        ),
        warranty=(warranty or None),
        status=status,
        created_at=datetime.utcnow(),
    )

    # ==================================
    # SAVE TO POSTGRESQL
    # ==================================

    try:

        db.session.add(unit)

        db.session.commit()

        flash(
            "Unit successfully registered.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Database error: {error}",
            "danger",
        )

        return redirect(url_for("inventory.unit_register"))

    return redirect(url_for("inventory.units_inventory"))


# ==================================================
# DELETE UNIT
# ==================================================


@inventory_bp.route(
    "/inventory/delete-unit/<asset_code>",
    methods=["POST"],
)
@login_required
def delete_unit(asset_code):

    unit = UnitInventory.query.filter_by(asset_code=asset_code).first()

    if unit is None:

        flash(
            "Unit not found.",
            "danger",
        )

        return redirect(url_for("inventory.units_inventory"))

    try:

        db.session.delete(unit)

        db.session.commit()

        flash(
            "Unit successfully deleted.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Database error: {error}",
            "danger",
        )

    return redirect(url_for("inventory.units_inventory"))


# ==================================================
# VIEW UNIT DETAILS
# ==================================================


@inventory_bp.route("/inventory/view-unit/<asset_code>")
@login_required
def view_unit(asset_code):

    unit = UnitInventory.query.filter_by(asset_code=asset_code).first()

    if unit is None:

        flash(
            "Unit not found.",
            "danger",
        )

        return redirect(url_for("inventory.units_inventory"))

    return render_template(
        "inventory/unit_view.html",
        unit=unit,
    )


# ==================================================
# EDIT UNIT PAGE
# ==================================================


@inventory_bp.route("/inventory/edit-unit/<asset_code>")
@login_required
def edit_unit(asset_code):

    unit = UnitInventory.query.filter_by(asset_code=asset_code).first()

    if unit is None:

        flash(
            "Unit not found.",
            "danger",
        )

        return redirect(url_for("inventory.units_inventory"))

    return render_template(
        "inventory/unit_edit.html",
        unit=unit,
    )


# ==================================================
# UPDATE UNIT
# ==================================================


@inventory_bp.route(
    "/inventory/update-unit/<asset_code>",
    methods=["POST"],
)
@login_required
def update_unit(asset_code):

    unit = UnitInventory.query.filter_by(asset_code=asset_code).first()

    if unit is None:

        flash(
            "Unit not found.",
            "danger",
        )

        return redirect(url_for("inventory.units_inventory"))

    try:

        # ==================================
        # UNIT INFORMATION
        # ==================================

        unit.unit_category = request.form.get("unit_category")

        unit.brand = request.form.get("brand")

        unit.model = request.form.get("model")

        unit.serial_number = request.form.get("serial_number")

        # ==================================
        # OWNERSHIP / PURCHASE
        # ==================================

        unit.ownership_type = request.form.get("ownership_type")

        unit.supplier = request.form.get("supplier")

        unit.purchase_date = request.form.get("purchase_date") or None

        unit.date_delivered = request.form.get("date_delivered") or None

        unit.purchase_price = request.form.get("purchase_price") or None

        unit.warranty = request.form.get("warranty")

        unit.status = request.form.get("status")

        unit.updated_at = datetime.utcnow()

        # ==================================
        # QR REMAINS UNCHANGED
        # QR CONTAINS ASSET CODE ONLY
        # ==================================

        # ==================================
        # SAVE CHANGES
        # ==================================

        db.session.commit()

        flash(
            "Unit successfully updated.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Unable to update unit: {error}",
            "danger",
        )

    return redirect(url_for("inventory.units_inventory"))


# ==================================================
# PARTS INVENTORY
# ==================================================


@inventory_bp.route("/inventory/parts")
@login_required
def parts_inventory():

    parts = PartInventory.query.order_by(PartInventory.id.desc()).all()

    inventory_data = {
        "title": "Parts Inventory",
        "module": "parts",
        "parts": parts,
    }

    return render_template(
        "inventory/parts_inventory.html",
        inventory_data=inventory_data,
    )


# ==================================================
# LOW STOCK ALERTS
# ==================================================


@inventory_bp.route("/inventory/low-stock")
@login_required
def low_stock():

    # ==================================
    # LOW STOCK LIMIT
    # ==================================

    LOW_STOCK_LIMIT = 5

    # ==================================
    # COUNT AVAILABLE UNITS
    # ==================================

    available_units_count = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "available"
    ).count()

    # ==================================
    # GET TOTAL PART STOCK
    # ==================================

    total_part_stock = db.session.query(
        func.coalesce(
            func.sum(PartInventory.stock),
            0,
        )
    ).scalar()

    # ==================================
    # CREATE ALERT DATA
    # ==================================

    alert_items = []

    # ==================================
    # UNIT ALERT
    # ==================================

    if available_units_count == 0:

        unit_alert_status = "Out of Stock"

    elif available_units_count <= LOW_STOCK_LIMIT:

        unit_alert_status = "Low Stock"

    else:

        unit_alert_status = "Normal"

    alert_items.append(
        {
            "inventory_type": "Unit",
            "item_name": ("Available Units"),
            "current_count": (available_units_count),
            "minimum_count": (LOW_STOCK_LIMIT),
            "alert_status": (unit_alert_status),
        }
    )

    # ==================================
    # PART ALERT
    # ==================================

    if total_part_stock == 0:

        part_alert_status = "Out of Stock"

    elif total_part_stock <= LOW_STOCK_LIMIT:

        part_alert_status = "Low Stock"

    else:

        part_alert_status = "Normal"

    alert_items.append(
        {
            "inventory_type": "Part",
            "item_name": ("Total Parts Stock"),
            "current_count": (total_part_stock),
            "minimum_count": (LOW_STOCK_LIMIT),
            "alert_status": (part_alert_status),
        }
    )

    # ==================================
    # COUNT ACTIVE ALERTS
    # ==================================

    alert_count = sum(
        1
        for item in alert_items
        if (
            item["alert_status"]
            in [
                "Low Stock",
                "Out of Stock",
            ]
        )
    )

    # ==================================
    # SEND DATA TO HTML
    # ==================================

    low_stock_data = {
        "title": "Low Stock Alerts",
        "items": alert_items,
        "alert_count": alert_count,
        "available_units": (available_units_count),
        "total_parts": (total_part_stock),
        "low_stock_limit": (LOW_STOCK_LIMIT),
    }

    return render_template(
        "inventory/low_stock.html",
        low_stock_data=low_stock_data,
    )


# ==================================================
# REGISTER PART PAGE
# ==================================================


@inventory_bp.route("/inventory/part-register")
@login_required
def part_register():

    register_data = {
        "title": "Register Part",
        "module": "parts",
    }

    return render_template(
        "inventory/part_register.html",
        register_data=register_data,
    )


# ==================================================
# GENERATE PART CODE
# ==================================================


def generate_part_code():

    last_part = PartInventory.query.order_by(PartInventory.id.desc()).first()

    if not last_part:

        return "YPTSC-PART-00001"

    return f"YPTSC-PART-" f"{last_part.id + 1:05d}"


# ==================================================
# AUTOMATIC STOCK STATUS
# ==================================================


def get_part_status(
    stock,
    minimum_stock,
):

    if stock <= 0:

        return "Out of Stock"

    if stock <= minimum_stock:

        return "Low Stock"

    return "Available"


# ==================================================
# REGISTER PART PROCESS
# ==================================================


@inventory_bp.route(
    "/inventory/register-part",
    methods=["POST"],
)
@login_required
def register_part():

    # ==================================
    # GET FORM DATA
    # ==================================

    category = (request.form.get("category") or "").strip()

    part_number = (request.form.get("part_number") or "").strip()

    description = (request.form.get("description") or "").strip()

    brand = (request.form.get("brand") or "").strip()

    compatible_model = (request.form.get("compatible_model") or "").strip()

    supplier = (request.form.get("supplier") or "").strip()

    location = (request.form.get("location") or "").strip()

    remarks = (request.form.get("remarks") or "").strip()

    # ==================================
    # CHECK PART NUMBER
    # ==================================

    if not part_number:

        flash(
            "Part number is required.",
            "danger",
        )

        return redirect(url_for("inventory.part_register"))

    existing_part = PartInventory.query.filter_by(part_number=part_number).first()

    if existing_part:

        flash(
            "Part number already exists.",
            "danger",
        )

        return redirect(url_for("inventory.part_register"))

    # ==================================
    # STOCK VALUES
    # ==================================

    stock = (
        request.form.get(
            "stock",
            type=int,
        )
        or 0
    )

    minimum_stock = (
        request.form.get(
            "minimum_stock",
            type=int,
        )
        or 0
    )

    # ==================================
    # CALCULATE STATUS
    # ==================================

    status = get_part_status(
        stock,
        minimum_stock,
    )

    # ==================================
    # GENERATE PART CODE
    # ==================================

    part_code = generate_part_code()

    # ==================================
    # PART QR DATA
    # QR CONTAINS PART CODE ONLY
    # ==================================

    part_qr_data = part_code

    # ==================================
    # GENERATE PART QR
    # ==================================

    qr_code = generate_qr(
        data=part_qr_data,
        filename=part_code,
    )

    # ==================================
    # CREATE PART
    # ==================================

    part = PartInventory(
        part_code=part_code,
        qr_code=qr_code,
        category=category,
        part_number=part_number,
        description=description,
        brand=(brand or None),
        compatible_model=(compatible_model or None),
        supplier=(supplier or None),
        stock=stock,
        minimum_stock=(minimum_stock),
        location=(location or None),
        status=status,
        remarks=(remarks or None),
        created_at=datetime.utcnow(),
    )

    # ==================================
    # SAVE TO POSTGRESQL
    # ==================================

    try:

        db.session.add(part)

        db.session.commit()

        flash(
            "Part successfully registered.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Database error: {error}",
            "danger",
        )

        return redirect(url_for("inventory.part_register"))

    return redirect(url_for("inventory.parts_inventory"))


# ==================================================
# EDIT PART
# ==================================================


@inventory_bp.route(
    "/inventory/edit-part/<int:part_id>",
    methods=["GET", "POST"],
)
@login_required
def edit_part(part_id):

    # ==================================
    # GET PART
    # ==================================

    part = PartInventory.query.get_or_404(part_id)

    # ==================================
    # SHOW EDIT PAGE
    # ==================================

    if request.method == "GET":

        return render_template(
            "inventory/edit_part.html",
            part=part,
        )

    # ==================================
    # GET FORM VALUES
    # ==================================

    category = (request.form.get("category") or "").strip()

    part_number = (request.form.get("part_number") or "").strip()

    description = (request.form.get("description") or "").strip()

    brand = (request.form.get("brand") or "").strip()

    compatible_model = (request.form.get("compatible_model") or "").strip()

    supplier = (request.form.get("supplier") or "").strip()

    location = (request.form.get("location") or "").strip()

    remarks = (request.form.get("remarks") or "").strip()

    # ==================================
    # STOCK VALUES
    # ==================================

    stock = (
        request.form.get(
            "stock",
            type=int,
        )
        or 0
    )

    minimum_stock = (
        request.form.get(
            "minimum_stock",
            type=int,
        )
        or 0
    )

    # ==================================
    # CHECK DUPLICATE PART NUMBER
    # ==================================

    existing_part = PartInventory.query.filter(
        PartInventory.part_number == part_number,
        PartInventory.id != part.id,
    ).first()

    if existing_part:

        flash(
            "Part number already exists.",
            "danger",
        )

        return redirect(
            url_for(
                "inventory.edit_part",
                part_id=part.id,
            )
        )

    # ==================================
    # UPDATE PART
    # ==================================

    part.category = category

    part.part_number = part_number

    part.description = description

    part.brand = brand or None

    part.compatible_model = compatible_model or None

    part.supplier = supplier or None

    part.stock = stock

    part.minimum_stock = minimum_stock

    part.location = location or None

    part.remarks = remarks or None

    # ==================================
    # AUTOMATIC STATUS
    # ==================================

    part.status = get_part_status(
        stock,
        minimum_stock,
    )

    # ==================================
    # QR REMAINS UNCHANGED
    # QR CONTAINS PART CODE ONLY
    # ==================================

    # ==================================
    # SAVE CHANGES
    # ==================================

    try:

        db.session.commit()

        flash(
            "Part successfully updated.",
            "success",
        )

        return redirect(url_for("inventory.parts_inventory"))

    except Exception as error:

        db.session.rollback()

        flash(
            f"Unable to update part: {error}",
            "danger",
        )

        return redirect(
            url_for(
                "inventory.edit_part",
                part_id=part.id,
            )
        )


# ==================================================
# DELETE PART
# ==================================================


@inventory_bp.route(
    "/inventory/delete-part/<part_code>",
    methods=["POST"],
)
@login_required
def delete_part(part_code):

    part = PartInventory.query.filter_by(part_code=part_code).first()

    if part is None:

        flash(
            "Part not found.",
            "danger",
        )

        return redirect(url_for("inventory.parts_inventory"))

    try:

        db.session.delete(part)

        db.session.commit()

        flash(
            "Part successfully deleted.",
            "success",
        )

    except Exception as error:

        db.session.rollback()

        flash(
            f"Unable to delete part: {error}",
            "danger",
        )

    return redirect(url_for("inventory.parts_inventory"))


# ==================================================
# PRINT UNIT QR CODE
# ==================================================


@inventory_bp.route("/inventory/print-qr/<asset_code>")
@login_required
def print_qr(asset_code):

    # ==================================
    # GET UNIT FROM POSTGRESQL
    # ==================================

    unit = UnitInventory.query.filter_by(asset_code=asset_code).first()

    if unit is None:

        flash(
            "Unit not found.",
            "danger",
        )

        return redirect(url_for("inventory.units_inventory"))

    if not unit.qr_code:

        flash(
            "QR code is not available " "for this unit.",
            "warning",
        )

        return redirect(url_for("inventory.units_inventory"))

    return render_template(
        "inventory/unit_qr_print.html",
        unit=unit,
    )


# ==================================================
# PRINT PART QR CODE
# ==================================================


@inventory_bp.route("/inventory/print-part-qr/<part_code>")
@login_required
def print_part_qr(part_code):

    # ==================================
    # GET PART FROM POSTGRESQL
    # ==================================

    part = PartInventory.query.filter_by(part_code=part_code).first()

    # ==================================
    # PART NOT FOUND
    # ==================================

    if part is None:

        flash(
            "Part not found.",
            "danger",
        )

        return redirect(url_for("inventory.parts_inventory"))

    # ==================================
    # QR NOT AVAILABLE
    # ==================================

    if not part.qr_code:

        flash(
            "QR code is not available " "for this part.",
            "warning",
        )

        return redirect(url_for("inventory.parts_inventory"))

    # ==================================
    # OPEN PRINT PAGE
    # ==================================

    return render_template(
        "inventory/part_qr_print.html",
        part=part,
    )
