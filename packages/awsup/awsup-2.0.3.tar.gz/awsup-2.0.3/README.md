# 🚀 AWSUP - Lightning-Fast AWS Website Deployment

Production-grade CLI tool for deploying static websites to AWS using S3, CloudFront, Route53, and ACM. Zero configuration, maximum automation.

## ⚡ Quick Start

```bash
# Install globally
pip install awsup

# Deploy your website instantly
cd /path/to/your/website
awsup deploy yourdomain.com --website-path .

# Or deploy with default "Coming Soon" page
awsup deploy yourdomain.com
```

**That's it!** AWSUP handles all AWS infrastructure automatically.

## ✨ Features

- 🎯 **Zero Config** - Works out of the box
- 🔒 **Secure by Default** - SSL, OAC, encryption enabled
- ⚡ **Lightning Fast** - Global CloudFront CDN
- 🛡️ **Production Ready** - Comprehensive validation & error handling
- 🎨 **Beautiful CLI** - Rich terminal UI with progress bars
- 🔄 **Smart State** - Resumes interrupted deployments
- 🌍 **Global** - Works with any domain registrar

## 🎯 Common Workflows

**React/Next.js:**
```bash
npm run build
awsup deploy myapp.com --website-path ./build
```

**Vue/Nuxt:**
```bash
npm run generate  
awsup deploy myapp.com --website-path ./dist
```

**Static HTML:**
```bash
awsup deploy myapp.com --website-path ./public
```

**Jekyll/Hugo:**
```bash
awsup deploy myapp.com --website-path ./_site
```

## 📋 All Commands

```bash
# Deploy website
awsup deploy yourdomain.com --website-path ./build

# Check status
awsup status yourdomain.com

# Clear CDN cache
awsup invalidate yourdomain.com

# Remove all AWS resources
awsup cleanup yourdomain.com

# Advanced: Deploy in phases
awsup phase1 yourdomain.com    # DNS setup
awsup phase2 yourdomain.com    # Full deployment
```

## 🔄 How It Works

1. **Route53** - Creates hosted zone and DNS records
2. **ACM** - Requests and validates SSL certificate  
3. **S3** - Creates secure bucket and uploads files
4. **CloudFront** - Sets up global CDN with SSL
5. **DNS** - Configures domain routing

## 📋 Prerequisites

1. **AWS Account** with appropriate permissions
2. **Python 3.8+** installed  
3. **AWS CLI** configured with credentials
4. **Domain name** (registered with any registrar)

### Required AWS Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "route53:*",
        "s3:*", 
        "cloudfront:*",
        "acm:*",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## 🔧 Domain Configuration

After running `awsup deploy`, configure nameservers at your domain registrar:

```
Configure these nameservers at your registrar:
  NS1: ns-123.awsdns-12.com
  NS2: ns-456.awsdns-34.net
  NS3: ns-789.awsdns-56.org
  NS4: ns-012.awsdns-78.co.uk
```

**Steps:**
1. Log into your domain registrar (GoDaddy, Namecheap, etc.)
2. Go to DNS settings for your domain
3. Change nameservers from default to custom
4. Enter the NS records shown above
5. Wait 5-30 minutes for DNS propagation

## 🛡️ Security Features

- **S3 buckets are private** (no public access)
- **CloudFront Origin Access Control** (OAC)
- **TLS 1.2+ enforced** with automatic SSL certificates
- **Input validation** for domains and files
- **Security scanning** of uploaded content

## 🚨 Troubleshooting

**DNS Not Resolving**
- Verify NS records at your registrar
- Wait up to 48 hours for propagation
- Test: `dig yourdomain.com NS`

**CloudFront Not Updating**
- Clear cache: `awsup invalidate yourdomain.com`
- Wait 15-20 minutes for changes

**Certificate Issues**
- Ensure NS records are configured
- Wait up to 30 minutes for validation

## 💰 Cost Estimates

For a small website (<1GB, <100GB transfer/month): **~$5-10/month**

- **Route53**: $0.50 per hosted zone
- **S3**: ~$0.023 per GB stored
- **CloudFront**: ~$0.085 per GB transferred
- **ACM**: Free with CloudFront

## 🎛️ Advanced Usage

**Multiple environments:**
```bash
awsup deploy staging.myapp.com --website-path ./dist-staging
awsup deploy myapp.com --website-path ./dist-production
```

**Custom configuration:**
```bash
awsup init yourdomain.com --region us-west-2 --environment prod
```

## 📊 Monitoring

AWSUP automatically sets up:
- CloudWatch dashboards
- Resource tagging for cost tracking
- Structured logging
- State management

## 🤝 Support

For issues or feature requests:
- GitHub Issues: https://github.com/Akramovic1/aws-website-quick-deployer/issues
- Include error messages, AWS region, and domain details

## 📄 License

MIT License - Feel free to use and modify.

---

**Made with ❤️ for developers who want simple AWS deployments**