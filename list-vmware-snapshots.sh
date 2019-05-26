#!/bin/bash
#
# it works only in conjunction with TerraformWare (Géant Tool)
#
FRA_VM=$(vm_list -l fra | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')
PAR_VM=$(vm_list -l par | awk -F '/' '/\/vm\//&&!/Templates/{ print $NF }')

for VM in $FRA_VM $PAR_VM; do

    SNAP=$(vm_snapshot -l fra --vm $VM -ls)
    if echo "$SNAP" | grep -q ']  '; then
        echo "$SNAP" | awk '!/ found /&&!/Script processed/'
    fi

done
