from flask import Flask, request, jsonify
from datetime import datetime
import cloudinary
import cloudinary.api
import json

app = Flask(__name__)

# إعداد Cloudinary
cloudinary.config(
    cloud_name="duu2fy7bq",
    api_key="459654532934462",
    api_secret="WMWrndmiqcot_20p0rc50odjPTw"
)

# دالة لجلب الملف من Cloudinary باستخدام public_id
def fetch_keys():
    try:
        # جلب الملف باستخدام public_id
        resource = cloudinary.api.resource("keys/ky.txt", resource_type="raw")
        file_url = resource["secure_url"]  # الرابط الآمن للملف

        # تنزيل محتوى الملف
        response = requests.get(file_url)
        response.raise_for_status()  # التحقق من وجود أخطاء في الطلب
        return json.loads(response.text)
    except Exception as e:
        print(f"Error fetching keys: {str(e)}")
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
