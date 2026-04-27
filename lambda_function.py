import json
import urllib.request

# --- ฟังก์ชันหลักที่ AWS Lambda จะเรียกใช้ ---
def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        if not body.get('events'):
            return {'statusCode': 200, 'body': 'no events'}
            
        line_event = body['events'][0]
        reply_token = line_event['replyToken']
        
        # รับค่าตำแหน่งพิกัด
        if line_event['message']['type'] == 'location':
            lat = line_event['message']['latitude']
            lon = line_event['message']['longitude']
            address = line_event['message']['address']
            
            api_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=pm2_5"
            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                pm_value = data['current']['pm2_5']
            
            return process_and_reply(reply_token, pm_value, address)

        # รับค่าข้อความเช็กฝุ่น
        elif line_event['message']['type'] == 'text':
            user_text = line_event['message']['text']
            if "เช็กฝุ่น" in user_text:
                instruction = [{"type": "text", "text": "📍 กรุณาส่งตำแหน่งที่ตั้ง (Location) มาให้หนูหน่อยนะคะ"}]
                send_reply(reply_token, instruction)
                
    except Exception as e:
        print(f"Error occurred: {e}")
    return {'statusCode': 200, 'body': 'ok'}

# --- ส่วนของคนที่ 2: ต้องชิดซ้ายสุดแบบนี้ (ไม่เยื้อง) ---
def process_and_reply(reply_token, pm_value, address):
    # 1. กำหนดเกณฑ์สีและข้อความ
    if pm_value <= 15:
        status, color = "ดีมาก", "#00E4FF"
        advice = "อากาศบริสุทธิ์ เหมาะกับการทำกิจกรรมกลางแจ้ง"
    elif pm_value <= 37.5:
        status, color = "ดี", "#00FF00"
        advice = "ทำกิจกรรมกลางแจ้งได้ตามปกติ"
    elif pm_value <= 75:
        status, color = "เริ่มมีผลกระทบ", "#FF7E00"
        advice = "ควรสวมหน้ากากอนามัยเมื่อออกนอกอาคาร"
    else:
        status, color = "มีผลกระทบมาก", "#FF0000"
        advice = "งดกิจกรรมกลางแจ้งและสวมหน้ากาก N95"

    # 2. สร้าง Flex Message
    flex_contents = {
        "type": "bubble",
        "header": {
            "type": "box", "layout": "vertical",
            "contents": [{"type": "text", "text": "CloudyPM Report", "weight": "bold", "color": "#FFFFFF", "size": "sm"}],
            "backgroundColor": color
        },
        "body": {
            "type": "box", "layout": "vertical",
            "contents": [
                {"type": "text", "text": f"📍 {address}", "size": "xs", "wrap": True, "color": "#8C8C8C"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": f"{pm_value} µg/m³", "size": "xxl", "weight": "bold", "color": color, "margin": "md"},
                {"type": "text", "text": f"สถานะ: {status}", "weight": "bold", "size": "md"},
                {"type": "text", "text": advice, "size": "xs", "wrap": True, "margin": "md", "color": "#555555"}
            ]
        },
        "footer": {
            "type": "box", "layout": "vertical",
            "contents": [{"type": "text", "text": "อัปเดตข้อมูลแบบ Real-time", "size": "xxs", "align": "center", "color": "#AAAAAA"}]
        }
    }
    
    messages = [{"type": "flex", "altText": f"รายงานค่าฝุ่น: {status}", "contents": flex_contents}]
    return send_reply(reply_token, messages)

# --- ฟังก์ชันส่งข้อความกลับ: ต้องชิดซ้ายสุดเช่นกัน ---
def send_reply(reply_token, messages):
    access_token = 'ใส่_TOKEN_ของคุณตรงนี้'
    url = 'https://api.line.me/v2/bot/message/reply'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    data = {'replyToken': reply_token, 'messages': messages}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    with urllib.request.urlopen(req) as res:
        return {'statusCode': 200, 'body': 'ok'}