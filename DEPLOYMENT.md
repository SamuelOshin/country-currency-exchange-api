# Deployment Guide

This guide covers deployment options for the Country Currency API.

## Table of Contents
- [Railway Deployment](#railway-deployment)
- [Heroku Deployment](#heroku-deployment)
- [AWS Deployment](#aws-deployment)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [Render Deployment](#render-deployment)

---

## Railway Deployment (Recommended)

Railway offers easy deployment with MySQL support.

### Prerequisites
- GitHub account
- Railway account

### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main
```

2. **Create Railway Project**
- Go to [Railway](https://railway.app)
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose your repository

3. **Add MySQL Database**
- Click "New" → "Database" → "Add MySQL"
- Railway will automatically provide connection details

4. **Set Environment Variables**
Go to your service → Variables → Add:
```
DATABASE_URL=<from-mysql-service>
API_HOST=0.0.0.0
API_PORT=8000
RESTCOUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD
API_TIMEOUT=30
CACHE_DIR=app/cache
ENVIRONMENT=production
```

5. **Configure Start Command**
- Settings → Deploy → Start Command:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

6. **Deploy**
- Railway will auto-deploy on push
- Get your URL from Settings → Domains

7. **Initial Data Load**
```bash
curl -X POST https://your-app.railway.app/api/v1/countries/refresh
```

---

## Heroku Deployment

### Prerequisites
- Heroku account
- Heroku CLI installed

### Steps

1. **Login to Heroku**
```bash
heroku login
```

2. **Create App**
```bash
heroku create your-app-name
```

3. **Add MySQL Database**
```bash
heroku addons:create jawsdb:kitefin
```

4. **Get Database URL**
```bash
heroku config:get JAWSDB_URL
```

5. **Set Environment Variables**
```bash
heroku config:set ENVIRONMENT=production
heroku config:set DATABASE_URL=$(heroku config:get JAWSDB_URL)
heroku config:set RESTCOUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
heroku config:set EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD
heroku config:set API_TIMEOUT=30
heroku config:set CACHE_DIR=app/cache
```

6. **Create Procfile**
```bash
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

7. **Deploy**
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

8. **Run Migrations**
```bash
heroku run alembic upgrade head
```

9. **Initial Data Load**
```bash
curl -X POST https://your-app-name.herokuapp.com/api/v1/countries/refresh
```

---

## AWS Deployment

### Architecture
- EC2: Application server
- RDS: MySQL database
- ALB: Load balancer
- S3: Image storage (optional)

### Steps

1. **Create RDS MySQL Instance**
- Go to AWS RDS Console
- Create database → MySQL
- Note connection details

2. **Launch EC2 Instance**
- Ubuntu 22.04 LTS
- t2.micro (or larger)
- Security group: Allow 22, 80, 443, 8000

3. **SSH into EC2**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

4. **Install Dependencies**
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx mysql-client -y
```

5. **Clone Repository**
```bash
git clone <your-repo-url>
cd country-currency-api
```

6. **Setup Application**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

7. **Configure Environment**
```bash
nano .env
# Add your RDS connection details
DATABASE_URL=mysql+pymysql://admin:password@your-rds-endpoint:3306/countries_db
```

8. **Run Migrations**
```bash
alembic upgrade head
```

9. **Create Systemd Service**
```bash
sudo nano /etc/systemd/system/country-api.service
```

Add:
```ini
[Unit]
Description=Country Currency API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/country-currency-api
Environment="PATH=/home/ubuntu/country-currency-api/venv/bin"
ExecStart=/home/ubuntu/country-currency-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

10. **Start Service**
```bash
sudo systemctl start country-api
sudo systemctl enable country-api
```

11. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/country-api
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/country-api /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

12. **SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## DigitalOcean Deployment

### Using App Platform

1. **Create App**
- Go to DigitalOcean → App Platform
- Connect GitHub repository

2. **Add Database**
- Add Component → Database → MySQL

3. **Configure Environment**
Add environment variables from database connection

4. **Configure Build**
- Build Command: `pip install -r requirements.txt`
- Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8080`

5. **Deploy**
DigitalOcean will build and deploy automatically

### Using Droplet

Similar to AWS EC2 deployment above.

---

## Render Deployment

**Note**: Task specifies Render is forbidden for this cohort.

---

## Post-Deployment Checklist

✅ Database is accessible  
✅ Environment variables are set  
✅ Migrations have run  
✅ Initial data refresh completed  
✅ All endpoints are accessible  
✅ SSL certificate installed (production)  
✅ Health check endpoint responds  
✅ Summary image generation works  
✅ Error responses are correct  

## Testing Deployment

```bash
# Health check
curl https://your-domain.com/health

# Refresh data
curl -X POST https://your-domain.com/api/v1/countries/refresh

# Get all countries
curl https://your-domain.com/api/v1/countries

# Get status
curl https://your-domain.com/api/v1/status

# Get image
curl https://your-domain.com/api/v1/countries/image --output summary.png

# Test specific country
curl https://your-domain.com/api/v1/countries/Nigeria
```

## Monitoring

### Railway
- Built-in metrics dashboard
- View logs in real-time
- Set up alerts

### AWS CloudWatch
```bash
# View logs
aws logs tail /aws/ec2/country-api --follow
```

### Basic Uptime Monitoring
- Use UptimeRobot (free)
- Monitor `/health` endpoint
- Set up email alerts

## Troubleshooting

### Database Connection Issues
```bash
# Test database connection
mysql -h your-db-host -u username -p database_name

# Check environment variables
printenv | grep DATABASE_URL
```

### Application Not Starting
```bash
# Check logs (Railway)
railway logs

# Check logs (Heroku)
heroku logs --tail

# Check logs (systemd)
sudo journalctl -u country-api -f
```

### External API Timeout
- Increase `API_TIMEOUT` environment variable
- Check firewall rules allow outbound HTTPS

### Image Generation Fails
```bash
# Install required fonts (Linux)
sudo apt-get install fonts-dejavu-core

# Check cache directory permissions
ls -la app/cache
chmod 755 app/cache
```

## Performance Optimization

### Database Indexing
Indexes are already defined in the model, but verify:
```sql
SHOW INDEX FROM countries;
```

### Connection Pooling
Already configured in `database.py`:
- `pool_pre_ping=True`
- `pool_recycle=3600`

### Caching Strategy
- Data is cached in MySQL
- Refresh only when needed via POST endpoint
- Consider Redis for session caching (optional enhancement)

## Security Best Practices

✅ Use environment variables for secrets  
✅ Enable SSL/TLS in production  
✅ Keep dependencies updated  
✅ Use strong database passwords  
✅ Restrict database access by IP  
✅ Enable CORS only for trusted domains  
✅ Rate limit API endpoints (optional)  
✅ Regular security audits  

## Backup Strategy

### Database Backups

**Railway**: Automatic backups included

**Heroku**: 
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

**AWS RDS**: Enable automated backups in console

**Manual Backup**:
```bash
mysqldump -h host -u user -p database_name > backup.sql
```

### Restore from Backup
```bash
mysql -h host -u user -p database_name < backup.sql
```

## Scaling Considerations

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use managed database (RDS, Railway DB)
- Ensure cache directory is shared (S3, NFS)

### Vertical Scaling
- Increase server resources (RAM, CPU)
- Optimize database queries
- Use database read replicas for GET requests

## Cost Estimation

### Railway
- Hobby: $5/month (includes MySQL)
- Pro: $20/month

### Heroku
- Basic: $7/month (dyno) + $15/month (MySQL)
- Standard: $25/month + $50/month

### AWS
- EC2 t2.micro: ~$10/month
- RDS db.t3.micro: ~$15/month
- Data transfer: ~$5/month
- **Total**: ~$30/month

### DigitalOcean
- Basic Droplet: $6/month
- Managed MySQL: $15/month
- **Total**: ~$21/month

## Support

For deployment issues:
1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Review external API accessibility
5. Check firewall/security group rules

## Additional Resources

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Documentation](https://docs.railway.app/)
- [Heroku Python Guide](https://devcenter.heroku.com/articles/getting-started-with-python)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [DigitalOcean Tutorials](https://www.digitalocean.com/community/tutorials)