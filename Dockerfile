FROM python:3.12-slim
WORKDIR /work
COPY . /work
CMD ["python3", "scripts/verify_public_package.py"]
