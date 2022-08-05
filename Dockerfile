FROM python:3.7
LABEL maintainer="Double <ethan9141@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y tesseract-ocr \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

COPY . /tmp/src
WORKDIR /tmp/src
RUN sed -i 's/__commit_hash__.*/__commit_hash__ = "$(git rev-parse --short HEAD)"/g' /tmp/src/tnpb/__init__.py
RUN pip install /tmp/src && rm -rf /tmp/src

### Avoid: 
# ImportError: libGL.so.1: cannot open shared object file: No such file or directory
RUN pip uninstall -y opencv-python opencv-python-headless && \
    pip install opencv-python-headless==4.4.0.46

ENV DEBIAN_FRONTEND=dialog

WORKDIR /
CMD ["tnpb"]
