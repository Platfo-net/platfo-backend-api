from pydantic import UUID4
from app import services, schemas
from fastapi import APIRouter, Depends, Security, status
from app import models
from app.api import deps
from app.constants.role import Role
from sqlalchemy.orm import Session
from app.constants.errors import Error
from app.constants.payment_status import PaymentStatus
from app.core.exception import raise_http_exception

router = APIRouter(prefix="/invoice")


@router.post("/", response_model=schemas.credit.Invoice)
def create_invoice(
        *,
        db: Session = Depends(deps.get_db),
        obj_in: schemas.credit.InvoiceCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    plan = services.credit.plan.get_by_uuid(db, uuid=obj_in.plan_id)
    if not plan:
        return raise_http_exception(Error.PLAN_NOT_FOUND)
    if not plan.is_active:
        return raise_http_exception(Error.PLAN_NOT_ACTIVE)

    invoice_in = schemas.credit.InvoiceCreate(
        plan_id=plan.id,
        user_id=current_user.id,
        amount=plan.discounted_price,
        currency=plan.currency,
        bought_on_discount=plan.is_discounted,
        plan_name=plan.title,
        module=plan.module,
        extend_days=plan.extend_days,
        extend_count=plan.extend_count,
    )
    db_invoice = services.credit.invoice.create(db, obj_in=invoice_in)

    return schemas.credit.Invoice(
        id=db_invoice.uuid,
        amount=db_invoice.amount,
        currency=db_invoice.currency,
        bought_on_discount=db_invoice.bought_on_discount,
        plan_name=plan.title,
        module=plan.module,
        extend_days=plan.extend_days,
        extend_count=plan.extend_count,
    )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_invoice(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    invoice = services.credit.invoice.get_by_uuid(db, uuid=id)
    if not invoice:
        raise_http_exception(Error.INVOICE_NOT_FOUND)

    if invoice.status == PaymentStatus.FAILED:
        raise_http_exception(Error.INVOICE_CANNOT_DELETE_STATUS_FAILED)

    if invoice.status == PaymentStatus.SUCCESS:
        raise_http_exception(Error.INVOICE_CANNOT_DELETE_STATUS_SUCCESS)

    services.credit.invoice.remove(db, id=invoice.id)
    return


@router.get("/", response_model=schemas.credit.InvoiceList)
def get_invoices(
        *,
        db: Session = Depends(deps.get_db),
        page: int = 1,
        page_size: int = 20,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    invoices, pagination = services.credit.invoice.get_multi_by_user(
        db, user_id=current_user.id,
        page=page, page_size=page_size
    )

    items = [
        schemas.credit.InvoiceListItem(
            plan_name=invoice.plan_name,
            amount=invoice.amount,
            currency=invoice.currency,
            status=invoice.status,
            module=invoice.module,
        ) for invoice in invoices
    ]

    return schemas.credit.InvoiceList(
        items=items,
        pagination=pagination
    )


@router.get("/{id}", response_model=schemas.credit.Invoice)
def get_invoice(
        *,
        db: Session = Depends(deps.get_db),
        id: UUID4,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[
                Role.USER["name"],
                Role.ADMIN["name"],
            ],
        ),
):
    invoice = services.credit.invoice.get_by_uuid(db, uuid=id)
    if not invoice:
        return raise_http_exception(Error.INVOICE_NOT_FOUND)

    return schemas.credit.Invoice(
        id=invoice.uuid,
        amount=invoice.amount,
        currency=invoice.currency,
        bought_on_discount=invoice.bought_on_discount,
        plan_name=invoice.plan.title,
        extend_days=invoice.plan.extend_days,
        extend_count=invoice.plan.extend_count,
        module=invoice.plan.module
    )
