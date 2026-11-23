#!/bin/bash
# install_set.sh <minecraft dir> <mods dir> [server]  — copies the HiTech set: jars, scripts, configs (+resources for clients)
set -e
MC="$1"; MODS="$2"; SIDE="${3:-client}"
H="C:/Users/avito/McSkill/clients/Hitech1122jvm21"; T=F:/minecraft-mods/_tools/hitech
while IFS= read -r j; do
  j="${j/#H\//$H/mods/}"; cp "$j" "$MODS/"
done < $T/hitech_set.txt
mkdir -p "$MC/scripts" "$MC/config"
rm -f "$MC"/scripts/*.zs
python -I $T/copy_scripts.py "$H/scripts" "$MC/scripts" "*.zs" | tail -1
for c in modularmachinery requious requious.cfg AE2Stuff JAOPCA.cfg MixedMod extendedae.cfg gendustry gendustryjei.cfg htc_reactors.cfg nae2.cfg novaeng_core.cfg lazy_ae2.cfg; do cp -r "$H/config/$c" "$MC/config/"; done
sed -i 's/S:applicationID=[0-9]*/S:applicationID=/' "$MC/config/MixedMod/MixedMod.cfg"
if [ "$SIDE" != server ]; then
  python -I $T/extract_assets.py "$H" "$MC" contenttweaker modularmachinery requious gendustry threng mixedmod htc_reactors nae2 novaeng_core
fi
echo installed
