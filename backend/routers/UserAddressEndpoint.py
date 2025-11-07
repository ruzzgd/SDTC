from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from DatabaseConnector import get_db
from database.UserTable import Address as AddressTable, User
from models.UserModel import Address, AddressResponse, ActivateAddress
import tools
from database.AdminTable import RecentActivity
from datetime import datetime
router = APIRouter(prefix="/users", tags=["users"])

# ---------------- Get All Addresses ----------------
@router.get("/addresses", response_model=list[AddressResponse])
def get_addresses(user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    addresses = db.query(AddressTable).filter(AddressTable.user_id == user.id).all()
    return addresses


# ---------------- Add New Address ----------------
@router.post("/address/add", response_model=AddressResponse)
def add_address(address: Address, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_address = AddressTable(
        user_id=user.id,
        house_number=address.house_number,
        street=address.street,
        barangay=address.barangay,
        city=address.city,
        province=address.province,
        is_active=False
    )

    db.add(new_address)

    # Log recent activity
    activity = RecentActivity(
        email=user_email,
        activity="Added a new address",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)

    db.commit()
    db.refresh(new_address)
    return new_address


# ---------------- Activate Address ----------------
@router.put("/address/{address_id}/activate", response_model=AddressResponse)
def activate_address(address_id: int, request: ActivateAddress, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    address = db.query(AddressTable).filter(AddressTable.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if request.is_active:
        db.query(AddressTable).filter(AddressTable.user_id == address.user_id).update(
            {AddressTable.is_active: False}
        )
        address.is_active = True
        action = "Activated"
    else:
        address.is_active = False
        action = "Deactivated"

    # Log recent activity
    activity = RecentActivity(
        email=user_email,
        activity=f"{action} an address",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)

    db.commit()
    db.refresh(address)
    return address


# ---------------- Delete Address ----------------
@router.delete("/address/{address_id}", response_model=AddressResponse)
def delete_address(address_id: int, user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    address = db.query(AddressTable).filter(AddressTable.id == address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(address)

    # Log recent activity
    activity = RecentActivity(
        email=user_email,
        activity="Deleted an address",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)

    db.commit()
    return address
