FROM alpine:3.14.2 
LABEL maintainer="NGINX OpenWebServer <info@openwebserver.net>"
RUN apk add --no-cache nginx
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]