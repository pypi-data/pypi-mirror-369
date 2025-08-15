from qr_payment_cz.app import App
from qr_payment_cz.exceptions import ParseException, PaymentException
from qr_payment_cz.print import Print


def main():
    app = App()
    try:
        app.run()
    except (ParseException, PaymentException) as ex:
        Print.err(f"Exception occured while processing payment: {ex}")
        exit(1)


if __name__ == "__main__":
    main()
