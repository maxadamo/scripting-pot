#!/usr/bin/ruby
#
host = ARGV[0]
hostgrp = host.downcase.gsub(%r{[0-9]}, '').gsub(%r{(^lon|^ch)-}, '').gsub(%r{(^dev|^test|^uat|^prod|^prd)-}, '')
hostgrp = if hostgrp.include? 'psma-gn-'
            'geant-psma'
          elsif ['psmp-gn-bw', 'ps-test', 'psmp-lhc-mgmt', 'psmp-gn-mgmt-'].include?(hostgrp)
            'geant-psmp'
          elsif ['rhps', 'rhpsc'].include?(hostgrp)
            'perfsonarkit'
          else
            hostgrp
          end

print("#{hostgrp}\n")

