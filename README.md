# 1. Create and enter project directory
mkdir quic-chat
cd quic-chat

# 2. Create directory structure
mkdir -p src/{client,server,protocol,utils} config ssl tests

# 3. Generate SSL certificates
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"

# 4. Create client config
cat > config/client_config.json << EOL
{
    "server_host": "localhost",
    "server_port": 4433,
    "alpn_protocols": ["chat/1"],
    "verify_mode": 0
}
EOL

# 5. Create server config
cat > config/server_config.json << EOL
{
    "host": "0.0.0.0",
    "port": 4433,
    "cert_path": "ssl/cert.pem",
    "key_path": "ssl/key.pem",
    "alpn_protocols": ["chat/1"]
}
EOL

# 6. Set up Python environment
python3 -m venv venv
source venv/bin/activate

# 7. Create requirements.txt
cat > requirements.txt << EOL
aioquic>=0.9.20
python-jose[cryptography]>=3.3.0
bcrypt>=4.0.1
pytest>=7.3.1
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
EOL

# 8. Install dependencies
pip install -r requirements.txt

# 9. Set permissions for SSL directory
chmod 755 ssl
chmod 644 ssl/*.pem

# 10. Verify installation
pip list  # Should show aioquic, python-jose, bcrypt, etc.
ls -l ssl/  # Should show cert.pem and key.pem

# 11. Start the server (in terminal 1)
source venv/bin/activate
PYTHONPATH=$PWD python -m src.server.chat_server

# 12. Start the client (in terminal 2)
source venv/bin/activate
PYTHONPATH=$PWD python -m src.client.chat_client

# --- Optional Commands ---

# Check if port is in use
netstat -tuln | grep 4433

# Kill process using port if needed
sudo lsof -i :4433
kill -9 <PID>

# Run tests
PYTHONPATH=$PWD pytest tests/ -v

# Generate coverage report
pytest --cov=src tests/ --cov-report=html

# Cleanup
deactivate  # Deactivate virtual environment
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache .coverage htmlcov

# Regenerate certificates if needed
rm ssl/*.pem
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"

# Chat Commands
# hello everyone          # Send public message
# @username message      # Send private message
# /quit                  # Exit the chat