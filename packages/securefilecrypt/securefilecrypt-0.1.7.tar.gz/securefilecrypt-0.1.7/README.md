# securefilecrypt — Simple AES-GCM File Encryption
**SecureFileCrypt** is a Python utility for encrypting and decrypting files using **AES-256-GCM** with password-based key derivation (PBKDF2-HMAC-SHA256).  
It is designed for ease of use while providing strong, modern encryption with authentication to ensure data confidentiality and integrity.

## Features

- AES-256 in **Galois/Counter Mode (GCM)** for authenticated encryption
- Password-based key derivation using **PBKDF2-HMAC-SHA256** with configurable iterations
- Random **salt** and **nonce** generated for each encryption
- Automatic salt length derived from password characteristics
- Simple file-based workflow: encrypt and decrypt with one function call
- Compatible across Python 3.6+ on Windows, Linux, and macOS

## Security Design

- **Encryption algorithm:** AES-256-GCM (confidentiality + authentication)
- **Key derivation:** PBKDF2-HMAC-SHA256, 100,000 iterations
- **Salt:** Random per file, length based on password contents
- **Nonce:** 12 bytes random per encryption
- **Password requirements:** At least 12 base36 characters (`0-9a-z`)

## Installation

```bash
pip install securefilecrypt
````

## Quick Start

### Encrypt a file

```python
from securefilecrypt import EncryptFile

status, message = EncryptFile("secret.txt", "secret.enc", "mypassword123abc")
if not status:
  print("Error:", message)
else:
  print("File encrypted successfully!")
```

### Decrypt a file

```python
from securefilecrypt import DecryptFile

status, message = DecryptFile("secret.enc", "secret_decrypted.txt", "mypassword123abc")
if not status:
  print("Error:", message)
else:
  print("File decrypted successfully!")
```

## Command line tool

On the command line the library can be called with the following arguments:

```
Usage: sfcrypt <input_file> <output_file> (--encrypt|--decrypt) (--pw:<password>|--ev:<envvar>)

<input_filename>  : Input file for encryption or decryption

<output_filename> : Encrypted / decrypted file to produce

--encrypt           : Encryption mode

--decrypt           : Decryption mode

--pw:<password>   : Password for encryption/decription

--ev:<envvar>     : Get password for encryption / decryption from an environment variable
```

## API Reference

### `EncryptData(input_file, password)`

Encrypts `input_file` using AES-256-GCM with provided `password`.
Returns: 
- `status' (bool): True if successful, False something went wrong
- `message` (str): Error message in case of error, otherwise empty
- `data` (bytes): Encrypted bytes

### `DecryptData(input_file, password)`

Decrypts `input_file` using AES-256-GCM with provided `password`.
Returns: 
- `status' (bool): True if successful, False something went wrong
- `message` (str): Error message in case of error, otherwise empty
- `data` (bytes): Decrypted bytes

### `EncryptFile(input_file, output_file, password)`

Encrypts `input_file` into `output_file` using AES-256-GCM with provided `password`.
Returns: 
- `status' (bool): True if successful, False something went wrong
- `message` (str): Error message in case of error, otherwise empty

### `DecryptFile(input_file, output_file, password)`

Decrypts `input_file` into `output_file` using AES-256-GCM with provided `password`.
Returns: 
- `status' (bool): True if successful, False something went wrong
- `message` (str): Error message in case of error, otherwise empty

## Security Notes

* Always use a **strong password** (long, random, mix of letters/numbers).
* Store your password securely — if lost, data **cannot** be recovered.
* PBKDF2 is secure, but for higher resistance to GPU cracking, consider upgrading to **Argon2id** in the future.

## License

MIT License — do anything with it, but no warranty.

## Changelog

See the full changelog [here](https://github.com/diegomarin75-work/SecureFileCrypt/blob/main/CHANGELOG.md).