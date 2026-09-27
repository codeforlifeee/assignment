from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from .models import BookingStatus

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DiagnosticTestBase(BaseModel):
    name: str
    price: Decimal

class DiagnosticTestCreate(DiagnosticTestBase):
    pass

class DiagnosticTestResponse(DiagnosticTestBase):
    id: int
    centre_id: int

    class Config:
        from_attributes = True

class CentreBase(BaseModel):
    name: str
    location: str

class CentreCreate(CentreBase):
    pass

class CentreResponse(CentreBase):
    id: int
    tests: List[DiagnosticTestResponse] = []

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    test_id: int
    appointment_date: datetime

class BookingResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    centre_id: int
    appointment_date: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentSimulateRequest(BaseModel):
    booking_id: int
    # In a real app we might pass card details etc., here we mock it
    amount: Decimal

class PaymentSimulateResponse(BaseModel):
    status: str
    transaction_id: str

class PaymentWebhookRequest(BaseModel):
    event_id: str
    booking_id: int
    status: str  # SUCCESS or FAILED
