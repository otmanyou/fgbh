from flask import Flask, request, jsonify
from datetime import datetime
import requests
import json

app = Flask(__name__)

# دالة لجلب الملف من الرابط
def fetch_keys():
    try:
        response = requests.get('https://res.cloudinary.com/duu2fy7bq/raw/upload/v1741983005/keys/ky.txt')
        response.raise_for_status()  # التحقق من وجود أخطاء في الطلب
        return json.loads(response.text)
    except Exception as e:
        return {}

# دالة للتحقق من صلاحية الكود
def is_key_valid(key_data):
    expiry_str = key_data.get('expiry')
    if not expiry_str:
        return False

    expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
    current_date = datetime.now()

    return current_date < expiry_date

@app.route('/check', methods=['GET'])
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"error": "يرجى تقديم المفتاح."}), 400

    keys_data = fetch_keys()
    key_data = keys_data.get(key)

    if not key_data:
        return jsonify({"result": "خطأ"})  # المفتاح غير موجود

    if is_key_valid(key_data):
        return jsonify({"result": "صحيح"})  # المفتاح صالح
    else:
        return jsonify({"result": "خطأ"})  # المفتاح منتهي الصلاحية

if __name__ == '__main__':
    app.run(debug=True)
