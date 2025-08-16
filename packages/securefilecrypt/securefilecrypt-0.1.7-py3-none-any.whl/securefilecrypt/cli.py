#Import libraries
import sys
from securefilecrypt import __version__,EncryptFile,DecryptFile

#----------------------------------------------------------------------------------------------------------------------
# Show help
#----------------------------------------------------------------------------------------------------------------------
def ShowHelp():
  print("Secure encryption / decryption tool - v"+__version__+" - Diego Marin 2025")
  print("")
  print("Usage: sfcrypt <input_file> <output_file> (--encrypt|--decrypt) (--pw:<password>|--ev:<envvar>)")
  print("")
  print("<input_filename>  : File read for encryption or decryption")
  print("<output_filename> : Encrypted / decrypted file to produce")
  print("--encrypt         : Encrypt mode")
  print("--decrypt         : Decrypt mode")
  print("--pw:<password>   : Password for encryption / decryption.")
  print("--ev:<envvar>     : Get password for encryption / decryption from an environment variable")
  print("")

#----------------------------------------------------------------------------------------------------------------------
# Get command line arguments
#----------------------------------------------------------------------------------------------------------------------
def GetCommandLineOptions(Options):

  #Default values for options
  InputFile=""
  OutputFile=""
  Encryption=0
  Decryption=0
  Password=""
  EnvVar=""

  #Get arguments
  InputFile=sys.argv[1]
  OutputFile=sys.argv[2]
  for i in range(3,len(sys.argv)):
    item=sys.argv[i]
    if item=="--encrypt":
      Encryption=1
    elif item=="--decrypt":
      Decryption=1
    elif item.startswith("--pw:"):
      Password=item.replace("--pw:","")
    elif item.startswith("--ev:"):
      EnvVar=item.replace("--ev:","")
    else:
      print("Invalid option: ",item)
      return False

  #Check encryption or decryption mode is given
  if Encryption+Decryption!=1:
    print("Must specify either --encrypt or --decrypt")
    return False
  
  #Check password is given
  if len(Password)==0 and len(EnvVar)==0:
    print("Must provide password")
    return False
  if len(Password)!=0 and len(EnvVar)!=0:
    print("Must not provide password and environment variable at the same time")
    return False

  #Calculate mode
  if Encryption==1:
    Mode="encrypt"
  else:
    Mode="decrypt"

  #Return arguments
  Options.append(InputFile)
  Options.append(OutputFile)
  Options.append(Mode)
  Options.append(Password)
  Options.append(EnvVar)

  #Return code
  return True

#----------------------------------------------------------------------------------------------------------------------
# Main
#----------------------------------------------------------------------------------------------------------------------
def main():

  #Not enough arguments given show help
  if len(sys.argv)<2:
    ShowHelp()
    sys.exit(0)
    
  #Init variables
  Options=[]
  
  #Get command line arguments
  if(GetCommandLineOptions(Options)):
    InputFile=Options[0]
    OutputFile=Options[1]
    Mode=Options[2]
    Password=Options[3]
    EnvVar=Options[4]
  else:
    sys.exit(1)
  
  #Get password from environment variable
  if len(EnvVar)!=0:
    if EnvVar in os.environ:
      Password=os.environ[EnvVar]
    else:
      print("Cannot get password from environment variable "+EnvVar)
      sys.exit(1)
  
  # Encrypt file
  if Mode=="encrypt":
    Status,Message=EncryptFile(InputFile,OutputFile,Password)
    if Status==False:
      print(Message)
      sys.exit(1)
    print(f"File {InputFile} was encrypted into {OutputFile}")
  
  # Decrypt file
  elif Mode=="decrypt":
    Status,Message=DecryptFile(InputFile,OutputFile,Password)
    if Status==False:
      print(Message)
      sys.exit(1)
    print(f"File {InputFile} was decrypted into {OutputFile}")
  
  #Return successfully
  sys.exit(0)

#Invoke main routine
if __name__ == "__main__":
  main()
