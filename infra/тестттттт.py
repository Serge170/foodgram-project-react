version: '3.8'
services:

  db:
    image: postgres:13.0-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    env_file:
      - .env

  backend:
    image: markkryl93/foodgram:v1.0
    volumes:
      - static_value:/app/static/
      - media_value:/app/media/
    depends_on:
      - db
    env_file:
      - .env
    restart: always

  frontend:
    image: markkryl93/foodgram_front:v1.0
    volumes:
      - ../frontend/:/app/result_build/


  nginx:
    image: nginx:1.19.3
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ../frontend/build:/usr/share/nginx/html/
      - ../docs/:/usr/share/nginx/html/api/docs/
      - static_value:/var/html/static/
      - media_value:/var/html/media/
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  static_value:
  media_value: