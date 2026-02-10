#!/bin/bash
# =============================================================================
# Booksmart Backend — AWS EC2 Deployment Script
# Run this ON the EC2 instance after SSH-ing in.
# =============================================================================
set -e

DOMAIN="booksmartutt.duckdns.org"  
EMAIL="0320127831@ut-tijuana.edu.mx"       
DB_ROOT_PASS="pass"      
DB_USER="booksmart_user"
DB_PASS="pass"           
DB_NAME="booksmart"

echo "=== 1. System update ==="
sudo apt update && sudo apt upgrade -y

echo "=== 2. Install Docker ==="
sudo apt install -y docker.io docker-compose-plugin curl git
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER

echo "=== 3. Install MySQL 8 ==="
sudo apt install -y mysql-server
sudo systemctl enable mysql
sudo systemctl start mysql

# Secure MySQL and create the app database/user
sudo mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_ROOT_PASS}';
CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF
echo "   MySQL ready: ${DB_NAME} database created"

echo "=== 4. Install Certbot (Let's Encrypt) ==="
sudo apt install -y certbot

echo "=== 5. Get SSL certificate ==="
# Stop anything on port 80 first
sudo certbot certonly --standalone -d "$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive

echo "=== 6. Clone / copy your project ==="
# Option A: git clone
# git clone https://github.com/your-user/booksmart_backend.git
# cd booksmart_backend

cd ~/booksmart_backend

echo "=== 7. Create .env file ==="
if [ ! -f .env ]; then
    cat > .env <<ENVEOF
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASS}@host.docker.internal:3306/${DB_NAME}
SECRET_KEY=$(openssl rand -hex 32)
ENVEOF
    echo "   .env created — review it with: nano .env"
fi

echo "=== 8. Update nginx.conf with your domain ==="
sed -i "s/your-domain.com/$DOMAIN/g" deploy/nginx.conf

echo "=== 9. Build and start ==="
sudo docker compose up -d --build

echo "=== 10. Run database migrations ==="
# Run alembic inside the container to create tables
sudo docker compose exec api alembic upgrade head

echo "=== 11. Set up auto-renewal for SSL ==="
(sudo crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && docker compose -f $HOME/booksmart_backend/docker-compose.yml restart nginx") | sudo crontab -

echo ""
echo "✅ Deployment complete!"
echo "   https://$DOMAIN        → API"
echo "   wss://$DOMAIN/api/v1/ws?token=JWT  → WebSocket"
echo ""
echo "Useful commands:"
echo "   sudo docker compose logs -f api     # view API logs"
echo "   sudo docker compose restart api     # restart API"
echo "   sudo docker compose down            # stop everything"
