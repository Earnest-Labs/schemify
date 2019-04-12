#!/usr/bin/env groovy
@Library('jenkins-pipeline-library') _
 
pipeline {
  agent {
    label "generic"
  }
  options {
    ansiColor colorMapName: 'XTerm'
  }
  stages {
    stage("Display ENV data") {
      steps {
        printEnvSorted ()
      }
    }
  }
}
