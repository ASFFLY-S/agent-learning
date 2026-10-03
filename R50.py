import os
import requests
from dotenv import load_dotenv
load_dotenv()
key=os.environ.get("DEEPSEEK_API_KEY")
if not key:
    print("Please set DEEPSEEK_API_KEY environment variable")
else:
    print("读到密钥：",key[:6]+"..."+key[-4:])
