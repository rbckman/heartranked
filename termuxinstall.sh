#!/data/data/com.termux/files/usr/bin/bash

echo "Initializing Heartranked Version 11 Installer for Android Termux..."
cat <<'EOF'
      .__---~~~(~~-_.
   _-'  ) -~~- ) _-" )_
  (  ( `-,_..`.,_--_ '_,)_
 (  -_)  ( -_-~  -_ `,    )
 (_ -_ _-~-__-~`, ,' )__-'))--___--~~~--__--~~--___--__..
 _ ~`_-'( (____;--==,,_))))--___--~~~--__--~~--__----~~~'`=__-~+_-_.
(@) (@) `````      `-_(())_-~  mn
EOF

# 1. System updates inside Termux architecture
echo "Updating Termux repositories..."
pkg update -y && pkg upgrade -y

# 2. Grab system dependencies safely inside native phone sandbox environment
echo "Installing core utilities, media libraries, and compression systems..."
pkg install -y python ndk-sysroot clang make libjpeg-turbo wget zip unzip ffmpeg sox mediainfo

# 3. Handle specific modern python wheels inside mobile platforms
echo "Upgrading pip components..."
pip install --upgrade pip setuptools wheel

# 4. Pull Python libraries required for data extraction, web parsing, and text generation
echo "Installing application requirements..."
pip install mutagen pillow markdown requests

# 5. Extract and deploy web.py framework bundle from project archive
if [ -f "webpy-v.0.76.zip" ]; then
    echo "Installing local web.py wheel framework..."
    pip install ./webpy-v.0.76.zip
else
    echo "⚠️ Warning: webpy-v.0.76.zip archive not directly located in execution path."
    echo "Attempting alternative distribution extraction..."
    pip install web.py
fi

# 6. Initialize tracking paths natively so web.py server loop starts immediately
#echo "Building functional directory tree structures..."
#mkdir -p p/posts p/zipped p/comborank p/heartrank p/deleted u/ r/visitors r/invites r/trusted r/users r/stopflood r/stopresetpass #sessions

cat <<'EOF'
                       .-.
        .-""`""-.    |(@ @)
     _/`oOoOoOoOo`\_ \ \-/
    '.-=-=-=-=-=-=-.' \/ \
      `-=.=-.-=.=-'    \ /\
         ^  ^  ^       _H_ \
         
🚀 Installation Complete!
To deploy your sovereign network node live on your phone, execute:
python server.py
EOF
