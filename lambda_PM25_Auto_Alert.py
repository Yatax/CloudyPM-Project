import json
import urllib.request
import boto3

# เชื่อมต่อ DynamoDB
dynamodb = boto3.resource('dynamodb')
sub_table = dynamodb.Table('User_Subscriptions')

def lambda_handler(event, context):
    # 1. ดึงรายชื่อคนที่มี "จุดประจำ" ทั้งหมดออกมา
    response = sub_table.scan()
    users = response.get('Items', [])
    
    token = "3a4dcec3b23620f3249f5ead9282334ab304a91b" # AQICN Token
    line_access_token = 'nv75LkdCyHm1jQ+wU5e4RTvqwjVjlGWdu3gK9DsCW15N/w0P6kNqXgKHezzm1YhZp/qWq5SrZTABskqRCH/GBfUMbdN0lDgD58GAWacrOBFBefYDmL00UXsqdV+KW2onw2exf4+vDENhxRfBJwEZpQdB04t89/1O/w1cDnyilFU='

    for user in users:
        user_id = user['userId']
        lat = user['fav_lat']
        lon = user['fav_lon']
        loc_name = user['location_name']
        
        # 2. แอบไปถามค่าฝุ่นที่จุดนั้นจาก API
        api_url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={token}"
        try:
            with urllib.request.urlopen(api_url) as res:
                data = json.loads(res.read().decode())
                if data['status'] == 'ok':
                    pm_value = data['data']['iaqi'].get('pm25', {}).get('v', 0)
                    
                    # 3. เงื่อนไข: ถ้าฝุ่นสูงเกิน 37.5 (เริ่มอันตราย) ให้ทักไปเตือน
                    # (ตอนทดสอบอาจลองปรับเลขให้ต่ำลงเพื่อให้บอททักทันทีได้ค่ะ)
                    if pm_value > 37.5: 
                        send_push_notification(user_id, loc_name, pm_value, line_access_token)
        except Exception as e:
            print(f"Error checking for user {user_id}: {e}")
                    
    return {'statusCode': 200, 'body': 'Monitoring Complete'}

def send_push_notification(user_id, location, pm_value, access_token):
    url = 'https://api.line.me/v2/bot/message/push' # ใช้ /push สำหรับส่งเอง
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    msg_text = f"📢  Cloudy แจ้งเตือนค่ะ!\nตอนนี้ค่าฝุ่นแถว '{location}'\nสูงถึง {pm_value} µg/m³ แล้วนะคะ\n😷 อย่าลืมสวมหน้ากาก N95 ด้วยนะคะ เป็นห่วงค่ะ!"
    
    data = json.dumps({
        'to': user_id,
        'messages': [{'type': 'text', 'text': msg_text}]
    }, ensure_ascii=False).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        urllib.request.urlopen(req)
        print(f"Push message sent to {user_id}")
    except Exception as e:
        print(f"Push Error: {e}")