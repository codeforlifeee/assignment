import uuid
import random
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth
from ..tasks import trigger_webhook_task

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=schemas.PaymentSimulateResponse)
def simulate_payment(
    request: Request,
    payment_req: schemas.PaymentSimulateRequest, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify booking exists and belongs to user
    booking = db.query(models.Booking).filter(models.Booking.id == payment_req.booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if booking.status != models.BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Booking is already {booking.status.value}")

    # Simulate payment processing
    status = "SUCCESS" if random.random() > 0.2 else "FAILED"
    event_id = str(uuid.uuid4())
    
    # In a real system, the payment provider would hit our webhook asynchronously
    # We use Celery to call our own webhook reliably
    webhook_url = str(request.base_url) + "payments/webhook/"
    payload = {
        "event_id": event_id,
        "booking_id": booking.id,
        "status": status
    }
    trigger_webhook_task.delay(webhook_url, payload)
    
    return schemas.PaymentSimulateResponse(status=status, transaction_id=event_id)

@router.post("/webhook/")
def payment_webhook(payload: schemas.PaymentWebhookRequest, db: Session = Depends(database.get_db)):
    """
    Idempotent webhook endpoint to receive payment status updates.
    """
    # Check if this event was already processed (Idempotency check)
    existing_event = db.query(models.PaymentEvent).filter(models.PaymentEvent.event_id == payload.event_id).first()
    if existing_event:
        # We already processed this, return 200 OK immediately
        return {"message": "Webhook already processed"}
    
    # Find the booking
    booking = db.query(models.Booking).filter(models.Booking.id == payload.booking_id).first()
    if not booking:
        # Invalid booking ID. We still return 200 so the provider stops retrying.
        # Alternatively, could return 404, but for webhooks, 200 is safer to acknowledge receipt if we can't do anything about it.
        return {"message": "Booking not found, event ignored"}

    # Update booking status
    if payload.status == "SUCCESS":
        booking.status = models.BookingStatus.CONFIRMED
    else:
        booking.status = models.BookingStatus.FAILED
    
    # Record the event to ensure idempotency
    payment_event = models.PaymentEvent(
        event_id=payload.event_id,
        booking_id=payload.booking_id,
        status=payload.status
    )
    
    db.add(payment_event)
    db.commit()
    
    return {"message": "Webhook processed successfully"}
