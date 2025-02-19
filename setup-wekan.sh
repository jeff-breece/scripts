#!/bin/bash

# Wekan Installation Script for Ubuntu
# Make sure to run this script as root or with sudo privileges

# Variables - Update these accordingly
DOMAIN="localhost"   # Change this to your domain
SERVER_IP="127.0.0.1" # Change this if using IP instead of domain
PORT="3001"
MONGODB_USER="wekan"
MONGODB_PASSWORD="Jefrobaby656#"  # Change this to a strong password

# Update System and Install Dependencies
echo "Updating system and installing dependencies..."
sudo apt update --fix-missing && sudo apt upgrade -y
sudo apt install -y curl snapd nginx certbot python3-certbot-nginx dnsutils

# Ensure Snap is enabled
echo "Enabling Snap service..."
sudo systemctl enable --now snapd

# Verify network connectivity
echo "Checking internet connection..."
ping -c 4 google.com || { echo "Network issue detected. Check your internet connection." ; exit 1; }

# Install Wekan via Snap
echo "Installing Wekan..."
sudo snap install wekan || { echo "Wekan installation failed." ; exit 1; }

# Configure Wekan
echo "Configuring Wekan..."
sudo snap set wekan root-url="http://$SERVER_IP"
sudo snap set wekan port="$PORT"
sudo snap set wekan mongodb-user="$MONGODB_USER"
sudo snap set wekan mongodb-password="$MONGODB_PASSWORD"

# Restart Wekan Service
echo "Restarting Wekan service..."
sudo systemctl restart snap.wekan.wekan
sudo systemctl enable snap.wekan.wekan

# Configure Firewall (UFW) if enabled
echo "Configuring firewall (UFW)..."
sudo ufw allow $PORT/tcp

# Install and Configure Nginx
echo "Installing and setting up Nginx..."
sudo apt install -y nginx || { echo "Nginx installation failed." ; exit 1; }
NGINX_CONF="/etc/nginx/sites-available/wekan"
echo "server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:$PORT/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}" | sudo tee $NGINX_CONF

# Enable Nginx site configuration
echo "Enabling Nginx configuration..."
sudo ln -s /etc/nginx/sites-available/wekan /etc/nginx/sites-enabled/ || { echo "Failed to create symlink." ; exit 1; }
sudo systemctl restart nginx || { echo "Failed to restart Nginx." ; exit 1; }

# Secure with Let's Encrypt SSL
echo "Installing SSL with Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN || { echo "Certbot setup failed." ; exit 1; }

# Restart services
echo "Restarting services..."
sudo systemctl restart nginx
sudo systemctl restart snap.wekan.wekan

echo "Wekan installation complete! Access it at: https://$DOMAIN or http://$SERVER_IP:$PORT"