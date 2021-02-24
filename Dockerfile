FROM python:3.9.2-buster

ENV APP_DIR /unity_cloud_discord_ci_bot
ENV PYTHONPATH $PYTHONPATH:$APP_DIR

WORKDIR $APP_DIR

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends locales locales-all

COPY . $APP_DIR

CMD python app/discord_bot.py
