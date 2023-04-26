pipeline {
    agent {
        node {
            label 'cloudythy'
        }
    }

    parameters {
        string(name: 'REPO_URLS', defaultValue: '', description: 'Comma-separated list of repository URLs')
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Check for changes in Repositories') {
            steps {
                script {
                    def urls = params.REPO_URLS.split(',')
                    def changedRepositories = []
                    for (url in urls) {
                        def branch = github.branch(env.CHANGE_BRANCH)
                        def changeset = branch.commitId
                            if (changeset != readFile(".last_${url}_${env.CHANGE_BRANCH}_changeset", "").trim()) {
                                echo "Changes detected in ${url}:${env.CHANGE_BRANCH}. Adding to list of changed repositories."
                                changedRepositories.add(url)
                                writeFile file: ".last_${url}_${env.CHANGE_BRANCH}_changeset", text: "${changeset}"
                            }
                    }
                    env.CHANGED_REPOS = changedRepositories.join(',')
                }
            }
        }

        stage('Build Repositories') {
            when {
                expression { env.CHANGED_REPOS != null }
            }
            steps {
                script {
                    def changedRepositories = env.CHANGED_REPOS.split(',')
                    for (url in changedRepositories) {
                        def branch = env.CHANGE_BRANCH
                        def changeset = github.branch(branch).commitId
                        def directoryName = url.substring(url.lastIndexOf('/') + 1, url.lastIndexOf('.'))
                        echo "Building ${url}:${branch} at ${changeset}"
                        sh "git clone ${url} ${directoryName}"
                        sh "cd ${directoryName}"
                        sh "git checkout ${branch}"
                        cd model 
                        sh "chmod +x ./build.sh"
                        sh "./build.sh"
                        sh "cd .."
                        sh "rm -rf ${directoryName}"
                    }
                }
            }
        }
    }
}