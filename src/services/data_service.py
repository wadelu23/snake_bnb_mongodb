from typing import List, Optional

import datetime

import bson

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner
from data.snakes import Snake


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects(email=email).first()
    return owner
