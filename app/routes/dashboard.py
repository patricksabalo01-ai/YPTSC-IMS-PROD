from flask import (
    Blueprint,
    render_template,
)

from sqlalchemy import func
from app import db

from app.models import (
    UnitInventory,
    PartInventory,
)

from app.decorators import (
    login_required,
)

# ==================================
# BLUEPRINT
# ==================================

dashboard_bp = Blueprint("dashboard", __name__)


# ==================================
# DASHBOARD
# ==================================


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    # ==================================
    # LIVE UNIT INVENTORY COUNTS
    # ==================================

    total_units = UnitInventory.query.count()

    installed = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "installed"
    ).count()

    repair = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "under repair"
    ).count()

    available = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "available"
    ).count()

    reserved = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "reserved"
    ).count()

    pulled_out = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "pulled out"
    ).count()

    disposal = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "disposal"
    ).count()

    # ==================================
    # PARTS INVENTORY COUNTS
    # ==================================

    total_parts = PartInventory.query.count()

    low_stock = PartInventory.query.filter(
        func.lower(PartInventory.status) == "low stock"
    ).count()

    spare_parts = PartInventory.query.filter(
        func.lower(PartInventory.category) == "spare parts"
    ).count()

    consumables = PartInventory.query.filter(
        func.lower(PartInventory.category) == "consumables"
    ).count()

    toner = PartInventory.query.filter(
        func.lower(PartInventory.category) == "toner"
    ).count()

    ink = PartInventory.query.filter(
        func.lower(PartInventory.category) == "ink"
    ).count()

    office_supplies = PartInventory.query.filter(
        func.lower(PartInventory.category) == "office supplies"
    ).count()

    # ==================================
    # LOW STOCK SETTINGS
    # ==================================

    LOW_STOCK_LIMIT = 5

    # ==================================
    # AVAILABLE UNIT COUNT
    # ==================================

    available_units_count = UnitInventory.query.filter(
        func.lower(UnitInventory.status) == "available"
    ).count()

    # ==================================
    # TOTAL PART STOCK
    # ==================================

    total_part_stock = db.session.query(
        func.coalesce(
            func.sum(PartInventory.stock),
            0,
        )
    ).scalar()

    # ==================================
    # LOW STOCK ALERT COUNT
    # ==================================

    low_stock_alerts = 0

    # Units alert

    if available_units_count <= LOW_STOCK_LIMIT:

        low_stock_alerts += 1

    # Parts alert

    if total_part_stock <= LOW_STOCK_LIMIT:

        low_stock_alerts += 1

    # ==================================
    # DASHBOARD DATA
    # ==================================

    dashboard_data = {
        # ==================================
        # EXECUTIVE KPI SUMMARY
        # ==================================
        "total_units": total_units,
        "total_parts": total_parts,
        "installed": installed,
        "repair": repair,
        "low_stock": low_stock_alerts,
        "available_units_count": available_units_count,
        "total_part_stock": total_part_stock,
        # ==================================
        # MACHINE LIFECYCLE STATUS
        # ==================================
        "available": available,
        "reserved": reserved,
        "pulled_out": pulled_out,
        "disposal": disposal,
        # ==================================
        # INVENTORY ACTIVITY
        # ==================================
        "incoming": 0,
        "released": 0,
        "maintenance": 0,
        # ==================================
        # PARTS INVENTORY
        # ==================================
        "spare_parts": spare_parts,
        "consumables": consumables,
        "toner": toner,
        "ink": ink,
        "office_supplies": office_supplies,
        # ==================================
        # REPAIR ANALYTICS
        # ==================================
        "repair_chart": [],
        # ==================================
        # RECENT TRANSACTIONS
        # ==================================
        "recent_transactions": [],
    }

    # ==================================
    # RENDER DASHBOARD
    # ==================================

    return render_template("dashboard.html", dashboard_data=dashboard_data)
