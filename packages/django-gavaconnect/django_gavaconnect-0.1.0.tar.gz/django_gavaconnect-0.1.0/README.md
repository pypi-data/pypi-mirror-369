# DJANGO-GAVACONNECT

`gavaconnect` is a reusable Django app that provides a simple and standardized interface for integrating with the GavaConnect KRA APIs (Kenya Revenue Authority), supporting both sandbox and production modes.

It allows you to easily connect to KRA services such as:

- PIN Checker (by PIN)
- PIN Checker (by National ID)
- IT (Income Tax) Exemption Checker
- VAT Exemption Checker
- PRN Search from iTax

## Features
- Easy to install and configure in any Django project
- Sandbox and production environment support
- Centralized API authentication
- Clean exception handling
- Built-in self-test management command
- Type hints for better IDE support

## Installation

```bash
pip install gavaconnect
```

Or install from source:

```bash
git clone https://github.com/mworia-Br/gavaconnect.git
cd gavaconnect
pip install .
```

## Configuration

In your Django settings:

```python
GAVACONNECT = {
    "MODE": "sandbox",  # or "production"
    "CLIENT_ID": "your_client_id",
    "CLIENT_SECRET": "your_client_secret",
    "BASE_URL_SANDBOX": "https://sandbox.gavaconnect.co.ke/api",
    "BASE_URL_PRODUCTION": "https://api.gavaconnect.co.ke/api",
}
```

## Usage

### PIN Checker by PIN
```python
from gavaconnect.api import pin_checker_by_pin

result = pin_checker_by_pin("A123456789B")
print(result)
```

### PIN Checker by National ID
```python
from gavaconnect.api import pin_checker_by_id

result = pin_checker_by_id("12345678")
print(result)
```

### IT Exemption Checker
```python
from gavaconnect.api import it_exemption_checker

result = it_exemption_checker("A123456789B")
print(result)
```

### VAT Exemption Checker
```python
from gavaconnect.api import vat_exemption_checker

result = vat_exemption_checker("A123456789B")
print(result)
```

### Search PRN from iTax
```python
from gavaconnect.api import search_prn

result = search_prn("PRN123456789")
print(result)
```

## Running Self-Test
```bash
python manage.py gavaconnect_selftest
```

This will:
- Test connectivity to GavaConnect
- Check authentication
- Validate sample API requests

## Running Tests
```bash
pytest
```

## License
This project is licensed under the MIT License – see the LICENSE file for details.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Create a Pull Request

## Author
**Brian Nganga**  
[GitHub](https://github.com/mworia-Br) | [LinkedIn](https://www.linkedin.com/in/mworia-br/)

## Disclaimer

This package is not affiliated with or endorsed by Gava Connect. Use it at your own risk.