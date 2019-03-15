#!/usr/bin/ruby
#
host = ARGV[0]
hostgrp = host.downcase.gsub(/[0-9]/, '').gsub(/(^test|^uat|^prod)-/, '')
hostgrp = if hostgrp.include? 'psma-gn-'
            'geant-psma'
          elsif [
            'psmp-gn-bw', 'ps-test', 'psmp-lhc-mgmt', 'psmp-gn-mgmt-'
          ].any? { |w| hostgrp.include?(w) }
            'geant-psmp'
          elsif hostgrp == 'rhps'
            'perfsonarkit'
          elsif hostgrp.include? 'ch-dev-'
            'ch-dev'
          elsif hostgrp.include? 'jenkins'
            'jenkins'
          else
            hostgrp
          end

print hostgrp
