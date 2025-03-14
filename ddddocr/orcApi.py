# example.py
from flask import Flask, request, jsonify
import ddddocr
import hashlib
import os
from functools import wraps

app = Flask(__name__)

# 从环境变量获取配置
SECRET_TOKEN = os.getenv('SECRET_TOKEN', 'your_secret_token_here')
PORT = int(os.getenv('PORT', 5000))

def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        # 移除 "Bearer " 前缀（如果存在）
        token = token.replace('Bearer ', '')
        
        # 计算 token 的 SHA256 哈希值
        hashed_token = hashlib.sha256(token.encode()).hexdigest()
        expected_hash = hashlib.sha256(SECRET_TOKEN.encode()).hexdigest()
        
        if hashed_token != expected_hash:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function

# 初始化 OCR
ocr = ddddocr.DdddOcr()

@app.route('/ocr', methods=['POST'])
@verify_token
def ocr_api():
    try:
        # 检查是否有文件上传
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
            
        image_file = request.files['image']
        image_data = image_file.read()
        
        # 进行 OCR 识别
        result = ocr.classification(image_data)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)