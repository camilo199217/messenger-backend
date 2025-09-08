FROM python:3.13.3

COPY . ./futbolt-back

WORKDIR ./futbolt-back

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
