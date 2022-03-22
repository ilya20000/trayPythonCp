FROM alpine:3.14.2 
LABEL maintainer="OpenWebServer <info@openwebserver.net>"
RUN apk add php7-fpm
RUN apk add nginx 

RUN apk add apache2
RUN sed "s/Listen 80/Listen 8080/g" /etc/apache2/httpd.conf> /root/tmp
RUN mv /root/tmp /etc/apache2/httpd.conf

RUN apk update && \
	apk add mysql mysql-client && \
	addgroup mysql mysql && \
	mkdir /scripts
	#rm -rf /var/cache/apk/*

#RUN sed "s/\[mysqld\]/\[mysqld\]\\nuser=root/g" /etc/my.cnf> /root/tmp
#RUN mv /root/tmp /etc/my.cnf

VOLUME ["/var/lib/mysql"]

COPY ./startmysql.sh /scripts/startmysql.sh
RUN chmod +x /scripts/startup.sh

#RUN apk add phpmyadmin

EXPOSE 3306
EXPOSE 9000 
EXPOSE 80

ENTRYPOINT ["/scripts/startmysql.sh"]


CMD [ "php-fpm7", "-F"]
CMD ["httpd", "-DNO_DETACH", "-DFOREGROUND", "-e", "info"]
#CMD ["nginx", "-g", "daemon off;"]

