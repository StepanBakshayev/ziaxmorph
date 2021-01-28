FROM pypy:3.7-buster

WORKDIR /var/build/ziaxmorph

COPY ziaxmorph.py .
COPY poetry.lock .
COPY pyproject.toml .

RUN pip install -U pip wheel setuptools
RUN pip install poetry==1.1.4

RUN poetry build --format wheel
RUN pip uninstall --yes poetry

RUN pip install ./dist/ziaxmorph-0.1.0-py3-none-any.whl

RUN rm -rf /var/build/ziaxmorph

EXPOSE 2021

CMD ["gunicorn", "--bind", ":2021", "--keep-alive", "15", "--user", "nobody", "--group", "nogroup", "ziaxmorph:application"]
