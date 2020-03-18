apt-get update 
apt install wget supervisor
wget https://github.com/fatedier/frp/releases/download/v0.20.0/frp_0.20.0_linux_amd64.tar.gz 
tar -xzvf frp_0.20.0_linux_amd64.tar.gz
cd frp_0.20.0_linux_amd64
chmod +x frps
cat >frps.ini<<EOF
[common]
bind_port = 7000
vhost_http_port = 80
token = password
EOF
cp frps /usr/bin
cp frps.ini /etc/frps.ini
touch /etc/systemd/system/frps.service
cat >/etc/systemd/system/frps.service<<EOF
[Unit]
Description=frp proxy server
Wants=network-online.target
After=network.target
[Service]
ExecStart=/usr/bin/frps -c /etc/frps.ini
ExecReload=/usr/bin/frps -c /etc/frps.ini reload
ExecStop=/bin/kill -2 $MAINPID
Type=simple
KillMode=none
Restart=on-failure
RestartSec=30
[Install]
WantedBy=multi-user.target
EOF
touch /etc/supervisor/conf.d/frps.conf
cat >/etc/supervisor/conf.d/frps.conf<<EOF
[program:frps]
command =frps -c /etc/frps.ini
autostart = true
autorestart=true
user = root
redirect_stderr = true
stdout_logfile = /var/log/supervisor/frps.log
EOF

