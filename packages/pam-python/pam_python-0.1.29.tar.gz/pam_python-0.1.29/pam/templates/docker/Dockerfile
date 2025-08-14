FROM python:3.13-alpine

COPY . /app

WORKDIR /app

ENV DATA_FOLDER=/app/data
RUN mkdir -p $DATA_FOLDER

RUN pip install --upgrade pip
RUN pip cache purge
RUN pip install -r requirements.txt

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

# ห้ามแก้ -w เป็นอย่างอื่น นอกจาก 1
# เพราะว่า service start เท่านั้นถึงจะรับ on_data ได้
# แต่ถ้ามีหลาย replica มีโอกาสที่ on_data จะเข้า ตัวที่ไม่ได้ Start 
CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "main:app"]