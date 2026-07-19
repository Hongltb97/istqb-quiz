# ISTQB Practice

Website luyện đề tĩnh, chạy được trên GitHub Pages, không cần backend.

## Chạy local

Do trình duyệt chặn `fetch()` khi mở trực tiếp file, hãy chạy web server:

```bash
python -m http.server 8000
```

Mở `http://localhost:8000`.

## Convert Word sang JSON

```bash
pip install -r requirements.txt
python tools/convert_docx.py "input/EXAM 1.docx"
```

Tool tạo `data/manifest.json`, từng file `data/exam-N.json`, và trích ảnh vào `assets/questions/`.

## Deploy GitHub Pages

1. Tạo repository mới trên GitHub.
2. Push toàn bộ thư mục này lên branch `main`.
3. Vào **Settings → Pages**.
4. Chọn **Deploy from a branch**, branch `main`, thư mục `/ (root)`.
5. Mở URL `https://<username>.github.io/<repository>/`.

## Lưu ý dữ liệu

Lịch sử, theme và danh sách câu sai được lưu bằng `localStorage` trên từng trình duyệt.
