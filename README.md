# Trợ lý Tuyển sinh Đại học Thông minh (VJU Admissions Chatbot)

Dự án cá nhân xây dựng chatbot tư vấn tuyển sinh cho Trường Đại học Việt Nhật (VJU) – ĐHQGHN, ứng dụng kiến trúc RAG (Retrieval-Augmented Generation) kết hợp Google Gemini API để trả lời tự động các câu hỏi về tuyển sinh năm 2026.

---

## Ý tưởng dự án

Là sinh viên đang theo học tại Trường Đại học Việt Nhật và từng làm cộng tác viên tuyển sinh cho trường. Trong quá trình làm việc, mình nhận thấy mỗi mùa tuyển sinh có rất nhiều thí sinh và phụ huynh hỏi đi hỏi lại những câu giống nhau: học phí bao nhiêu, ngành nào đang tuyển, xét tuyển bằng phương thức gì, lịch phỏng vấn khi nào,... Trả lời thủ công từng người rất mất thời gian.

Từ đó mình nảy ra ý tưởng xây dựng một chatbot AI có thể:
- **Trả lời tự động** dựa trên tài liệu tuyển sinh chính thức của trường (không bịa thông tin).
- **Nhớ ngữ cảnh** cuộc hội thoại để trả lời mạch lạc hơn.
- **Thu thập thông tin thí sinh** giúp bộ phận tuyển sinh quản lý và chủ động liên hệ tư vấn.

---

## Công nghệ sử dụng

Python, FastAPI, Streamlit, ChromaDB, LangChain, Gemini API.

---

## Cấu trúc thư mục

```
TuyenSinhChatbot/
├── data/
│   ├── faq.json              # Câu hỏi thường gặp
│   └── majors_info.md        # Thông tin tuyển sinh 2026
├── chroma_db/                # Vector database (tự sinh khi chạy ingest)
├── src/
│   ├── __init__.py
│   ├── config.py             # Cấu hình biến môi trường
│   ├── database.py           # Kết nối SQLAlchemy & Redis
│   ├── ingest.py             # Nạp dữ liệu vào ChromaDB
│   ├── rag_engine.py         # Core RAG engine
│   └── main.py               # FastAPI server
├── index.html                # Giao diện frontend (SPA)
├── requirements.txt
├── .env                      # Biến môi trường (API key, DB URL,...)
└── README.md
```

---

## Hướng dẫn cài đặt và chạy

### 1. Cài thư viện

Cần Python 3.9 trở lên.

```bash
pip install -r requirements.txt
```

### 2. Cấu hình file `.env`

```ini
GEMINI_API_KEY=your_google_gemini_api_key
DATABASE_URL=sqlite:///./admissions_chatbot.db
REDIS_URL=
CHROMA_DB_DIR=./chroma_db
```

- `GEMINI_API_KEY`: Lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/apikey).
- `REDIS_URL`: Để trống nếu không có Redis, hệ thống tự dùng bộ nhớ tạm thay thế.

### 3. Nạp dữ liệu vào ChromaDB

```bash
python src/ingest.py
```

Script này đọc file `data/majors_info.md` và `data/faq.json`, chia nhỏ (chunking), tạo embedding rồi lưu vào ChromaDB.

### 4. Chạy API server

```bash
python src/main.py
```

hoặc:

```bash
uvicorn src.main:app --reload
```

Server chạy tại `http://127.0.0.1:8000`. Mở `index.html` trong trình duyệt để sử dụng giao diện chat.

---

## Các chức năng chính

### Phía thí sinh

- **Đăng ký / Đăng nhập** bằng số điện thoại 10 chữ số + xác thực OTP 6 số.
- **Chat với AI** – giao diện chat có typing animation, gợi ý câu hỏi nhanh (Quick Questions), gợi ý câu hỏi tiếp theo (Suggested Questions) sau mỗi lượt trả lời.
- **Validation real-time** – SĐT chỉ nhập số, họ tên chỉ nhập chữ, kiểm tra ngay khi gõ.
- **Multi-model fallback** – nếu model AI chính bị lỗi hoặc quá tải, hệ thống tự chuyển sang model khác (hỗ trợ 6 model Gemini).
- **Auto retry** khi gặp rate-limit (429) hoặc server error (503).

### Phía Admin (Quản trị viên)

Ý tưởng: Admin là nhân viên tư vấn tuyển sinh. Sau khi thí sinh đăng ký và chat với bot, Admin vào hệ thống để xem thí sinh hỏi gì, quan tâm điều gì, từ đó chủ động gọi điện tư vấn. Nói đơn giản thì Admin Panel giống một công cụ CRM thu nhỏ cho phòng tuyển sinh.

Các chức năng Admin bao gồm:

| Chức năng | Mô tả | Mục đích |
|-----------|-------|----------|
| Dashboard thống kê | Tổng thí sinh, số đã chat, số đăng ký hôm nay | Nắm tình hình nhanh mỗi ngày |
| Tìm kiếm thí sinh | Lọc real-time theo tên hoặc SĐT | Tìm nhanh khi nhận cuộc gọi/email |
| Xem chi tiết thí sinh | Họ tên, SĐT, ngày sinh, tổ hợp, ngành, ngày ĐK (chỉ đọc) | Biết profile để tư vấn đúng |
| Phân tích chủ đề | Tự động quét chat → hiển thị tags: học phí, ngành, điểm chuẩn,... | Biết thí sinh lo lắng gì mà không cần đọc hết chat |
| Xem lịch sử chat | Toàn bộ hội thoại thí sinh ↔ chatbot, kèm thời gian | Xem bot trả lời đúng chưa, cải thiện dữ liệu |
| Ghi chú tư vấn | Admin ghi chú riêng cho từng thí sinh, lưu vĩnh viễn | Đội tư vấn phối hợp với nhau, biết ai đã liên hệ gì |
| Gọi tư vấn | Bấm nút gọi điện trực tiếp (tel: link) | Gọi luôn, không cần copy số |
| Xóa thí sinh | Xóa toàn bộ thông tin + chat, có confirm trước khi xóa | Dọn dữ liệu test hoặc spam |

---

## Luồng xử lý dữ liệu

### Nạp dữ liệu (chạy 1 lần)

```
Tài liệu tuyển sinh (MD, JSON)
    → Chunking (LangChain, ~500-1000 ký tự/đoạn)
    → Sinh embedding (Gemini Embedding API)
    → Lưu vào ChromaDB
```

### Xử lý câu hỏi (mỗi lần chat)

```
Thí sinh gửi câu hỏi
    → Embedding câu hỏi
    → Semantic Search trong ChromaDB (tìm đoạn tài liệu liên quan)
    → Ghép: system prompt + tài liệu tìm được + 3 lượt chat gần nhất (Redis)
    → Gọi Gemini API sinh câu trả lời
    → Parse JSON response → hiển thị answer + suggested questions
    → Lưu vào SQL DB + Redis
```

---

## Thiết kế cơ sở dữ liệu

### SQL – Bảng `chat_logs`

| Cột | Kiểu | Ghi chú |
|-----|------|---------|
| id | INTEGER (PK) | Tự tăng |
| session_id | VARCHAR(100) | Có index, dùng để truy vấn theo phiên |
| user_query | TEXT | Câu hỏi |
| bot_response | TEXT | Câu trả lời |
| timestamp | DATETIME | Thời điểm |

Dùng SQLAlchemy ORM nên chuyển đổi giữa SQLite, MySQL, PostgreSQL không cần sửa code.

### Redis – Session cache

- Key: `chat_history:{session_id}`
- Value: JSON array, 6 message gần nhất (3 lượt hỏi-đáp)
- TTL: 24 giờ
- Nếu không có Redis → tự dùng In-memory, không crash

### ChromaDB – Vector store

Lưu embedding vectors của tài liệu tuyển sinh, truy vấn bằng Semantic Search. Chạy local, không cần setup server.

### LocalStorage (Frontend)

| Key | Nội dung |
|-----|----------|
| `vju_users` | Danh sách thí sinh đã đăng ký |
| `vju_chats_{phone}` | Lịch sử chat theo SĐT |
| `vju_gemini_key` | API Key người dùng nhập |

---

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/health` | Kiểm tra server có đang chạy không |
| POST | `/chat` | Gửi câu hỏi, nhận câu trả lời từ RAG engine |
| GET | `/history/{session_id}` | Lấy lịch sử chat của một phiên |

Có bật CORS cho phép frontend gọi từ mọi domain.

---

## Tài khoản test

### Admin

| | |
|---|---|
| **Tên đăng nhập** | `adminvju` |
| **Mật khẩu** | `adminvju2026` |

Cách truy cập: Mở `index.html` → Đăng nhập → Nhấn "Đăng nhập Admin" → Nhập tài khoản trên.

### Thí sinh (tạo mới để test)

1. Nhấn **Đăng ký** → Điền SĐT 10 số, họ tên, ngày sinh, tổ hợp môn.
2. Nhấn **Đồng ý** ở modal xác nhận dữ liệu.
3. Nhập mã OTP 6 số hiển thị ở góc trên phải modal (chế độ demo).
4. Sau khi đăng nhập, nhập Gemini API Key ở sidebar trái để bắt đầu chat.

---

## Triển khai production (Free Tier)

| Thành phần | Dịch vụ | Ghi chú |
|------------|---------|---------|
| Vector DB | Chạy local `chroma_db/` | Deploy kèm source code |
| Redis | [Upstash](https://upstash.com/) | Đăng ký free, lấy Connection URL → `REDIS_URL` |
| SQL DB | [Supabase](https://supabase.com/) | PostgreSQL free → `DATABASE_URL` |
| Backend | [Render](https://render.com/) | Liên kết GitHub repo, cấu hình ENV trên dashboard |

---

## Một số điểm kỹ thuật đáng chú ý

- **Fault tolerance**: Hệ thống tự chuyển model khi Gemini API lỗi (6 model fallback), tự retry khi rate-limit, tự chuyển In-memory khi Redis chết.
- **Bảo mật**: OTP 6 số, validate input real-time, modal đồng ý thu thập dữ liệu (GDPR-like), phân quyền Admin/User rõ ràng.
- **Prompt Engineering**: System prompt thiết kế cho vai trò chuyên gia tư vấn tuyển sinh, output dạng JSON có `answer` + `suggested_questions`, xử lý parse JSON nhiều tầng fallback.
- **UX**: Responsive trên mobile, có micro-animation (typing dots, fade-in), quick replies, suggested questions.
