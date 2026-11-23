from uuid import UUID

from fastapi import APIRouter,status,Depends,Response
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.modules.auth.models import User
from app.modules.bookings.schemas import BookingCreate, BookingResponse
from app.modules.bookings import service
from app.modules.payments import service as payment_service
from app.modules.auth.dependencies import get_current_user
from app.modules.payments.models import Payment, PaymentStatusEnum
from app.modules.payments.schemas import PaymentResponse, PaymentVerifyRequest


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"],
)

@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
)-> BookingResponse:
    return service.create_booking(db=db, user_id=current_user.id, data=data)
    

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    status_code=status.HTTP_200_OK,
)
def get_booking_details(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
)-> BookingResponse:
    return service.get_booking_details(db=db, user_id=current_user.id, booking_id=booking_id)



@router.post(
    "/{booking_id}/cancel",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    service.cancel_booking(db=db, user_id=current_user.id, booking_id=booking_id)


@router.post(
    "/{booking_id}/payments",
    status_code=status.HTTP_201_CREATED,
    response_model=PaymentResponse
)
def create_payment_attempt(
    booking_id: UUID,
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
)-> Payment:
    payment, created = payment_service.create_payment_attempt(db=db, user_id=current_user.id, booking_id=booking_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return payment
    

@router.get(
    "/{booking_id}/payments/{payment_id}",
    status_code=status.HTTP_200_OK,
    response_model=PaymentResponse
)
def get_payment_details(
    booking_id: UUID,
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
)-> Payment:
    return payment_service.get_payment_details(db=db, user_id=current_user.id, booking_id=booking_id, payment_id=payment_id)


@router.post(
    "/{booking_id}/payments/{payment_id}/verify",
    status_code=status.HTTP_200_OK,
)
def verify_checkout_payment(
    booking_id: UUID,
    payment_id: UUID,
    data: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> dict[str, PaymentStatusEnum]:
    payment_status = payment_service.verify_checkout_payment(
        db=db,
        payment_id=payment_id,
        booking_id=booking_id,
        user_id=current_user.id,
        data=data
    )
    return {"payment_status": payment_status}