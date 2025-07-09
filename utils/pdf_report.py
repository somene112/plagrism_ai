import pdfkit
from flask import render_template_string

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        body { font-family: 'DejaVu Sans', sans-serif; }
        .highlight { background-color: #ffcccc; }
        table, th, td { border: 1px solid black; border-collapse: collapse; padding: 6px; }
        th { background-color: #f0f0f0; }
    </style>
</head>
<body>
    <h2>BÁO CÁO KIỂM TRA TRÙNG LẶP</h2>
    <p><strong>File gốc:</strong> {{ input_filename }}</p>
    <hr>
    {% for result in results %}
        <h4>📄 {{ result.file }}</h4>
        <p><strong>Tỷ lệ trùng:</strong> {{ result.similarity }}%</p>
        <p><strong>Số đoạn trùng:</strong> {{ result.matched_segments|length }}</p>
        {% if result.matched_segments %}
            <ul>
                {% for seg in result.matched_segments %}
                    <li><span class="highlight">{{ seg.text }}</span></li>
                {% endfor %}
            </ul>
        {% endif %}
        <table style="margin-top: 15px;">
            <tr>
                <th>File</th>
                <th>% Trùng</th>
                <th>Số đoạn trùng</th>
                <th>Cảnh báo</th>
            </tr>
            <tr>
                <td>{{ result.file }}</td>
                <td>{{ result.similarity }}%</td>
                <td>{{ result.matched_segments|length }}</td>
                <td>
                    {% if result.similarity >= threshold %}
                        Cảnh báo vượt ngưỡng
                    {% else %}
                        -
                    {% endif %}
                </td>
            </tr>
        </table>
        <hr>
    {% endfor %}
</body>
</html>
"""

def generate_pdf_report(input_filename, results, output_path, threshold=30):
    html = render_template_string(REPORT_TEMPLATE, input_filename=input_filename, results=results, threshold=threshold)
    pdfkit.from_string(html, output_path)
    return output_path
