#!/bin/bash

ROOT_UID=0   # Root has $UID 0.

if [ "$UID" -eq "$ROOT_UID" ]
then
   echo "OK"
else
    echo "Run with sudo!"
    echo "sudo ./install.sh"
    exit 0
fi

echo "Hurray! du e sudo user!"
cat <<'EOF'

      .__---~~~(~~-_.
   _-'  ) -~~- ) _-" )_
  (  ( `-,_..`.,_--_ '_,)_
 (  -_)  ( -_-~  -_ `,    )
 (_ -_ _-~-__-~`, ,' )__-'))--___--~~~--__--~~--___--__..
 _ ~`_-'( (____;--==,,_))))--___--~~~--__--~~--__----~~~'`=__-~+_-_.
(@) (@) `````      `-_(())_-~  mn
EOF

echo "Installing all dependencies..."
apt-get update
sudo apt install apache2 libapache2-mod-wsgi-py3 python3-pip python3-pil python3-bcrypt python3-webpy python3-markdown
pip3 install webpy-v.0.76.zip

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ACONF="/etc/apache2/sites-available/heartranked.conf"

echo "Adding local site to /etc/apache2/sites-available/heartranked.conf"
cat <<'EOF' > $ACONF
<VirtualHost *:80>
    ServerName localhost
EOF
echo "    DocumentRoot $DIR" >> $ACONF
echo "    WSGIScriptAlias / $DIR/server.py" >> $ACONF
echo "    WSGIPassAuthorization On" >> $ACONF
echo "    AddType text/html .py" >> $ACONF
echo "    Alias /static $DIR/public_html/" >> $ACONF
echo "    <Directory $DIR/public_html>" >> $ACONF
cat <<'EOF' >> $ACONF
        Options FollowSymlinks
	AllowOverride None
	Require all granted
    </Directory>
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride None
        Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
        Require all granted
    </Directory>
EOF
echo "    ErrorLog $DIR/error.log" >> $ACONF
echo "</VirtualHost>" >> $ACONF

echo "<Directory $DIR>" >> /etc/apache2/apache2.conf
cat <<'EOF' >> /etc/apache2/apache2.conf
	Options Indexes FollowSymLinks
	AllowOverride None
	Require all granted
</Directory>
EOF

sudo a2ensite heartranked.conf
sudo systemctl restart apache2

cat <<'EOF'
                       .-.
        .-""`""-.    |(@ @)
     _/`oOoOoOoOo`\_ \ \-/
    '.-=-=-=-=-=-=-.' \/ \
      `-=.=-.-=.=-'    \ /\
         ^  ^  ^       _H_ \

EOF

