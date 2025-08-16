#Import libraries
import os
import re
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

#Library version
__version__ = "0.1.7"

#Encryption constants
_MIN_PASSWORD_LENGTH=12
_MIN_SALT_LENGTH=16
_NONCE_LENGTH=12
_KEY_LENGTH=32
_KEY_ITERATIONS=100000

#----------------------------------------------------------------------------------------------------------------------
# Check password is compatible (must have 10 base36 digits)
#----------------------------------------------------------------------------------------------------------------------
def _IsPasswordValid(Password):
  Pattern=re.compile(r'[0-9a-z]')
  Matches=Pattern.findall(Password.lower())
  return len(Matches)>=_MIN_PASSWORD_LENGTH

#----------------------------------------------------------------------------------------------------------------------
# Get salt length from password
#----------------------------------------------------------------------------------------------------------------------
def _GetSaltLength(Password):
  PasswordBase36List=re.compile(r'[0-9a-z]').findall(Password.lower())[:_MIN_PASSWORD_LENGTH]
  PasswordBase36=int("".join(PasswordBase36List),36)
  PasswordMod10=PasswordBase36 % 10
  SaltLength=_MIN_SALT_LENGTH+PasswordMod10
  return SaltLength

#----------------------------------------------------------------------------------------------------------------------
# Encryption routine
#----------------------------------------------------------------------------------------------------------------------
def EncryptData(InputFile,Password):
  
  #Check password hass enough length
  if _IsPasswordValid(Password)==False:
    Message=f"Password does not have minimun required amount of base36 chars ({_MIN_PASSWORD_LENGTH})"
    return False,Message,None

  #Get salt length from password
  SaltLength=_GetSaltLength(Password)

  #Generate a random salt
  Salt=os.urandom(SaltLength)

  #Derive a key from the password
  Kdf=PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=_KEY_LENGTH,
    salt=Salt,
    iterations=_KEY_ITERATIONS,
    backend=default_backend()
  )
  Key=Kdf.derive(Password.encode())

  #Generate a random nonce
  Nonce=os.urandom(_NONCE_LENGTH)

  #Read the plaintext from the input file
  try:
    File=open(InputFile,'rb')
    Plaintext=File.read()
    File.close()
  except Exception as Ex:
    Message=f"Unable to read file {InputFile}: {str(Ex)}"
    return False,Message,None

  #Encrypt the plaintext
  try:
    AesGcm=AESGCM(Key)
    Ciphertext=AesGcm.encrypt(Nonce,Plaintext,None)
  except Exception as Ex:
    Message="Encryption failed"+(": "+str(Ex) if len(str(Ex))!=0 else "")
    return False,Message,None

  #Return encrypted data
  return True,"",Salt+Nonce+Ciphertext

#----------------------------------------------------------------------------------------------------------------------
# Decryption routine
#----------------------------------------------------------------------------------------------------------------------
def DecryptData(InputFile,Password):

  #Get salt length from password
  SaltLength=_GetSaltLength(Password)

  #Read the salt, nonce, and ciphertext from the input file
  try:
    File=open(InputFile,'rb')
    Salt=File.read(SaltLength)
    Nonce=File.read(_NONCE_LENGTH)
    Ciphertext=File.read()
    File.close()
  except Exception as Ex:
    Message=f"Unable to read file {InputFile}: {str(Ex)}"
    return False,Message,None

  #Derive the key from the password
  Kdf=PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=_KEY_LENGTH,
    salt=Salt,
    iterations=_KEY_ITERATIONS,
    backend=default_backend()
  )
  Key=Kdf.derive(Password.encode())

  #Decrypt the ciphertext
  try:
    AesGcm=AESGCM(Key)
    ClearData=AesGcm.decrypt(Nonce,Ciphertext,None)
  except Exception as Ex:
    Message="Decryption failed"+(": "+str(Ex) if len(str(Ex))!=0 else "")
    return False,Message,None

  #Return decrypted data
  return True,"",ClearData

#----------------------------------------------------------------------------------------------------------------------
# File encryption routine
#----------------------------------------------------------------------------------------------------------------------
def EncryptFile(InputFile,OutputFile,Password):
  
  #Encrypt data
  Status,Message,CipherData=EncryptData(InputFile,Password)
  if Status==False:
    return False,Message

  #Write file
  try:
    File=open(OutputFile,'wb')
    File.write(CipherData)
    File.close()
  except Exception as Ex:
    Message=f"Unable to save file {OutputFile}: {str(Ex)}"
    return False,Message

  #Return success
  return True,""

#----------------------------------------------------------------------------------------------------------------------
# File decryption routine
#----------------------------------------------------------------------------------------------------------------------
def DecryptFile(InputFile,OutputFile,Password):

  #Decrypt data
  Status,Message,ClearData=DecryptData(InputFile,Password)
  if Status==False:
    return False,Message

  #Write the unencripted data to the output file
  try:
    File=open(OutputFile,'wb')
    File.write(ClearData)
    File.close()
  except Exception as Ex:
    Message=f"Unable to save file {OutputFile}: {str(Ex)}"
    return False,Message
  
  #Return success
  return True,""