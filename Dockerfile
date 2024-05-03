# 使用 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制 Python 文件和依赖文件到工作目录
COPY requirements.txt .
COPY api.py .
COPY wb.txt .

EXPOSE 50600

# 安装依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 设置入口点或命令
CMD ["python", "api.py"]
