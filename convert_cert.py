# Convert CA Certificate to Base64 for Leapcell Deployment
# This script reads ca.pem and outputs a base64 encoded string

import base64
import os

def convert_cert_to_base64():
    """Convert ca.pem to base64 string for environment variable"""
    cert_path = "ca.pem"
    
    if not os.path.exists(cert_path):
        print(f"❌ Error: {cert_path} not found!")
        print(f"   Current directory: {os.getcwd()}")
        return None
    
    try:
        with open(cert_path, 'rb') as cert_file:
            cert_content = cert_file.read()
            base64_cert = base64.b64encode(cert_content).decode('utf-8')
            
            print("=" * 80)
            print("✅ Certificate converted successfully!")
            print("=" * 80)
            print("\nAdd this to your Leapcell environment variables:\n")
            print("Variable Name: SSL_CERT_BASE64")
            print("Value:")
            print("-" * 80)
            print(base64_cert)
            print("-" * 80)
            print("\nInstructions:")
            print("1. Copy the base64 string above")
            print("2. Go to Leapcell dashboard > Environment Variables")
            print("3. Add new variable: SSL_CERT_BASE64")
            print("4. Paste the base64 string as the value")
            print("5. Remove SSL_CERT_PATH from environment variables (or set it to empty)")
            print("6. Keep SSL_VERIFY=True")
            print("\n" + "=" * 80)
            
            # Also save to file for easy copying
            with open('ssl_cert_base64.txt', 'w') as f:
                f.write(base64_cert)
            print("\n💾 Base64 certificate also saved to: ssl_cert_base64.txt")
            
            return base64_cert
            
    except Exception as e:
        print(f"❌ Error converting certificate: {e}")
        return None

if __name__ == "__main__":
    convert_cert_to_base64()
