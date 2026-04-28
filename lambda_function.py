import json
import urllib.request

# --- ฟังก์ชันหลักที่ AWS Lambda จะเรียกใช้ ---
def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        if not body.get('events'):
            return {'statusCode': 200, 'body': 'no events'}
            
        line_event = body['events'][0]
        reply_token = line_event.get('replyToken')
        message = line_event.get('message', {})
        msg_type = message.get('type')

        # 1. กรณีรับค่าตำแหน่งพิกัด (Location)
        if msg_type == 'location':
            lat = message['latitude']
            lon = message['longitude']
            address = message.get('address', 'ตำแหน่งของคุณ')
            
            # --- เปลี่ยนมาใช้ AQICN API ตรงนี้ค่ะ ---
            token = "3a4dcec3b23620f3249f5ead9282334ab304a91b"
            api_url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"

            with urllib.request.urlopen(api_url) as response:
                data = json.loads(response.read().decode())
                if data['status'] == 'ok':
                    # ดึงค่า PM 2.5 (ถ้าไม่มีข้อมูลให้เป็น 0)
                    pm_value = data['data']['iaqi'].get('pm25', {}).get('v', 0)
                    # ดึงชื่อสถานีตรวจวัดมาต่อท้ายที่อยู่เพื่อความแม่นยำ
                    station = data['data']['city']['name']
                    address = f"{address} (สถานี: {station})"
                else:
                    pm_value = 0
            # -----------------------------------
            
            return process_and_reply(reply_token, pm_value, address)

        # 2. กรณีรับข้อความ "เช็กฝุ่น"
        elif msg_type == 'text':
            user_text = message.get('text', '')
            if "เช็กค่าฝุ่น" in user_text or "เช็คค่าฝุ่น" in user_text:
                instruction = [{"type": "text", "text": "📍 กรุณาส่งตำแหน่งที่ตั้ง (Location) มาให้หนูหน่อยนะคะ โดยกดปุ่ม + แล้วเลือก 'ตำแหน่งที่ตั้ง' ค่ะ"}]
                return send_reply(reply_token, instruction)
            # --- ปุ่มวิธีป้องกันตัว (ที่เพิ่มใหม่) ---
            elif "วิธีป้องกันตัว" in user_text:
                tips = [
                    {
                        "type": "text", 
                        "text": "😷 วิธีป้องกันตัวจาก PM 2.5:\n\n1. สวมหน้ากาก N95 เมื่อออกกลางแจ้ง\n2. หลีกเลี่ยงกิจกรรมออกกำลังกายกลางแจ้ง\n3. ปิดประตูหน้าต่างให้มิดชิด\n4. ใช้เครื่องฟอกอากาศที่มีแผ่นกรอง HEPA\n5. ดื่มน้ำสะอาดบ่อยๆ เพื่อช่วยขับสารพิษ"
                    }
                ]
                return send_reply(reply_token, tips)
                
    except Exception as e:
        print(f"Error occurred: {e}")
    return {'statusCode': 200, 'body': 'ok'}

def process_and_reply(reply_token, pm_value, address):
    # เลือกรูปภาพและสถานะตามเกณฑ์ AQI/PM2.5
    if pm_value <= 15:
        status_text = "EXCELLENT 😊"
        image_url = "https://raw.githubusercontent.com/Yatax/CloudyPM-Project/main/assets/good.png"
    elif pm_value <= 37.5:
        status_text = "MODERATE 😐"
        image_url = "https://raw.githubusercontent.com/Yatax/CloudyPM-Project/main/assets/moderate.png"
    elif pm_value <= 75:
        status_text = "UNHEALTHY 😷"
        image_url = "https://raw.githubusercontent.com/Yatax/CloudyPM-Project/main/assets/unhealthy.png"
    else:
        status_text = "HAZARDOUS 🚨"
        image_url = "https://raw.githubusercontent.com/Yatax/CloudyPM-Project/main/assets/hazardous.png"

    flex_contents = {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectMode": "cover",
            "aspectRatio": "1:1",
            "gravity": "center"
          },
          {
            "type": "box",
            "layout": "vertical",
            "contents": [],
            "position": "absolute",
            "background": {
              "type": "linearGradient",
              "angle": "0deg",
              "endColor": "#00000000",
              "startColor": "#00000099"
            },
            "width": "100%",
            "height": "40%",
            "offsetBottom": "0px",
            "offsetStart": "0px",
            "offsetEnd": "0px"
          },
          {
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "text",
                        "text": status_text,
                        "size": "xl",
                        "color": "#ffffff",
                        "weight": "bold"
                      }
                    ]
                  },
                  {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                      {
                        "type": "text",
                        "text": f"{pm_value} µg/m³",
                        "color": "#ffffff",
                        "size": "md"
                      }
                    ],
                    "spacing": "xs"
                  },
                  {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                      {
                        "type": "box",
                        "layout": "baseline",
                        "contents": [
                          {
                            "type": "text",
                            "text": f"📍 {address}",
                            "color": "#ffffff",
                            "size": "sm",
                            "flex": 0,
                            "wrap": True
                          }
                        ],
                        "flex": 0,
                        "spacing": "lg"
                      }
                    ]
                  }
                ],
                "spacing": "xs"
              }
            ],
            "position": "absolute",
            "offsetBottom": "0px",
            "offsetStart": "0px",
            "offsetEnd": "0px",
            "paddingAll": "20px"
          }
        ],
        "paddingAll": "0px"
      }
    }

    messages = [{"type": "flex", "altText": f"ระดับฝุ่น: {status_text}", "contents": flex_contents}]
    return send_reply(reply_token, messages)

def send_reply(reply_token, messages):
    access_token = 'nv75LkdCyHm1jQ+wU5e4RTvqwjVjlGWdu3gK9DsCW15N/w0P6kNqXgKHezzm1YhZp/qWq5SrZTABskqRCH/GBfUMbdN0lDgD58GAWacrOBFBefYDmL00UXsqdV+KW2onw2exf4+vDENhxRfBJwEZpQdB04t89/1O/w1cDnyilFU='
    url = 'https://api.line.me/v2/bot/message/reply'
    
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': f'Bearer {access_token}'
    }
    
    data = {
        'replyToken': reply_token,
        'messages': messages
    }
    
    # ป้องกัน Error ภาษาไทยด้วย ensure_ascii=False และการ encode
    json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(url, data=json_data, headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            return {'statusCode': 200, 'body': 'ok'}
    except Exception as e:
        print(f"Send Reply Error: {e}")
        return {'statusCode': 500, 'body': str(e)}