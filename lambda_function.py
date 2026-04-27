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

    def process_and_reply(reply_token, pm_value, address):
    # 1. กำหนดเกณฑ์สีและข้อความตามค่าฝุ่น (อ้างอิงมาตรฐานกรมอนามัย)
    if pm_value <= 15:
        status = "ดีมาก"
        color = "#00E4FF"  # สีฟ้า
        advice = "อากาศบริสุทธิ์ เหมาะกับการทำกิจกรรมกลางแจ้ง"
    elif pm_value <= 37.5:
        status = "ดี"
        color = "#00FF00"  # สีเขียว
        advice = "ทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm_value <= 75:
        status = "เริ่มมีผลกระทบ"
        color = "#FF7E00"  # สีส้ม
        advice = "ควรสวมหน้ากากอนามัยเมื่อออกนอกอาคาร"
    else:
        status = "มีผลกระทบมาก"
        color = "#FF0000"  # สีแดง
        advice = "งดกิจกรรมกลางแจ้งและสวมหน้ากาก N95"

    # 2. สร้างโครงสร้าง Flex Message (JSON) เพื่อส่งกลับ
    flex_contents = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "CloudyPM Report", "weight": "bold", "color": "#FFFFFF", "size": "sm"}
            ],
            "backgroundColor": color
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"📍 {address}", "size": "xs", "wrap": True, "color": "#8C8C8C"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": f"{pm_value} µg/m³", "size": "xxl", "weight": "bold", "color": color, "margin": "md"},
                {"type": "text", "text": f"สถานะ: {status}", "weight": "bold", "size": "md"},
                {"type": "text", "text": advice, "size": "xs", "wrap": True, "margin": "md", "color": "#555555"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "อัปเดตข้อมูลแบบ Real-time", "size": "xxs", "align": "center", "color": "#AAAAAA"}
            ]
        }
    }
    
    # ส่งข้อมูลที่ประกอบเสร็จแล้วไปที่ฟังก์ชัน send_reply
    messages = [{"type": "flex", "altText": f"รายงานค่าฝุ่น: {status}", "contents": flex_contents}]
    return send_reply(reply_token, messages)

def send_reply(reply_token, messages):
    # ส่วนนี้ใช้เชื่อมต่อกับ LINE API เพื่อส่งข้อความกลับ
  
    access_token = 'ใส่_CHANNEL_ACCESS_TOKEN_จริงตรงนี้'
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    data = {
        'replyToken': reply_token,
        'messages': messages
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as res:
        return {'statusCode': 200, 'body': 'ok'}