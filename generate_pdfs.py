from fpdf import FPDF
import os
import random

os.makedirs("data/text_docs", exist_ok=True)

base_sentences = [
    "Trường Đại học Bách Khoa sẽ tổ chức hội thảo vào tuần tới.",
    "Buổi hội thảo nhằm hỗ trợ sinh viên định hướng nghề nghiệp.",
    "Sinh viên năm cuối được khuyến khích tham gia đầy đủ.",
    "Thông tin chi tiết sẽ được cập nhật trên website của nhà trường.",
    "Hội thảo sẽ có sự tham gia của nhiều chuyên gia từ các doanh nghiệp."
]

paraphrases = [
    "Một hội thảo định hướng nghề nghiệp sẽ diễn ra trong thời gian tới.",
    "Sự kiện giúp sinh viên năm cuối chuẩn bị cho con đường sự nghiệp.",
    "Những bạn sinh viên cuối khóa nên có mặt đầy đủ.",
    "Chi tiết buổi hội thảo sẽ được công bố trên cổng thông tin trường.",
    "Các chuyên gia doanh nghiệp sẽ đến chia sẻ kinh nghiệm thực tế."
]

def generate_text(paraphrase_prob=0.3):
    lines = []
    for i in range(len(base_sentences)):
        if random.random() < paraphrase_prob:
            lines.append(paraphrases[i])
        else:
            lines.append(base_sentences[i])
    return "\n".join(lines)

pdf_font_path = "DejaVuSans.ttf"  # bạn cần có file này ở cùng thư mục

for i in range(1, 101):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", pdf_font_path, uni=True)
    pdf.set_font("DejaVu", size=12)

    text = generate_text(paraphrase_prob=random.uniform(0.2, 0.6))
    pdf.multi_cell(0, 10, text)
    pdf.output(f"data/text_docs/sample_{i:03}.pdf")