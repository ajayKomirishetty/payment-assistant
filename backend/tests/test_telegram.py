from app.services.telegram_service import TelegramService


def test_payment_is_not_invoice_payment():
    service = object.__new__(TelegramService)

    assert not service.is_invoice_payment_request(
        "What is my latest payment?"
    )


def test_pay_invoice_is_invoice_payment():
    service = object.__new__(TelegramService)

    assert service.is_invoice_payment_request(
        "Pay my invoice"
    )


def test_pay_this_is_invoice_payment():
    service = object.__new__(TelegramService)

    assert service.is_invoice_payment_request(
        "Pay this $250.00"
    )


def test_paid_is_confirmation():
    service = object.__new__(TelegramService)

    assert service.is_payment_confirmation("paid")


def test_done_is_confirmation():
    service = object.__new__(TelegramService)

    assert service.is_payment_confirmation("done")