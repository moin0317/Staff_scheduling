# Deployment Options for HealthyLife Staff Scheduler

This document outlines several deployment options for the HealthyLife Staff Scheduler application. Choose the option that best fits your requirements and technical infrastructure.

## Option 1: Streamlit Cloud (Recommended for Quick Deployment)

Streamlit Cloud offers free hosting for Streamlit applications with GitHub integration.

1. **Create a GitHub repository**:
   - Push your code to a new GitHub repository
   - Make sure your `requirements.txt` file is in the root directory

2. **Deploy on Streamlit Cloud**:
   - Visit [Streamlit Cloud](https://streamlit.io/cloud)
   - Sign in with your GitHub account
   - Select your repository, branch, and the `app.py` file
   - Click "Deploy"

Your app will be available at a `*.streamlit.app` URL, and you can set up authentication if needed.

## Option 2: Heroku Deployment

1. **Install Heroku CLI**:
   ```bash
   # Download and install from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a Heroku app**:
   ```bash
   heroku create healthylife-staff-scheduler
   ```

4. **Deploy the application**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku master
   ```

5. **Open the application**:
   ```bash
   heroku open
   ```

## Option 3: Docker Deployment

1. **Create a Dockerfile**:
   Create a file named `Dockerfile` in your project root:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt ./
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py"]
   ```

2. **Build the Docker image**:
   ```bash
   docker build -t healthylife-staff-scheduler .
   ```

3. **Run the Docker container**:
   ```bash
   docker run -p 8501:8501 healthylife-staff-scheduler
   ```

4. **Access the application**:
   Open your browser and navigate to `http://localhost:8501`

## Option 4: On-Premises Deployment

For local network deployment:

1. **Set up a Python environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure Streamlit to listen on the network**:
   ```bash
   streamlit run app.py --server.address=0.0.0.0 --server.port=8501
   ```

3. **Access from other computers**:
   Other computers on your network can access the application at `http://[your-ip-address]:8501`

## Option 5: AWS Elastic Beanstalk

1. **Install AWS CLI and EB CLI**:
   ```bash
   pip install awscli awsebcli
   ```

2. **Configure AWS credentials**:
   ```bash
   aws configure
   ```

3. **Initialize EB application**:
   ```bash
   eb init -p python-3.9 healthylife-scheduler
   ```

4. **Create an environment and deploy**:
   ```bash
   eb create healthylife-scheduler-env
   ```

5. **Open the application**:
   ```bash
   eb open
   ```

## Other Considerations

### Database Integration
For production use, you might want to:
- Store historical data in a database
- Set up user authentication
- Configure regular backups

### Performance Optimization
- For larger facilities or more complex scenarios, consider optimizing the MILP solver
- Pre-compute common scheduling patterns
- Implement caching mechanisms

### Maintenance
- Set up CI/CD pipelines for automated testing and deployment
- Create monitoring for application performance
- Regular dependency updates
