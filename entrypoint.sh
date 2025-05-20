echo "127.0.0.1 semgrep.dev" >> /etc/hosts ;
cd /mock_server/; python server.py &
semgrep login;
