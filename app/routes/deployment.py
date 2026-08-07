import json
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app import db
from app.decorators import login_required
from app.models import Deployment, UnitInventory, User


# ==================================
# DEPLOYMENT BLUEPRINT
# ==================================

deployment_bp = Blueprint(
    "deployment",
    __name__,
)


# ==================================
# SEARCH AVAILABLE UNITS
# ==================================

@deployment_bp.route("/deployment/search-units")
@login_required
def search_units():
    search = (request.args.get("search", "") or "").strip()

    if not search:
        return {"units": []}

    units = (
        UnitInventory.query
        .filter(
            UnitInventory.status == "Available",
            db.or_(
                UnitInventory.asset_code.ilike(f"%{search}%"),
                UnitInventory.brand.ilike(f"%{search}%"),
                UnitInventory.model.ilike(f"%{search}%"),
                UnitInventory.serial_number.ilike(f"%{search}%"),
            ),
        )
        .order_by(UnitInventory.asset_code.asc())
        .limit(10)
        .all()
    )

    return {
        "units": [
            {
                "id": unit.id,
                "asset_code": unit.asset_code,
                "unit_category": unit.unit_category,
                "brand": unit.brand,
                "model": unit.model,
                "serial_number": unit.serial_number,
                "status": unit.status,
            }
            for unit in units
        ]
    }


# ==================================
# HELPERS
# ==================================

def _parse_optional_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_selected_unit_ids(raw_value):
    """Return a de-duplicated list of positive integer unit IDs."""
    try:
        parsed = json.loads(raw_value or "[]")
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid selected unit data.") from exc

    if not isinstance(parsed, list):
        raise ValueError("Invalid selected unit data.")

    unit_ids = []
    seen = set()

    for item in parsed:
        # Backward-compatible with the previous JS that stored whole objects.
        raw_id = item.get("id") if isinstance(item, dict) else item

        try:
            unit_id = int(raw_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("One or more selected units are invalid.") from exc

        if unit_id <= 0:
            raise ValueError("One or more selected units are invalid.")

        if unit_id not in seen:
            seen.add(unit_id)
            unit_ids.append(unit_id)

    return unit_ids


# ==================================
# DEPLOYMENT PAGE
# ==================================

@deployment_bp.route(
    "/deployment",
    methods=["GET", "POST"],
)
@login_required
def deployment():
    if request.method == "GET":
        sales_agents = (
            User.query
            .filter_by(role="Sales", is_active=True)
            .order_by(User.full_name.asc())
            .all()
        )

        technicians = (
            User.query
            .filter_by(role="Technician", is_active=True)
            .order_by(User.full_name.asc())
            .all()
        )

        return render_template(
            "deployment/deployment.html",
            sales_agents=sales_agents,
            technicians=technicians,
        )

    # ==================================
    # GET FORM DATA
    # ==================================

    selected_units_raw = request.form.get("selected_units", "")
    company_name = (request.form.get("company_name") or "").strip()
    sales_agent_id = request.form.get("sales_agent_id", type=int)
    technician_id = request.form.get("technician_id", type=int)

    contract_start = (request.form.get("contract_start") or "").strip()
    contract_end = (request.form.get("contract_end") or "").strip()
    monthly_rate = (request.form.get("monthly_rate") or "").strip()
    department = (request.form.get("department") or "").strip()
    location = (request.form.get("location") or "").strip()
    deployment_date = (request.form.get("deployment_date") or "").strip()
    transaction_type = (request.form.get("transaction_type") or "").strip()
    black_meter = (request.form.get("black_meter") or "0").strip()
    color_meter = (request.form.get("color_meter") or "0").strip()
    remarks = (request.form.get("remarks") or "").strip()

    # ==================================
    # REQUIRED FIELD VALIDATION
    # ==================================

    if not company_name:
        flash("Company name is required.", "danger")
        return redirect(url_for("deployment.deployment"))

    if not sales_agent_id:
        flash("Please select a sales agent.", "danger")
        return redirect(url_for("deployment.deployment"))

    if not technician_id:
        flash("Please select a technician.", "danger")
        return redirect(url_for("deployment.deployment"))

    try:
        unit_ids = _parse_selected_unit_ids(selected_units_raw)
    except ValueError as error:
        flash(str(error), "danger")
        return redirect(url_for("deployment.deployment"))

    if not unit_ids:
        flash("Please select at least one available unit.", "danger")
        return redirect(url_for("deployment.deployment"))

    # ==================================
    # VALIDATE SALES + TECHNICIAN
    # ==================================

    sales_agent = db.session.get(User, sales_agent_id)
    technician = db.session.get(User, technician_id)

    if (
        sales_agent is None
        or not sales_agent.is_active
        or sales_agent.role != "Sales"
    ):
        flash("The selected sales agent is invalid or inactive.", "danger")
        return redirect(url_for("deployment.deployment"))

    if (
        technician is None
        or not technician.is_active
        or technician.role != "Technician"
    ):
        flash("The selected technician is invalid or inactive.", "danger")
        return redirect(url_for("deployment.deployment"))

    # ==================================
    # CONVERT DATE + NUMBER VALUES
    # ==================================

    try:
        contract_start_value = _parse_optional_date(contract_start)
        contract_end_value = _parse_optional_date(contract_end)
        deployment_date_value = _parse_optional_date(deployment_date)
    except ValueError:
        flash("One or more dates are invalid.", "danger")
        return redirect(url_for("deployment.deployment"))

    if (
        contract_start_value
        and contract_end_value
        and contract_end_value < contract_start_value
    ):
        flash("Contract end date cannot be earlier than contract start date.", "danger")
        return redirect(url_for("deployment.deployment"))

    try:
        monthly_rate_value = Decimal(monthly_rate) if monthly_rate else None
        black_meter_value = int(black_meter)
        color_meter_value = int(color_meter)
    except (InvalidOperation, ValueError):
        flash("Monthly rate and meter values must be valid numbers.", "danger")
        return redirect(url_for("deployment.deployment"))

    if monthly_rate_value is not None and monthly_rate_value < 0:
        flash("Monthly rate cannot be negative.", "danger")
        return redirect(url_for("deployment.deployment"))

    if black_meter_value < 0 or color_meter_value < 0:
        flash("Meter readings cannot be negative.", "danger")
        return redirect(url_for("deployment.deployment"))

    # ==================================
    # GET + VALIDATE ALL SELECTED UNITS
    # ==================================

    selected_units = (
        UnitInventory.query
        .filter(UnitInventory.id.in_(unit_ids))
        .all()
    )

    units_by_id = {unit.id: unit for unit in selected_units}

    missing_ids = [unit_id for unit_id in unit_ids if unit_id not in units_by_id]
    if missing_ids:
        flash("One or more selected units no longer exist.", "danger")
        return redirect(url_for("deployment.deployment"))

    unavailable_units = [
        units_by_id[unit_id]
        for unit_id in unit_ids
        if units_by_id[unit_id].status != "Available"
    ]

    if unavailable_units:
        unavailable_codes = ", ".join(
            unit.asset_code or str(unit.id)
            for unit in unavailable_units
        )
        flash(
            f"These units are no longer available: {unavailable_codes}.",
            "danger",
        )
        return redirect(url_for("deployment.deployment"))

    # ==================================
    # CREATE ONE DEPLOYMENT ROW PER UNIT
    # ==================================

    try:
        for unit_id in unit_ids:
            selected_unit = units_by_id[unit_id]

            new_deployment = Deployment(
                unit_id=selected_unit.id,
                company_name=company_name,
                sales_agent_id=sales_agent.id,
                technician_id=technician.id,
                contract_start=contract_start_value,
                contract_end=contract_end_value,
                monthly_rate=monthly_rate_value,
                department=department or None,
                location=location or None,
                deployment_date=deployment_date_value,
                transaction_type=transaction_type or None,
                black_meter=black_meter_value,
                color_meter=color_meter_value,
                remarks=remarks or None,
            )

            db.session.add(new_deployment)
            selected_unit.status = "Installed"

        # One atomic commit: either every selected unit is deployed, or none are.
        db.session.commit()

        unit_count = len(unit_ids)
        unit_word = "unit" if unit_count == 1 else "units"

        flash(
            f"{unit_count} {unit_word} deployed successfully to {company_name}.",
            "success",
        )

        return redirect(url_for("deployment.deployment"))

    except Exception:
        db.session.rollback()
        flash(
            "Unable to save the deployment. No selected units were deployed.",
            "danger",
        )
        return redirect(url_for("deployment.deployment"))
