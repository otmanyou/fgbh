from flask import Flask, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# رابط الملف على Cloudinary
CLOUDINARY_FILE_URL = "https://res.cloudinary.com/duu2fy7bq/raw/upload/v1741983005/keys/ky.txt"

# دالة لتحميل الملف من Cloudinary
def load_keys():
    try:
        response = requests.get(CLOUDINARY_FILE_URL)
        response.raise_for_status()  # التحقق من وجود أخطاء في الطلب
        return response.json()  # تحويل النص إلى JSON
    except Exception as e:
        print(f"Error loading file from Cloudinary: {e}")
        return {}

# دالة للتحقق من صلاحية المفتاح
def is_key_valid(key):
    keys = load_keys()
    key_data = keys.get(key)

    if not key_data:
        return "خطأ"  # المفتاح غير موجود

    expiry_time = datetime.strptime(key_data["expiry"], "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()

    if current_time > expiry_time:
        return "خطأ"  # المفتاح منتهي الصلاحية

    return "صحيح"  # المفتاح صالح

# نقطة النهاية للتحقق من المفتاح
@app.route('/check', methods=['GET'])
def check_key():
    key = request.args.get('key')  # الحصول على المفتاح من الطلب

    if not key:
        return jsonify({"error": "يرجى تقديم المفتاح."}), 400

    result = is_key_valid(key)
    return jsonify({"result": result})

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
