pipeline {
    agent {
        node {
            label 'cloudythy'
        }
    }
    environment {
        SSH =  credentials('a3b7ee69-1c10-4158-86f4-5ec46e30a266')
        ACCESS_TOKEN = credentials('vove-access-token')
    }

    triggers {
        githubPush()
    }

    stages {
        stage('Detect environment') {
            steps {
                script {
                    def credentialsId = ''
                    env.GIT_BRANCH = env.GIT_BRANCH ?env.GIT_BRANCH: 'origin/dev'
                    def branch = env.GIT_BRANCH
                    if (branch == 'origin/master') {
                        env.BRANCH = "master"
                        env.ENV = 'vove_bug_env_prod'
                        env.ALEMBIC = 'alembic_vove_bug'
                        env.CONTAINER_PREFIX = 'prod'
                    } else if (branch == 'origin/dev') {
                        env.ENV = 'vove_bug_env'
                        env.BRANCH = "dev"
                        env.ALEMBIC = 'alembic_vove_bug'
                        env.CONTAINER_PREFIX = 'dev'
                    }
                }
            }
        }
        stage('Clean workspace before build') {
            steps {
                script{
                    sh "rm -rf model"
                }
            }
        }
        stage('Build Repositories') {
            steps {
                script {
                    def directoryName = 'model'
                    def url = 'git@github.com:3T-LVTN/model.git'
                    withCredentials([
                        file(credentialsId: env.ENV, variable: 'ENV'),
                        file(credentialsId: env.ALEMBIC, variable: 'ALEMBIC'),
                    ]){
                        sh "ssh-agent bash -c 'ssh-add ${env.SSH}; ssh -o StrictHostKeyChecking=no cloudythy@gmail.com@github.com;git clone ${url} -b ${env.BRANCH} ${directoryName}'"
                        def container_prefix = env.CONTAINER_PREFIX
                        def container_name = container_prefix.length() == 0 ? 'model' : container_prefix + "_model"
                        sh "cp $ENV $WORKSPACE/${directoryName}/.env"
                        sh "cp $ALEMBIC $WORKSPACE/${directoryName}/alembic.ini"
                        sh "cd ${directoryName}; chmod +x ./build.sh; ./build.sh --env $container_prefix --env-file .env"
                    }
                }
            }
        }
    }
}