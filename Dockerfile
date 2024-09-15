# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container to /app
WORKDIR /app

# Update package lists and install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    apache2 \
    apache2-utils \
    python3-dev \
    python3.10 \
    libapache2-mod-wsgi-py3 \
    python3-pip \
    python3.10-venv \
    pkg-config \
    default-libmysqlclient-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Enable Apache's WSGI module
RUN a2enmod wsgi

# Copy the dependencies file to the working directory
COPY requirements.txt /app/

# Install Python dependencies from requirements.txt
RUN pip3 cache purge && \
    pip3 install -r requirements.txt --no-cache-dir

# Copy the entire project to the working directory
COPY . /app/

# Set appropriate permissions for directories and files
RUN chmod 775 /app
RUN chmod 775 /app/PEMA
RUN chmod 775 /app/prestamos
RUN chmod 775 /app/PEMA/static
RUN chmod 775 /app/prestamos/wsgi.py
RUN chmod 777 /app/media
RUN chmod -R 777 /app/media
RUN chmod -R 777 /app/data
RUN chmod -R 777 /var/www

# Enable the default Apache virtual host configuration
RUN a2ensite 000-default.conf

# Expose port 80 for HTTP traffic
EXPOSE 80

# Start Apache in the foreground
CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
