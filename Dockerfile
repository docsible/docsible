FROM alpine:latest

WORKDIR /usr/local/
ENV PATH="/usr/local/docsible/bin:$PATH"

COPY . . 

RUN apk update && \
    apk add python3 && \
    apk add py3-pip && \
    python3 -m venv ./docsible && \
    . ./docsible/bin/activate && \
    pip install docsible

ENTRYPOINT ["docsible"]
