FROM nginx:alpine

# Copy static files
COPY index.html /usr/share/nginx/html/
COPY chat.css /usr/share/nginx/html/
COPY chat.js /usr/share/nginx/html/

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Run nginx
CMD ["nginx", "-g", "daemon off;"]