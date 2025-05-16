from flask import Flask, request, jsonify, render_template_string
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

# 初始化Flask应用
app = Flask(__name__)
rsa = RSAKeyExchange()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AES-RSA加密演示</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { margin-top: 30px; }
        textarea, input { width: 100%; margin: 10px 0; }
        button { padding: 10px 15px; background: #007bff; color: white; border: none; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AES-RSA加密演示</h1>
        
        <h2>1. 获取RSA公钥</h2>
        <button onclick="getPublicKey()">获取公钥</button>
        <div class="result" id="publicKeyResult"></div>
        
        <h2>2. 加密AES密钥</h2>
        <input type="text" id="aesKey" placeholder="输入AES密钥(16进制格式)">
        <button onclick="encryptAESKey()">加密AES密钥</button>
        <div class="result" id="encryptedKeyResult"></div>
        
        <h2>3. 加密数据</h2>
        <textarea id="plaintext" placeholder="输入要加密的文本"></textarea>
        <button onclick="encryptData()">加密数据</button>
        <div class="result" id="encryptedDataResult"></div>
        
        <h2>4. 解密数据</h2>
        <textarea id="encryptedData" placeholder="输入加密后的数据(iv:ct格式)"></textarea>
        <button onclick="decryptData()">解密数据</button>
        <div class="result" id="decryptedDataResult"></div>
    </div>

    <script>
        let publicKey = '';
        let encryptedAESKey = '';
        
        function getPublicKey() {
            fetch('/api/rsa/key')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('publicKeyResult').innerHTML = 
                        `<strong>公钥:</strong><br><textarea readonly>${data.public_key}</textarea>`;
                    publicKey = data.public_key;
                });
        }
        
        function encryptAESKey() {
            const aesKey = document.getElementById('aesKey').value;
            if (!aesKey) return alert('请输入AES密钥');
            
            fetch('/api/rsa/encrypt-key', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ aes_key: aesKey })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('encryptedKeyResult').innerHTML = 
                    `<strong>加密后的AES密钥:</strong><br><textarea readonly>${data.encrypted_key}</textarea>`;
                encryptedAESKey = data.encrypted_key;
            });
        }
        
        function encryptData() {
            const plaintext = document.getElementById('plaintext').value;
            if (!plaintext) return alert('请输入要加密的文本');
            if (!encryptedAESKey) return alert('请先加密AES密钥');
            
            console.log('正在加密数据...', {
                encryptedAESKey,
                plaintext
            });
            
            fetch('/api/aes/encrypt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    encrypted_aes_key: encryptedAESKey,
                    plaintext: plaintext 
                })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || '加密失败');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('加密成功:', data);
                document.getElementById('encryptedDataResult').innerHTML = 
                    `<strong>加密结果:</strong><br><textarea readonly>${data.encrypted_data}</textarea>`;
                document.getElementById('encryptedData').value = data.encrypted_data;
            })
            .catch(error => {
                console.error('加密错误:', error);
                alert('加密错误: ' + error.message);
                document.getElementById('encryptedDataResult').innerHTML = 
                    `<strong>错误:</strong> ${error.message}`;
            });
        }
        
        function decryptData() {
            const encryptedData = document.getElementById('encryptedData').value;
            if (!encryptedData) return alert('请输入加密后的数据');
            if (!encryptedAESKey) return alert('请先加密AES密钥');
            
            fetch('/api/aes/decrypt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    encrypted_aes_key: encryptedAESKey,
                    encrypted_data: encryptedData 
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('decryptedDataResult').innerHTML = 
                    `<strong>解密结果:</strong><br><textarea readonly>${data.decrypted_text}</textarea>`;
            });
        }
    </script>
</body>
</html>
"""

# API路由
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/rsa/key', methods=['GET'])
def get_public_key():
    """获取RSA公钥"""
    public_key_pem = rsa.key_pair.publickey().export_key().decode('utf-8')
    return jsonify({
        'public_key': public_key_pem,
        'message': 'RSA public key retrieved successfully'
    })

@app.route('/api/rsa/encrypt-key', methods=['POST'])
def encrypt_aes_key():
    """使用RSA公钥加密AES密钥"""
    data = request.get_json()
    if not data or 'aes_key' not in data:
        return jsonify({'error': 'Missing aes_key'}), 400
    
    encrypted_key = rsa.encrypt_aes_key(data['aes_key'])
    return jsonify({
        'encrypted_key': encrypted_key,
        'message': 'AES key encrypted successfully'
    })

@app.route('/api/aes/encrypt', methods=['POST'])
def encrypt_data():
    """使用AES加密数据"""
    data = request.get_json()
    if not data or 'encrypted_aes_key' not in data or 'plaintext' not in data:
        return jsonify({'error': '缺少必要字段'}), 400
    
    try:
        print("正在解密AES密钥...")
        aes_key = rsa.decrypt_aes_key(data['encrypted_aes_key'])
        print(f"解密后的AES密钥: {aes_key}")
        
        print("正在加密数据...")
        encrypted_data = SimpleAES.encrypt(data['plaintext'], aes_key)
        print(f"加密结果: {encrypted_data}")
        
        return jsonify({
            'encrypted_data': encrypted_data,
            'message': '数据加密成功'
        })
    except Exception as e:
        print(f"加密错误: {str(e)}")
        return jsonify({
            'error': f"加密失败: {str(e)}",
            'details': str(e)
        }), 500

@app.route('/api/aes/decrypt', methods=['POST'])
def decrypt_data():
    """使用AES解密数据"""
    data = request.get_json()
    if not data or 'encrypted_aes_key' not in data or 'encrypted_data' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # 解密AES密钥
        aes_key = rsa.decrypt_aes_key(data['encrypted_aes_key'])
        # 解密数据
        decrypted_text = SimpleAES.decrypt(data['encrypted_data'], aes_key)
        return jsonify({
            'decrypted_text': decrypted_text,
            'message': 'Data decrypted successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
