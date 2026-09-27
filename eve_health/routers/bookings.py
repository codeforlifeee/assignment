from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, auth

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post("/", response_model=schemas.BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking: schemas.BookingCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Verify test exists
    test = db.query(models.DiagnosticTest).filter(models.DiagnosticTest.id == booking.test_id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Diagnostic test not found")
    
    # Create booking
    new_booking = models.Booking(
        user_id=current_user.id,
        test_id=test.id,
        centre_id=test.centre_id,
        appointment_date=booking.appointment_date,
        amount=test.price,
        status=models.BookingStatus.PENDING
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=List[schemas.BookingResponse])
def get_user_bookings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user),
    skip: int = 0, limit: int = 100
):
    return db.query(models.Booking).filter(models.Booking.user_id == current_user.id).offset(skip).limit(limit).all()

@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")
    return booking

@router.patch("/{booking_id}/cancel", response_model=schemas.BookingResponse)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this booking")
    if booking.status != models.BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be cancelled")
    
    booking.status = models.BookingStatus.CANCELLED
    db.commit()
    db.refresh(booking)
    return booking

