from pdfminer.high_level import extract_text
import os
import time

def read_text_from_pdf(filepath: str) -> str:
    txt_path = filepath.replace(".pdf", ".txt")
    try:
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        text = extract_text(filepath).strip()
        if text:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)
        return text
    except Exception as e:
        print(f"❌ Lỗi đọc PDF: {e}")
        return ""

def cleanup_old_uploads(folder_path,max_age_hours=24):
    now=time.time()
    cutoff=now-(max_age_hours*3600)
    deleted=0
    for filename in os.listdir(folder_path):
        file_path=os.path.join(folder_path,filename)
        if os.path.isfile(file_path):
            created_time=os.path.getctime(file_path)
            if created_time<cutoff:
                try:
                    os.remove(file_path)
                    deleted+=1
                except Exception as e:
                    print(f"Lỗi xóa file: {e}")
    if deleted>0:
        print(f"Đã xoá {deleted} file cũ trong {folder_path}")