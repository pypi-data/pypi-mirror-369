# CBE Payment Receipt Verifier

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A robust Python package for verifying Commercial Bank of Ethiopia (CBE) payment receipts by reference number and account suffix.

## Features

- **Receipt Verification**: Validate CBE payment receipts using transaction references
- **PDF Parsing**: Extract transaction details from CBE PDF receipts
- **Error Handling**: Comprehensive error handling with retry mechanism
- **Multiple Date Formats**: Supports various date formats found in receipts
- **SSL Configuration**: Configurable SSL verification for secure connections

## Installation

```bash
pip install cbe-verify

```
## Usage 

```python

from cbe_verify import CBEVerifier

verifier = CBEVerifier()
result = verifier.verify("FT12345678", "1234578")  # Reference + last 8 digits

if result["success"]:
    print(f"Verified payment of {result['amount']} ETB")
    print(f"Transaction date: {result['date']}")
else:
    print(f"Verification failed: {result['error']}")

```

```


```
## Response Format

```bash

{
    "success": True,
    "payer": "John Doe",
    "payer_account": "XXXX1234",
    "receiver": "ABC Company",
    "receiver_account": "XXXX5678",
    "amount": 1500.00,
    "date": "2023-10-15T14:30:00",
    "reference": "FT12345678"
}

```
