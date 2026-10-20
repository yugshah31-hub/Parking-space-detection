// Alternative CI/CD pipeline for Jenkins (same stages as GitHub Actions)
pipeline {
    agent any

    environment {
        IMAGE_NAME = 'parking-space-detection'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Install & Lint') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements-dev.txt
                    flake8 app tests scripts
                '''
            }
        }
        stage('Test') {
            steps {
                sh '. venv/bin/activate && pytest -v --junitxml=report.xml'
            }
            post { always { junit 'report.xml' } }
        }
        stage('Docker Build') {
            steps { sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG -t $IMAGE_NAME:latest .' }
        }
        stage('Deploy') {
            steps {
                sh '''
                    docker rm -f parking-app || true
                    docker run -d --name parking-app -p 5000:5000 $IMAGE_NAME:latest
                    sleep 8
                    curl --fail http://localhost:5000/health
                '''
            }
        }
    }
    post {
        failure { echo 'Pipeline failed - check the stage logs.' }
        success { echo 'Pipeline succeeded - app deployed on port 5000.' }
    }
}
