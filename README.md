**Chatbot Tư Vấn Tuyển Sinh - Trường Đại Học Việt Nhật (VJU)**


**Mô tả dự án**

Trong quá trình tìm hiểu về tuyển sinh đại học, mình nhận thấy rằng các thí sinh thường gặp khá nhiều khó khăn khi muốn tìm kiếm thông tin về ngành học, học phí, điều kiện xét tuyển hay các chính sách học bổng. Thông tin thì nằm rải rác ở nhiều nguồn khác nhau, mà không phải lúc nào ban tuyển sinh cũng có thể trả lời kịp thời mọi câu hỏi của thí sinh, đặc biệt là vào mùa tuyển sinh khi lượng câu hỏi tăng đột biến.

Từ ý tưởng đó, mình đã xây dựng một chatbot tư vấn tuyển sinh dành cho Trường Đại học Việt Nhật (VJU) thuộc Đại học Quốc gia Hà Nội. Chatbot này hoạt động dựa trên kỹ thuật RAG (Retrieval-Augmented Generation), có nghĩa là thay vì để AI tự trả lời theo kiến thức chung, hệ thống sẽ tìm kiếm thông tin liên quan từ bộ dữ liệu tuyển sinh chính thức của trường, rồi dựa vào đó để sinh ra câu trả lời chính xác và sát với thực tế.

Mục tiêu chính của dự án là tạo ra một trợ lý ảo có thể hỗ trợ thí sinh 24/7, trả lời nhanh chóng các câu hỏi phổ biến về tuyển sinh như thông tin ngành đào tạo, học phí, phương thức xét tuyển, chính sách học bổng và các thông tin liên quan khác của VJU.


**Công nghệ sử dụng**

- **Python**: ngôn ngữ lập trình chính của toàn bộ dự án
- **FastAPI**: xây dựng API backend xử lý các yêu cầu chat từ phía người dùng
- **Streamlit**: xây dựng giao diện người dùng để thí sinh có thể tương tác trực tiếp với chatbot
- **ChromaDB**: cơ sở dữ liệu vector lưu trữ và tìm kiếm thông tin tuyển sinh theo ngữ nghĩa
- **LangChain**: framework kết nối các thành phần AI lại với nhau, từ việc chia nhỏ dữ liệu, tạo embedding, tìm kiếm tương tự cho đến gọi mô hình sinh câu trả lời
- **Gemini API**: sử dụng mô hình Gemini 1.5 Flash của Google để sinh câu trả lời và mô hình text-embedding-004 để tạo vector embedding cho dữ liệu tuyển sinh


**Cách hệ thống hoạt động**

Khi thí sinh gửi câu hỏi, hệ thống sẽ thực hiện các bước sau:

1. Câu hỏi của thí sinh được gửi lên API backend (FastAPI)
2. Hệ thống sử dụng ChromaDB để tìm kiếm các đoạn thông tin tuyển sinh có nội dung liên quan nhất với câu hỏi (similarity search)
3. Các đoạn thông tin tìm được sẽ được ghép cùng với lịch sử hội thoại gần nhất để tạo thành một prompt đầy đủ
4. Prompt này được gửi đến Gemini API để sinh ra câu trả lời tự nhiên, chính xác và dựa trên dữ liệu thực tế của trường
5. Câu trả lời được trả về cho thí sinh qua giao diện Streamlit, đồng thời cuộc hội thoại được lưu lại để phục vụ quản lý và phân tích


**Cấu trúc dự án**

TuyenSinhChatbot/
  data/
    majors_info.md          Thông tin chi tiết các ngành đào tạo của VJU
    faq.json                Các câu hỏi thường gặp về tuyển sinh
  src/
    config.py               Cấu hình biến môi trường và thông số hệ thống
    database.py             Xử lý lưu trữ dữ liệu và quản lý lịch sử hội thoại
    ingest.py               Nạp dữ liệu tuyển sinh vào ChromaDB
    main.py                 API backend chính (FastAPI)
    rag_engine.py           Logic xử lý RAG: tìm kiếm, tạo prompt, gọi Gemini API
  .env.example              Mẫu file cấu hình biến môi trường
  requirements.txt          Danh sách các thư viện cần cài đặt
  README.md


**Hướng dẫn khởi chạy dự án**

**Yêu cầu hệ thống**

- Python 3.10 trở lên
- Gemini API Key (lấy miễn phí tại Google AI Studio: https://aistudio.google.com/apikey)

**Bước 1**: Clone dự án

git clone https://github.com/minhducdevelop/VJU_ADMISSIONS_CHATBOT.git
cd VJU_ADMISSIONS_CHATBOT

**Bước 2**: Tạo môi trường ảo và cài đặt thư viện

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

Với macOS/Linux thì dùng:
source venv/bin/activate

**Bước 3**: Cấu hình biến môi trường

Tạo file .env từ file mẫu:
copy .env.example .env

Mở file .env và điền Gemini API Key của bạn vào:
GEMINI_API_KEY=api_key_cua_ban
DATABASE_URL=sqlite:///./admissions_chatbot.db
CHROMA_DB_DIR=./chroma_db

**Bước 4**: Nạp dữ liệu tuyển sinh vào ChromaDB

python -m src.ingest

Bước này sẽ đọc dữ liệu từ thư mục data/, chia nhỏ văn bản, tạo vector embedding và lưu vào ChromaDB.

**Bước 5**: Khởi chạy API backend

python -m src.main

API sẽ chạy tại địa chỉ: http://localhost:8000
Có thể xem tài liệu API tại: http://localhost:8000/docs

**Bước 6**: Khởi chạy giao diện Streamlit (nếu có)

streamlit run app.py

Giao diện sẽ mở tại địa chỉ: http://localhost:8501


**Một số điểm nổi bật**

- Hệ thống chỉ trả lời dựa trên dữ liệu tuyển sinh chính thức, không tự ý bịa đặt thông tin
- Hỗ trợ ghi nhớ lịch sử hội thoại trong phiên chat để hiểu ngữ cảnh câu hỏi tốt hơn
- Cấu trúc code rõ ràng, dễ mở rộng thêm dữ liệu hoặc tích hợp với các hệ thống khác
- API backend có thể kết nối với nhiều giao diện frontend khác nhau (web, mobile, tích hợp vào website trường)


**Các chức năng chính**

**Phía thí sinh**

- **Đăng ký và đăng nhập** bằng số điện thoại 10 chữ số, xác thực bằng mã OTP 6 số
- **Chat với AI**: giao diện chat có hiệu ứng typing animation, gợi ý câu hỏi nhanh (Quick Questions), gợi ý câu hỏi tiếp theo (Suggested Questions) sau mỗi lượt trả lời
- **Validation real-time**: số điện thoại chỉ cho nhập số, họ tên chỉ cho nhập chữ, kiểm tra ngay khi người dùng gõ
- **Multi-model fallback**: nếu model AI chính bị lỗi hoặc quá tải, hệ thống tự động chuyển sang model khác (hỗ trợ 6 model Gemini)
- **Auto retry** khi gặp lỗi rate-limit (429) hoặc server error (503)

**Phía Admin (Quản trị viên)**

Ý tưởng: Admin là nhân viên tư vấn tuyển sinh. Sau khi thí sinh đăng ký và chat với bot, Admin vào hệ thống để xem thí sinh hỏi gì, quan tâm điều gì, từ đó chủ động gọi điện tư vấn. Nói đơn giản thì Admin Panel giống một công cụ CRM thu nhỏ cho phòng tuyển sinh.

Các chức năng Admin bao gồm:

- **Dashboard thống kê**: hiển thị tổng thí sinh, số đã chat, số đăng ký hôm nay, giúp nắm tình hình nhanh mỗi ngày
- **Tìm kiếm thí sinh**: lọc real-time theo tên hoặc số điện thoại, tìm nhanh khi nhận cuộc gọi hoặc email
- **Xem chi tiết thí sinh**: họ tên, số điện thoại, ngày sinh, tổ hợp, ngành, ngày đăng ký (chỉ đọc), giúp biết profile để tư vấn đúng
- **Phân tích chủ đề**: tự động quét nội dung chat và hiển thị các tags như học phí, ngành, điểm chuẩn, giúp biết thí sinh lo lắng gì mà không cần đọc hết chat
- **Xem lịch sử chat**: toàn bộ hội thoại giữa thí sinh và chatbot kèm thời gian, giúp xem bot trả lời đúng chưa và cải thiện dữ liệu
- **Ghi chú tư vấn**: Admin ghi chú riêng cho từng thí sinh, lưu vĩnh viễn, giúp đội tư vấn phối hợp với nhau và biết ai đã liên hệ gì
- **Gọi tư vấn**: bấm nút gọi điện trực tiếp qua tel link, không cần copy số
- **Xóa thí sinh**: xóa toàn bộ thông tin và chat, có xác nhận trước khi xóa, dùng để dọn dữ liệu test hoặc spam


**Luồng xử lý dữ liệu**

**Nạp dữ liệu (chạy 1 lần)**

Tài liệu tuyển sinh (file MD, JSON) được chia nhỏ thành các đoạn khoảng 500-1000 ký tự bằng LangChain. Sau đó mỗi đoạn được sinh embedding bằng Gemini Embedding API và lưu vào ChromaDB để phục vụ tìm kiếm theo ngữ nghĩa.

**Xử lý câu hỏi (mỗi lần chat)**

Khi thí sinh gửi câu hỏi, hệ thống sẽ embedding câu hỏi đó rồi tìm kiếm ngữ nghĩa trong ChromaDB để lấy ra các đoạn tài liệu liên quan nhất. Tiếp theo, hệ thống ghép system prompt, tài liệu tìm được và 3 lượt chat gần nhất (lấy từ Redis) thành một prompt hoàn chỉnh, gửi đến Gemini API để sinh câu trả lời. Kết quả trả về được parse từ JSON response, hiển thị câu trả lời kèm các câu hỏi gợi ý tiếp theo, đồng thời lưu vào SQL DB và Redis.


**Thiết kế cơ sở dữ liệu**

**SQL - Bảng chat_logs**

- id: kiểu INTEGER, khóa chính, tự tăng
- session_id: kiểu VARCHAR(100), có index, dùng để truy vấn theo phiên
- user_query: kiểu TEXT, lưu câu hỏi của thí sinh
- bot_response: kiểu TEXT, lưu câu trả lời của chatbot
- timestamp: kiểu DATETIME, lưu thời điểm hội thoại

Dùng SQLAlchemy ORM nên có thể chuyển đổi giữa SQLite, MySQL, PostgreSQL mà không cần sửa code.

**Redis - Session cache**

- Key: chat_history:{session_id}
- Value: JSON array chứa 6 message gần nhất (tương đương 3 lượt hỏi-đáp)
- TTL: 24 giờ
- Nếu không có Redis thì hệ thống tự dùng In-memory, không bị crash

**ChromaDB - Vector store**

Lưu embedding vectors của tài liệu tuyển sinh, truy vấn bằng Semantic Search. Chạy local, không cần setup server riêng.

**LocalStorage (Frontend)**

- vju_users: danh sách thí sinh đã đăng ký
- vju_chats_{phone}: lịch sử chat theo số điện thoại
- vju_gemini_key: API Key mà người dùng nhập vào


**API Endpoints**

- GET /health: kiểm tra server có đang chạy không
- POST /chat: gửi câu hỏi, nhận câu trả lời từ RAG engine
- GET /history/{session_id}: lấy lịch sử chat của một phiên

Có bật CORS cho phép frontend gọi từ mọi domain.


**Hướng dẫn kiểm thử cho Tester**

**Tài khoản test**

**Admin**
  Tên đăng nhập: adminvju
  Mật khẩu: adminvju2026

Cách truy cập: Mở file index.html, chọn Đăng nhập, nhấn Đăng nhập Admin, nhập tài khoản ở trên.

**Thí sinh (tạo mới để test)**
  1. Nhấn Đăng ký, điền số điện thoại 10 số, họ tên, ngày sinh, tổ hợp môn
  2. Nhấn Đồng ý ở modal xác nhận dữ liệu
  3. Nhập mã OTP 6 số hiển thị ở góc trên phải modal (chế độ demo)
  4. Sau khi đăng nhập, nhập Gemini API Key ở sidebar bên trái để bắt đầu chat

**Một số câu hỏi mẫu để kiểm thử**

- Trường Đại học Việt Nhật có những ngành nào?
- Học phí ngành Công nghệ thông tin là bao nhiêu?
- Phương thức xét tuyển của VJU năm nay như thế nào?
- Trường có chính sách học bổng gì không?
- Điều kiện đầu vào ngành Kỹ thuật điện tử là gì?
- Ký túc xá của trường ở đâu?

**Lưu ý khi kiểm thử**

- Mỗi session_id đại diện cho một phiên chat riêng biệt, hệ thống sẽ ghi nhớ lịch sử hội thoại trong cùng một session
- Nếu hỏi câu hỏi ngoài phạm vi dữ liệu tuyển sinh, chatbot sẽ thông báo không có thông tin và hướng dẫn liên hệ ban tuyển sinh
- Đảm bảo đã chạy bước nạp dữ liệu (python -m src.ingest) trước khi test, nếu không chatbot sẽ không có dữ liệu để trả lời


**Thông tin liên hệ**

Dự án này được thực hiện bởi sinh viên trong quá trình học tập và nghiên cứu. Nếu bạn có góp ý hoặc muốn trao đổi thêm, vui lòng liên hệ qua GitHub.
