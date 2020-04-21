from enum import Enum, unique, auto


@unique
class PaymentStatus(Enum):
    not_paid = auto()
    paid = auto()
    payment_failed = auto()
    refunded = auto()


@unique
class TransportationOfferStatus(Enum):
    opened = auto()
    completed = auto()
    canceled = auto()


@unique
class TransportationTarget(Enum):
    people = auto()
    cargo = auto()
