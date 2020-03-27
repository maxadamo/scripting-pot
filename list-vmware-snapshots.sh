#!/bin/bash
#
# it works only in conjunction with TerraformWare (Géant Tool)
#
SEP="======================"
echo "fetching VM list from FRANKFURT"
FRA_VM=$(vm_list -l fra | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')
echo "fetching VM list from PARIS"
PAR_VM=$(vm_list -l par | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')
echo "fetching VM list from LONDON"
LON_VM=$(vm_list -l lon | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')
echo -e "done\n"

echo -e "Datacenter: FRANKFURT\n${SEP}"
for VM in $FRA_VM; do
    SNAP=$(vm_snapshot -l fra --vm $VM -ls)
    if echo "$SNAP" | grep -q ']  '; then
        echo "$SNAP" | awk '!/ found /&&!/Script processed/'
    fi
done

echo -e "Datacenter: PARIS\n${SEP}"
for VM in $PAR_VM; do
    SNAP=$(vm_snapshot -l fra --vm $VM -ls)
    if echo "$SNAP" | grep -q ']  '; then
        echo "$SNAP" | awk '!/ found /&&!/Script processed/'
    fi
done

echo -e "Datacenter: LONDON\n${SEP}"
for VM in $LON_VM; do
    SNAP=$(vm_snapshot -l fra --vm $VM -ls)
    if echo "$SNAP" | grep -q ']  '; then
        echo "$SNAP" | awk '!/ found /&&!/Script processed/'
    fi
done
