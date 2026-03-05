# 1. Sử dụng Node bản nhẹ
FROM node:20-slim

WORKDIR /app

# 2. Copy file quản lý thư viện
COPY package.json package-lock.json ./

# 3. Cài đặt thư viện
RUN npm install

# 4. Copy toàn bộ code frontend
COPY . .

# 5. Mở cổng cho Vite (mặc định là 5173)
EXPOSE 5173

# 6. Chạy Vite với flag --host để truy cập được từ bên ngoài container
CMD ["npm", "run", "dev", "--", "--host"]