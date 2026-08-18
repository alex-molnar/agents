FROM nginx:1.29.8

ARG BASE_URL="http://localhost:8080"

RUN rm -f /usr/share/nginx/html/index.html

COPY index.html /usr/share/nginx/html
COPY script.js /usr/share/nginx/html
COPY style.css /usr/share/nginx/html

RUN sed -i "s|PARAM_BASE_URL|$BASE_URL|g" /usr/share/nginx/html/script.js
