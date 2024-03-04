from enum import Enum


class CommandResponseType(str, Enum):
    not_supported = 'NOT_SUPPORTED'
    rejected = 'REJECTED'
    accepted = 'ACCEPTED'
    unknown_session = 'UNKNOWN_SESSION'


class CommandResultType(str, Enum):
    accepted = 'ACCEPTED'
    canceled_reservation = 'CANCELED_RESERVATION'
    evse_occupied = 'EVSE_OCCUPIED'
    evse_inoperative = 'EVSE_INOPERATIVE'
    failed = 'FAILED'
    not_supported = 'NOT_SUPPORTED'
    rejected = 'REJECTED'
    timeout = 'TIMEOUT'
    unknown_reservation = 'UNKNOWN_RESERVATION'


class CommandType(str, Enum):
    cancel_reservation = 'CANCEL_RESERVATION'
    reserve_now = 'RESERVE_NOW'
    start_session = 'START_SESSION'
    stop_session = 'STOP_SESSION'
    unlock_connector = 'UNLOCK_CONNECTOR'
