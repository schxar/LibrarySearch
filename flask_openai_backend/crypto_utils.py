from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
import base64

class SimpleAES:
    @staticmethod
    def encrypt(data: str, key: str) -> str:
        """AES加密"""
        key = bytes.fromhex(key)  # 将16进制密钥转换为字节
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode('utf-8')
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return f"{iv}:{ct}"

    @staticmethod
    def decrypt(encrypted_data: str, key: str) -> str:
        """AES解密"""
        key = bytes.fromhex(key)  # 将16进制密钥转换为字节
        iv, ct = encrypted_data.split(':')
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')

class RSAKeyExchange:
    def __init__(self):
        self.key_pair = RSA.generate(2048)
        self.public_key = self.key_pair.publickey()
    
    def encrypt_aes_key(self, aes_key: str) -> str:
        """使用RSA公钥加密AES密钥"""
        cipher = PKCS1_OAEP.new(self.public_key)
        encrypted_key = cipher.encrypt(bytes.fromhex(aes_key))
        return base64.b64encode(encrypted_key).decode('utf-8')
    
    def decrypt_aes_key(self, encrypted_aes_key: str) -> str:
        """使用RSA私钥解密AES密钥"""
        cipher = PKCS1_OAEP.new(self.key_pair)
        decrypted_key = cipher.decrypt(base64.b64decode(encrypted_aes_key))
        return decrypted_key.hex()
