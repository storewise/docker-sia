FROM golang:1.10-alpine

ENV APP=sia
ENV BASEDIR=/srv/apps/$APP
ENV APPDIR=$BASEDIR/app

# Create initial dirs
RUN mkdir -p $APPDIR
WORKDIR $APPDIR

# Install system dependencies
ENV RUNTIME_PACKAGES socat curl
ENV BUILD_PACKAGES git build-base
RUN apk --no-cache add $RUNTIME_PACKAGES

# Install Sia
RUN apk --no-cache add $BUILD_PACKAGES && \
    go get -u github.com/NebulousLabs/Sia/... && \
    apk del $BUILD_PACKAGES

COPY entrypoint.sh $APPDIR

EXPOSE 8000
ENTRYPOINT ./entrypoint.sh
