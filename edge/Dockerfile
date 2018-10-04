FROM nginx:stable-alpine

web:
  image: nginx
  ports:
   - "8080:80"
  command: /bin/bash -c "envsubst < /etc/nginx/conf.d/mysite.template > /etc/nginx/conf.d/default.conf && exec nginx -g 'daemon off;'"
