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
sudo apt install python3 python3-pip python3-pil python3-bcrypt python3-webpy python3-markdown zip
pip3 install webpy-v.0.76.zip

cat <<'EOF'
                       .-.
        .-""`""-.    |(@ @)
     _/`oOoOoOoOo`\_ \ \-/
    '.-=-=-=-=-=-=-.' \/ \
      `-=.=-.-=.=-'    \ /\
         ^  ^  ^       _H_ \

EOF

