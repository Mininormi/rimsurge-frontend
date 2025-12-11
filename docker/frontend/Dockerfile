FROM node:20-alpine

# 设置工作目录
WORKDIR /app

# 安装依赖（先复制 package 文件，利用 Docker 缓存）
COPY package*.json ./

# 安装 Node.js 依赖
RUN npm ci

# 复制项目文件
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器（监听所有接口，支持 Docker）
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]

