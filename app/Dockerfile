FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
WORKDIR /app
ADD ./requirements.txt /app
RUN pip install -r requirements.txt
ADD . /app
EXPOSE 8000
# pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
