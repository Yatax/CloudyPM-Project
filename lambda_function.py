import json
import urllib.request

def lambda_handler(event, context):
    try:
        # 1. รับข้อมูล JSON จาก LINE Webhook
        body = json.loads(event['body'])
        if not body.get('events'):
            return {'statusCode': 200, 'body': 'no events'}
            
        line_event = body['events'][0]
        reply_token = line_event['replyToken']
        
        # 2. ตรวจสอบว่า User ส่ง "พิกัด (Location)" มาหรือไม่
        if line_event['message']['type'] == 'location':
            lat = line_event['message']['latitude']
            lon = line_event['message']['longitude']
            address = line_event['message']['address']
            
            # 3. เชื่อมต่อ API ดึงค่าฝุ่น PM 2.5 จริงจาก Open-Meteo
            api_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                pm_value = data['current']['pm2_5']
            
            # 4. ส่งต่อให้ฟังก์ชันที่คนที่ 2 จะมาเขียน (process_and_reply)
            return process_and_reply(reply_token, pm_value, address)

        # 5. ตรวจสอบว่า User กดปุ่ม "เช็กฝุ่น" จาก Rich Menu หรือไม่
        elif line_event['message']['type'] == 'text':
            user_text = line_event['message']['text']
            if "เช็กฝุ่น" in user_text:
                instruction = [{"type": "text", "text": "📍 กรุณาส่งตำแหน่งที่ตั้ง (Location) มาให้หนูหน่อยนะคะ"}]
                send_reply(reply_token, instruction)
                
    except Exception as e:
        print(f"Error occurred: {e}")
    return {'statusCode': 200, 'body': 'ok'}