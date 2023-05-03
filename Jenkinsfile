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
                    env.BRANCH_NAME = env.BRANCH_NAME ?: 'master'
                    def branch = env.BRANCH_NAME
                    if (branch == 'master') {
                        env.ENV = 'vove_bug_env_prod'
                        env.ALEMBIC = 'alembic_vove_bug'
                        env.CONTAINER_PREFIX = 'prod'
                    } else if (branch == 'dev') {
                        env.ENV = 'vove_bug_env'
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
                        sh "ssh-agent bash -c 'ssh-add ${env.SSH}; ssh -o StrictHostKeyChecking=no cloudythy@gmail.com@github.com;git clone ${url} -b ${env.BRANCH_NAME} ${directoryName}'"
                        def container_prefix = env.CONTAINER_PREFIX
                        def container_name = container_prefix.length() == 0 ? 'model' : container_prefix + "_model"
                        sh "cp $ENV $WORKSPACE/${directoryName}/.env"
                        sh "cd ${directoryName}; chmod +x ./build.sh; ./build.sh --env $container_prefix --env-file .env"
                    }
                }
            }
        }
    }
}