# CloudyPM-Project

## Team Members

| ชื่อ | รหัสนักศึกษา | บทบาท |
|------|-------------|--------|
| นางสาวภวริศา อำนาคะ | 6709616772 | Designer/FrontEnd |
| นายธีร์ตภัฏฐ์ มะกรูดอินทร์ | 6709616558 | Project Admin/Git Master |
| นางสาวญาตาวี พีระสมบัติ | 6709616467 | Backend & API Intergration |
| นายสิริพิชญ์ สมุทระประภูต | 6709616921 | Data Logic & Intergration |

---
 
## 🎯 ปัญหาที่แก้ (Pain Point)
 
นักศึกษาขาดข้อมูลฝุ่นแบบ **Hyper-local** — เดินผ่านจุดก่อสร้างทุกวันโดยไม่รู้ว่าฝุ่นเกินมาตรฐาน เพราะไม่มีข้อมูล PM2.5 เฉพาะจุด
 
---
 
## ✅ Features
 
| # | Feature |
|---|---------|
| 1 | เช็กค่าฝุ่นหน้าตึกได้ผ่าน LINE ใน 2 คลิก |
| 2 | Crowdsourced Alert — แจ้งเตือนเพื่อนนักศึกษาเมื่อเจอจุดฝุ่นหนาเกินมาตรฐาน |
| 3 | ทำนายค่าฝุ่นล่วงหน้าได้ |
 
---
 
## 🏗️ Architecture
 
```
User → LINE Bot → Amazon API Gateway → AWS Lambda
                                            ↑
                                         IAM Role
```
 
ระบบทำงานแบบ **Fully Serverless** บน AWS Cloud:
 
- **Amazon API Gateway** — รับ Webhook จาก LINE
- **AWS Lambda** — Backend Logic / ประมวลผลคำขอ
- **IAM Role** — จัดการสิทธิ์การเข้าถึง
---
 
## 🚀 Implementation Progress
 
### ✅ เสร็จแล้ว
 
- **Infrastructure** — Fully Serverless ด้วย Amazon API Gateway + AWS Lambda
- **API Integration** — เชื่อมต่อ AQICN (WAQI) API ดึงค่า PM2.5 จากสถานีตรวจวัดของกรมควบคุมมลพิษทั่วประเทศ
- **UI/UX** — Custom Flex Message เปลี่ยนรูปภาพพื้นหลัง + สีตามระดับความรุนแรง (Good / Moderate / Unhealthy / Hazardous)
- **Location-based Service** — รับพิกัดผู้ใช้เพื่อหาค่าฝุ่นเฉพาะจุด
- **Text-based Command** — ปุ่ม "เช็กฝุ่น" และ "วิธีป้องกันตัว" ผ่าน Rich Menu
### 🔜 Next Plan
 
- **DynamoDB** — เก็บประวัติการเช็กฝุ่น + ระบบสะสมแต้ม "Campus Hero" สำหรับนักศึกษาที่ช่วยรายงานค่าฝุ่น
- **Push Notification** — แจ้งเตือนอัตโนมัติเมื่อค่าฝุ่นในพิกัดที่สนใจถึงระดับอันตราย
---
 
## 💰 Cost Estimate
 
| รายการ | งบประหยัด (ผู้ใช้หลักร้อย) | งบจริงจัง (หลักพัน/หมื่น) |
|--------|---------------------------|--------------------------|
| AWS Lambda & Gateway | ~0–50 บาท | ~200 บาท |
| LINE Messaging API | 0 บาท (Free Plan) | 1,200 บาท (Basic Plan) |
| Data API Source | 0 บาท | 700 บาท |
| **รวมสุทธิ** | **~50 บาท** | **~2,100 บาท** |
 
---
 
## 🏛️ AWS Well-Architected Framework Analysis
 
<details>
<summary>1. Operational Excellence</summary>
**ข้อดี:** ใช้ AWS Lambda ไม่ต้องดูแล Server / แยก UI (Flex) กับ Logic ทำให้แก้ง่าย  
**ข้อเสีย:** Debug ยาก ไม่มีระบบ Log ชัดเจน  
**แผนปรับปรุง:** ใช้ CloudWatch Logs + ตั้ง Log Format ให้ชัด  
**Trade-off:** Debug ดีขึ้น แต่ Log เยอะ อ่านยากขึ้นนิด
 
</details>
<details>
<summary>2. Security</summary>
**ข้อดี:** ใช้ LINE Webhook + Secret / ไม่เก็บข้อมูลผู้ใช้ถาวร  
**ข้อเสีย:** Secret อาจ Hardcode ในโค้ด / ไม่มีการจำกัดสิทธิ์ IAM ละเอียด  
**แผนปรับปรุง:** เก็บ Secret ใน AWS Secrets Manager  
**Trade-off:** ปลอดภัยขึ้น แต่ Setup เพิ่ม
 
</details>
<details>
<summary>3. Reliability</summary>
**ข้อดี:** AWS Lambda Uptime สูง / โครงสร้างเรียบง่าย Error น้อย  
**ข้อเสีย:** พึ่ง API ภายนอก (AQICN) — ถ้า API ล่ม Bot ใช้ไม่ได้  
**แผนปรับปรุง:** ใส่ Fallback Message + Retry Logic  
**Trade-off:** Code ซับซ้อนขึ้นเล็กน้อย
 
</details>
<details>
<summary>4. Performance Efficiency</summary>
**ข้อดี:** Serverless เร็วและ Scale Auto / ใช้ Resource เฉพาะตอนมี Request  
**ข้อเสีย:** Cold Start ของ Lambda / โหลด JSON หลายไฟล์อาจช้า  
**แผนปรับปรุง:** Cache Template ใน Memory  
**Trade-off:** เร็วขึ้น แต่ใช้ RAM มากขึ้นนิด
 
</details>
<details>
<summary>5. Cost Optimization</summary>
**ข้อดี:** ใช้ Free Tier แทบไม่เสียเงิน / Lambda จ่ายตาม Usage  
**ข้อเสีย:** ถ้า User เยอะ Cost พุ่ง / API ภายนอกอาจมี Limit  
**แผนปรับปรุง:** จำกัด Request Rate / Cache ผลลัพธ์  
**Trade-off:** ลด Cost แต่ข้อมูลอาจไม่ Realtime 100%
 
</details>
<details>
<summary>6. Sustainability</summary>
**ข้อดี:** Serverless ใช้พลังงานเฉพาะตอนใช้งาน / ลด Resource Waste  
**ข้อเสีย:** เรียก API บ่อยเกิน → ใช้พลังงานเพิ่มโดยไม่จำเป็น  
**แผนปรับปรุง:** Cache ผลลัพธ์ช่วงสั้น  
**Trade-off:** ประหยัดพลังงาน แต่ข้อมูลอาจ Delay เล็กน้อย
 
</details>

---
 
## 🤖 Demo / Prototype
 
ทดลองใช้งาน Bot ได้เลยผ่าน LINE:
 
**LINE ID:** `@336dimyj`
 
> เพิ่มเพื่อนแล้วกด "เช็กฝุ่น" หรือส่งพิกัดมาได้เลย!
 
---
