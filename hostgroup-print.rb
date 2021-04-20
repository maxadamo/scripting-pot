#!/usr/bin/ruby
#
host = ARGV[0]
hostgrp = host.to_s.downcase.gsub(/[0-9]/, '').gsub(/(^lon|^ch)-/, '').gsub(/(^dev|^test|^uat|^prod|^prd)-/, '')
hostgrp = if hostgrp.include? 'psma-gn-'
            'geant-psma'
          elsif ['psmp-gn-bw', 'ps-test', 'psmp-lhc-mgmt', 'psmp-gn-mgmt-'].any? { |w| hostgrp.include?(w) }
            'geant-psmp'
          elsif %w[rhps rhpsc].include?(hostgrp)
            'perfsonarkit'
          elsif hostgrp.include? 'jenkins'
            'jenkins'
          else
            hostgrp
          end

print("#{hostgrp}\n")
