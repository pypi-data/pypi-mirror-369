# QR Payment CZ

Tool to generate QR code pictures in PNG format (410x410px) for QR payments in Czech Republic 
based on standart https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

```bash
qr-payment-cz --help
```

```
usage: qr-payment-cz [-h] [-a ACCOUNT] [-i IBAN_ACC] -v AMMOUNT [-m MESSAGE] [-rn RN] [-vs VS] [-ss SS] [-ks KS] [-o OUTPUT_FILE] [-s] [-fs]

QR payment generator for CZE based on https://qr-platba.cz/pro-vyvojare/specifikace-formatu/

options:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account number std bank account format
  -i IBAN_ACC, --iban-account IBAN_ACC
                        Account number in IBAN format
  -v AMMOUNT, --ammount-value AMMOUNT
                        Payment ammount
  -m MESSAGE, --message MESSAGE
                        Message text for payment
  -rn RN, --receiver-name RN
                        Payment receiver name
  -vs VS, --variable-symbol VS
                        Payment variable symbol
  -ss SS, --specific-symbol SS
                        Payment specific symbol
  -ks KS, --constant-symbol KS
                        Payment contant symbol
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output PNG file path
  -s, --silent          Silent mode for info messages
  -fs, --force-silent   Stronger silent mode for all messages

```

# Changelog:

## 0.1.4
Silent mode added.

## 0.1.3
Validation of account number format added.

## 0.1.2
Support for account number defined in usual bank format xxxxxx-xxxxxxxxxx/xxxx.

## 0.1.1
first version supporting IBAN account numbers only.
