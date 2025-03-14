# 构建阶段
FROM python:3.10-alpine AS builder

WORKDIR /app

# 安装构建依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    jpeg-dev \
    zlib-dev \
    libjpeg

# 复制并安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# 运行阶段
FROM python:3.10-alpine

WORKDIR /app

# 安装运行时依赖
RUN apk add --no-cache \
    jpeg \
    libstdc++ \
    libgomp

# 从构建阶段复制 Python 包
COPY --from=builder /root/.local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# 复制应用代码
COPY ddddocr/ ./ddddocr/

# 创建非 root 用户
RUN adduser -D appuser && \
    chown -R appuser:appuser /app

USER appuser

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:${PORT:-5000}/fx_ocr || exit 1

# 启动应用
CMD ["python", "ddddocr/orcApi.py"] 