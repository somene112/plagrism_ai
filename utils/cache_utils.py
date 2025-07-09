import time
import os

def cleanup_cache_folder(cache_folder="data/embeddings", max_age_hours=72):
    now = time.time()
    cutoff = now - (max_age_hours * 3600)
    deleted = 0
    for filename in os.listdir(cache_folder):
        file_path = os.path.join(cache_folder, filename)
        if os.path.isfile(file_path) and filename.endswith(".npy"):
            created_time = os.path.getctime(file_path)
            if created_time < cutoff:
                try:
                    os.remove(file_path)
                    deleted += 1
                except Exception as e:
                    print(f"❌ Không thể xóa {filename}: {e}")
    if deleted > 0:
        print(f"✅ Đã xoá {deleted} file cache cũ trong {cache_folder}")
    else:
        print("🧼 Cache vẫn còn mới, không có gì để xóa.")