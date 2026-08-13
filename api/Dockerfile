
FROM kingbrady/fast-api-base:1.0.2-multi-architecture-ollama

COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]