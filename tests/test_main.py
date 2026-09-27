import pytest
from datetime import datetime, timedelta

def test_signup(client):
    response = client.post("/users/signup", json={
        "name": "Test User",
        "email": "test@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    assert "id" in response.json()

def test_login(client):
    # First, sign up the user if not exists (in isolated function scope it exists if tests were sequential but we use transaction rollback so we must create it)
    client.post("/users/signup", json={
        "name": "Test User 2",
        "email": "test2@example.com",
        "password": "strongpassword123"
    })
    response = client.post("/users/login", data={
        "username": "test2@example.com",
        "password": "strongpassword123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_create_centre_and_test(client):
    # Create Centre
    response = client.post("/centres/", json={
        "name": "Apollo Diagnostics",
        "location": "New York"
    })
    assert response.status_code == 201
    centre_id = response.json()["id"]
    
    # Create Test
    test_response = client.post(f"/centres/{centre_id}/tests", json={
        "name": "MRI Scan",
        "price": 500.0
    })
    assert test_response.status_code == 201
    assert test_response.json()["name"] == "MRI Scan"

def test_booking_flow(client):
    # Setup Data
    client.post("/users/signup", json={"name": "Booker", "email": "booker@example.com", "password": "pass"})
    login_res = client.post("/users/login", data={"username": "booker@example.com", "password": "pass"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    c_res = client.post("/centres/", json={"name": "City Lab", "location": "LA"})
    centre_id = c_res.json()["id"]
    t_res = client.post(f"/centres/{centre_id}/tests", json={"name": "Blood Test", "price": 50.0})
    test_id = t_res.json()["id"]

    # Book a test
    appointment = (datetime.utcnow() + timedelta(days=2)).isoformat()
    book_res = client.post("/bookings/", json={
        "test_id": test_id,
        "appointment_date": appointment
    }, headers=headers)
    
    assert book_res.status_code == 201
    booking_id = book_res.json()["id"]
    assert book_res.json()["status"] == "PENDING"
    
    # Simulate Payment
    pay_res = client.post("/payments/", json={
        "booking_id": booking_id,
        "amount": 50.0
    }, headers=headers)
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] in ["SUCCESS", "FAILED"]
    
    # Trigger Webhook Manually to test idempotency
    event_id = "test-event-123"
    webhook_res_1 = client.post("/payments/webhook/", json={
        "event_id": event_id,
        "booking_id": booking_id,
        "status": "SUCCESS"
    })
    assert webhook_res_1.status_code == 200
    assert webhook_res_1.json()["message"] == "Webhook processed successfully"
    
    # Verify Booking Updated
    book_get = client.get(f"/bookings/{booking_id}", headers=headers)
    assert book_get.json()["status"] == "CONFIRMED"
    
    # Trigger Webhook Again (Idempotency)
    webhook_res_2 = client.post("/payments/webhook/", json={
        "event_id": event_id,
        "booking_id": booking_id,
        "status": "SUCCESS"
    })
    assert webhook_res_2.status_code == 200
    assert webhook_res_2.json()["message"] == "Webhook already processed"
