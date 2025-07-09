from flask import Flask,send_file,render_template,request
import os
import uuid
import shutil
import time
import datetime
from utils.pdf_utils import read_text_from_pdf,cleanup_old_uploads
from utils.cache_utils import cleanup_cache_folder
from utils.text_matcher import tfidf_similarity,deep_similarity,deep_segment_similarity,sliding_window_tokens,get_model
from utils.highlights import get_matching_blocks
from utils.pdf_report import generate_pdf_report
from utils.json_report import generate_json_report

UPLOAD_FOLDER="uploads"
DATA_FOLDER="data/text_docs"
REPORT_FOLDER="reports"
REPORT_NAME = "plagrism_report.pdf"
last_cleanup_time = None
CLEANUP_INTERVAL_SECONDS = 3 * 24 * 3600  
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
os.makedirs(REPORT_FOLDER,exist_ok=True)

app=Flask(__name__)

@app.route("/")
def index():
    file_list=os.listdir(DATA_FOLDER)
    return render_template("index.html",file_list=file_list,results=None)

@app.route("/check", methods=["POST"])
def check():
    total_start = time.time()
    global last_cleanup_time
    now = datetime.datetime.now()
    if last_cleanup_time is None or (now - last_cleanup_time).total_seconds() > CLEANUP_INTERVAL_SECONDS:
        print("🧹 Đã quá hạn, tiến hành dọn cache embeddings...")
        cleanup_cache_folder()
        last_cleanup_time = now
    print("\n🟢 Bắt đầu xử lý kiểm tra trùng lặp\n")
    step_start = time.time()
    cleanup_old_uploads(UPLOAD_FOLDER)
    print(f"🧹 Cleanup uploads: {time.time() - step_start:.2f}s")
    input_file = request.files['input_pdf']
    method = request.form.get("method", "tfidf")
    threshold = float(request.form.get("threshold", 30))
    unique_name = f"{uuid.uuid4()}.pdf"
    input_path = os.path.join(UPLOAD_FOLDER, unique_name)
    input_file.save(input_path)
    step_start = time.time()
    input_text = read_text_from_pdf(input_path)
    max_tokens = 10000
    tokens = input_text.split()
    if len(tokens) > max_tokens:
        input_text = " ".join(tokens[:max_tokens])
    print(f"📄 Đọc input PDF: {time.time() - step_start:.2f}s")
    step_start = time.time()
    compare_filenames = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith(".pdf")]
    compare_texts = []
    file_paths = []
    for f in compare_filenames:
        full_path = os.path.join(DATA_FOLDER, f)
        text = read_text_from_pdf(full_path)
        if text.strip():
            compare_texts.append(text)
            file_paths.append(f)
    print(f"📁 Đọc {len(file_paths)} file trong thư mục so sánh: {time.time() - step_start:.2f}s")
    step_start = time.time()
    if method == "tfidf":
        scores = tfidf_similarity(input_text, compare_texts)
        get_segments = get_matching_blocks
        segment_kwargs = {"min_len": 30}
        input_emb = None
        input_segments = None
    else:
        scores = deep_similarity(input_text, compare_texts)
        get_segments = deep_segment_similarity
        segment_kwargs = {"threshold": 0.7, "window_size": 50, "stride": 25}
        input_segments = sliding_window_tokens(input_text, window_size=50, stride=25)
        input_emb = get_model().encode(input_segments, convert_to_tensor=True, batch_size=16)
    print(f"⚙️ Tính điểm tương đồng ({method}): {time.time() - step_start:.2f}s")
    step_start = time.time()
    results = []
    K=5
    top_k_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:K]
    for i in top_k_indices:
        score = scores[i]
        percent = round(score * 100, 2)
        if percent >= threshold:
            if method == "tfidf":
                matched = get_segments(input_text, compare_texts[i], **segment_kwargs)
            else:
                matched = get_segments(input_text, compare_texts[i], input_emb=input_emb, input_segments=input_segments, **segment_kwargs)
            results.append({
                "file": file_paths[i],
                "similarity": percent,
                "matched_segments": matched
            })
    print(f"🔍 Xử lý matching đoạn trùng: {time.time() - step_start:.2f}s")
    step_start = time.time()
    report_path = os.path.join(REPORT_FOLDER, REPORT_NAME)
    json_path = os.path.join(REPORT_FOLDER, "plagrism_report.json")
    generate_pdf_report(input_filename=input_file.filename, results=results, output_path=report_path, threshold=threshold)
    generate_json_report(input_filename=input_file.filename, results=results, output_path=json_path, threshold=threshold)
    print(f"📝 Tạo báo cáo PDF + JSON: {time.time() - step_start:.2f}s")
    print(f"\n✅ Tổng thời gian xử lý: {time.time() - total_start:.2f}s\n")
    return render_template("index.html", file_list=compare_filenames, results=results, input_text=input_text)

@app.route('/download_pdf')
def download_pdf():
    path=os.path.join(REPORT_FOLDER,REPORT_NAME)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "Báo cáo chưa được tạo."

@app.route('/download_json')
def download_json():
    path=os.path.join(REPORT_FOLDER,"plagrism_report.json")
    if os.path.exists(path):
        return send_file(path,as_attachment=True)
    return "Báo cáo chưa được tạo."

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,debug=False,use_reloader=False)
