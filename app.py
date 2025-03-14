from flask import Flask, request, jsonify
import json
import asyncio
from datetime import datetime
import httpx

app = Flask(__name__)

# بيانات Cloudinary (استبدل هذه القيم بمعلومات حسابك)
CLOUDINARY_CLOUD_NAME = "duu2fy7bq"
CLOUDINARY_API_KEY = "459654532934462"
CLOUDINARY_API_SECRET = "WMWrndmiqcot_20p0rc50odjPTw"

# تنزيل الملف من Cloudinary (غير متزامن)
async def download_file_from_cloudinary():
    url = "https://res.cloudinary.com/duu2fy7bq/raw/upload/v1741983005/keys/ky.txt"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            file_content = response.text
            print("Downloaded File Content:", file_content)
            return json.loads(file_content)
        else:
            raise Exception(f"Failed to download file from Cloudinary. Status Code: {response.status_code}")

# تحديث الملف في Cloudinary باستخدام API REST (غير متزامن)
async def update_file_in_cloudinary(keys):
    upload_url = f"https://api.cloudinary.com/v1_1/{CLOUDINARY_CLOUD_NAME}/raw/upload"
    auth = (CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)
    headers = {"Content-Type": "application/json"}
    data = {
        "public_id": "keys/ky.txt",
        "overwrite": True,
        "resource_type": "raw",
        "file": json.dumps(keys),
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(upload_url, auth=auth, headers=headers, json=data)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code != 200:
            raise Exception(f"Failed to update file in Cloudinary: {response.text}")

# التحقق من صلاحية الأكواد (غير متزامن)
async def is_valid_key(key):
    try:
        keys = await download_file_from_cloudinary()

        key_data = keys.get(key)
        print(f"Checking key: {key}")
        print(f"Key Data: {key_data}")

        if not key_data:
            print("Key not found in the file.")
            return False

        expiry_time = datetime.strptime(key_data["expiry"], "%Y-%m-%d %H:%M:%S")
        print(f"Expiry Time: {expiry_time}, Current Time: {datetime.now()}")

        if datetime.now() > expiry_time:
            print("Key has expired.")
            del keys[key]
            await update_file_in_cloudinary(keys)
            return False

        if len(key_data["used_by"]) >= key_data["limit"]:
            print("Key usage limit reached.")
            return False

        # تحديث قائمة المستخدمين الذين استخدموا المفتاح
        key_data["used_by"].append("anonymous")  # إضافة مستخدم مجهول
        keys[key] = key_data
        await update_file_in_cloudinary(keys)

        print("Key is valid.")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

# نقطة النهاية للتحقق من المفتاح (غير متزامن)
@app.route('/cod', methods=['GET'])
async def check_code():
    code = request.args.get('code')

    if not code:
        return jsonify({"valid": False, "message": "يرجى تقديم الكود."}), 400

    valid = await is_valid_key(code)
    return jsonify({"valid": valid})

# تشغيل التطبيق
if __name__ == "__main__":
    app.run(debug=True)
