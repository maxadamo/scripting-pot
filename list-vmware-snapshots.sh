#!/bin/bash
#
# it works only in conjunction with TerraformWare (Géant Tool)
#

if [[ "$#" -ne 1 ]]; then
    echo "you need to supply one location, between lon, par and fra"
    echo "for instance: ${0} lon"
    exit
fi

while [[ "$#" -gt 0 ]]; do
    case $1 in
    lon | london)
        LOCATION="LONDON"
        loc="lon"
        ;;
    par | paris)
        LOCATION="PARIS"
        loc="par"
        ;;
    fra | frankfurt)
        LOCATION="FRANKFURT"
        loc="fra"
        ;;
    help | h | --help | -h)
        echo "you need to supply one location, between lon, par and fra"
        echo "for instance: ${0} lon"
        exit
        ;;
    *)
        echo "Unknown parameter passed: $1"
        echo "valid parameters are: {lon, par, fra}"
        exit 1
        ;;
    esac
    shift
done

SEP="==============================="
echo -e "${SEP}\nfetching VM list from ${LOCATION}\n${SEP}\n"
FRA_VM=$(vm_list -l ${loc} | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')

echo -e "Datacenter: ${LOCATION}\n${SEP}"
for VM in $FRA_VM; do
    SNAP=$(vm_snapshot -l $loc --vm $VM -ls)
    if echo "$SNAP" | grep -q ']  '; then
        echo "$SNAP" | awk '!/ found /&&!/Script processed/'
    fi
done
