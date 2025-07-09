# 🧠 Plagiarism Checker AI (Vietnamese PDF)

Một hệ thống web kiểm tra trùng lặp nội dung giữa các tài liệu PDF tiếng Việt, hỗ trợ cả thuật toán **TF-IDF truyền thống** và **Sentence-BERT (Deep Learning)**.

---

## 🚀 Tính năng

- 📄 Tải lên 1 file PDF để kiểm tra
- 📁 So sánh với nhiều file PDF trong thư mục `data/text_docs/`
- 🧠 Hai phương pháp kiểm tra:
  - **Phương pháp thường**: TF-IDF + Cosine Similarity
  - **Phương pháp Deep**: Sentence-BERT (MiniLM) + Semantic Matching
- 🔍 Highlight các đoạn trùng lặp
- 📊 Xuất báo cáo JSON + PDF
- ⚡ Tối ưu tốc độ bằng cache vector embeddings

---

## 🛠️ Công nghệ sử dụng

- Python 3.10+
- Flask + Bootstrap
- pdfminer.six (đọc PDF text)
- sentence-transformers (`paraphrase-multilingual-MiniLM-L12-v2`)
- scikit-learn
- ReportLab / WeasyPrint (tạo PDF báo cáo)

---

## 📂 Cấu trúc thư mục

```bash
plagrism_ai/
├── app.py                  # Main Flask app
├── utils/                  # Các mô-đun xử lý PDF, matching, highlights
├── templates/index.html    # Giao diện web
├── data/                   # ⚠️ KHÔNG PUSH lên GitHub (bỏ trong .gitignore)
│   └── text_docs/          # Tài liệu cần so sánh
├── reports/                # Output báo cáo
├── uploads/                # File tạm từ người dùng
├── .gitignore              # Bỏ qua thư mục nặng
└── README.md               # Mô tả project

# Bước 1: Cài môi trường
pip install -r requirements.txt

# Bước 2: Khởi chạy Flask
python app.py

# Truy cập tại: http://127.0.0.1:5000
```
