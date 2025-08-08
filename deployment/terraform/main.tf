# Claude Agents Infrastructure as Code
# Multi-cloud Terraform configuration for production deployment

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
  }
  
  # Backend configuration - uncomment and configure for your setup
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "claude-agents/terraform.tfstate"
  #   region         = "us-west-2"
  #   encrypt        = true
  #   dynamodb_table = "terraform-lock"
  # }
}

# Local variables
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }
  
  # Kubernetes cluster configuration
  cluster_config = {
    version                = var.kubernetes_version
    node_groups           = var.node_groups
    enable_irsa          = true
    enable_cluster_autoscaler = true
    enable_metrics_server = true
    enable_alb_ingress   = true
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# Random password generation
resource "random_password" "postgres_password" {
  length  = 32
  special = true
}

resource "random_password" "redis_password" {
  length  = 32
  special = false
}

resource "random_id" "jwt_secret" {
  byte_length = 32
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"
  
  name_prefix        = local.name_prefix
  vpc_cidr          = var.vpc_cidr
  availability_zones = slice(data.aws_availability_zones.available.names, 0, 3)
  
  # Subnet configuration
  private_subnet_cidrs = var.private_subnet_cidrs
  public_subnet_cidrs  = var.public_subnet_cidrs
  database_subnet_cidrs = var.database_subnet_cidrs
  
  # NAT Gateway configuration
  enable_nat_gateway = true
  single_nat_gateway = var.environment == "development"
  
  # VPC Flow Logs
  enable_flow_logs = true
  flow_logs_retention = var.cloudwatch_log_retention
  
  tags = local.common_tags
}

# EKS Cluster Module
module "eks" {
  source = "./modules/eks"
  
  cluster_name    = "${local.name_prefix}-cluster"
  cluster_version = var.kubernetes_version
  
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  
  # Node groups configuration
  node_groups = {
    for ng_name, ng_config in var.node_groups : ng_name => merge(ng_config, {
      subnet_ids = module.vpc.private_subnet_ids
    })
  }
  
  # IRSA configuration
  enable_irsa = true
  irsa_oidc_provider_arn = module.eks.oidc_provider_arn
  
  # Add-ons
  cluster_addons = {
    aws-ebs-csi-driver = {
      most_recent = true
    }
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent = true
    }
  }
  
  tags = local.common_tags
}

# RDS Module for PostgreSQL
module "rds" {
  source = "./modules/rds"
  
  identifier = "${local.name_prefix}-postgres"
  
  engine              = "postgres"
  engine_version      = var.postgres_version
  instance_class      = var.postgres_instance_class
  allocated_storage   = var.postgres_allocated_storage
  max_allocated_storage = var.postgres_max_allocated_storage
  
  db_name  = var.postgres_db_name
  username = var.postgres_username
  password = random_password.postgres_password.result
  
  vpc_security_group_ids = [module.security_groups.rds_security_group_id]
  db_subnet_group_name   = module.vpc.database_subnet_group_name
  
  backup_retention_period = var.postgres_backup_retention
  backup_window          = var.postgres_backup_window
  maintenance_window     = var.postgres_maintenance_window
  
  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_enhanced_monitoring.arn
  
  # Encryption
  storage_encrypted = true
  
  # Multi-AZ for production
  multi_az = var.environment == "production"
  
  deletion_protection = var.environment == "production"
  skip_final_snapshot = var.environment != "production"
  
  tags = local.common_tags
}

# ElastiCache Module for Redis
module "redis" {
  source = "./modules/redis"
  
  cluster_id = "${local.name_prefix}-redis"
  
  engine_version    = var.redis_version
  node_type        = var.redis_node_type
  num_cache_nodes  = var.redis_num_nodes
  
  parameter_group_name = aws_elasticache_parameter_group.redis.name
  subnet_group_name    = module.vpc.elasticache_subnet_group_name
  security_group_ids   = [module.security_groups.redis_security_group_id]
  
  # Authentication
  auth_token = random_password.redis_password.result
  
  # Backup
  snapshot_retention_limit = var.redis_backup_retention
  snapshot_window         = var.redis_backup_window
  
  # Maintenance
  maintenance_window = var.redis_maintenance_window
  
  tags = local.common_tags
}

# Security Groups Module
module "security_groups" {
  source = "./modules/security-groups"
  
  name_prefix = local.name_prefix
  vpc_id      = module.vpc.vpc_id
  
  # CIDR blocks for access control
  cluster_security_group_id = module.eks.cluster_security_group_id
  node_security_group_id    = module.eks.node_security_group_id
  
  tags = local.common_tags
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [module.security_groups.alb_security_group_id]
  subnets           = module.vpc.public_subnet_ids
  
  enable_deletion_protection = var.environment == "production"
  
  access_logs {
    bucket  = aws_s3_bucket.access_logs.id
    prefix  = "alb-access-logs"
    enabled = true
  }
  
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-alb"
  })
}

# S3 Bucket for ALB access logs
resource "aws_s3_bucket" "access_logs" {
  bucket        = "${local.name_prefix}-alb-access-logs-${random_id.bucket_suffix.hex}"
  force_destroy = var.environment != "production"
  
  tags = local.common_tags
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket_versioning" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "access_logs" {
  bucket = aws_s3_bucket.access_logs.id
  
  rule {
    id     = "delete_old_logs"
    status = "Enabled"
    
    expiration {
      days = var.alb_access_logs_retention_days
    }
    
    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# IAM Role for RDS Enhanced Monitoring
resource "aws_iam_role" "rds_enhanced_monitoring" {
  name = "${local.name_prefix}-rds-enhanced-monitoring"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "rds_enhanced_monitoring" {
  role       = aws_iam_role.rds_enhanced_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# ElastiCache Parameter Group
resource "aws_elasticache_parameter_group" "redis" {
  family = "redis7.x"
  name   = "${local.name_prefix}-redis-params"
  
  parameter {
    name  = "maxmemory-policy"
    value = "allkeys-lru"
  }
  
  parameter {
    name  = "timeout"
    value = "300"
  }
  
  parameter {
    name  = "tcp-keepalive"
    value = "300"
  }
  
  tags = local.common_tags
}

# Kubernetes provider configuration
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  
  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

# Helm provider configuration
provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    
    exec {
      api_version = "client.authentication.k8s.io/v1beta1"
      command     = "aws"
      args = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
    }
  }
}

# Kubernetes Secret for database credentials
resource "kubernetes_secret" "database_credentials" {
  metadata {
    name      = "database-credentials"
    namespace = "claude-agents"
  }
  
  data = {
    username = var.postgres_username
    password = random_password.postgres_password.result
    host     = module.rds.db_instance_address
    port     = module.rds.db_instance_port
    database = var.postgres_db_name
    url      = "postgresql://${var.postgres_username}:${random_password.postgres_password.result}@${module.rds.db_instance_address}:${module.rds.db_instance_port}/${var.postgres_db_name}"
  }
  
  type = "Opaque"
  
  depends_on = [
    module.eks
  ]
}

# Kubernetes Secret for Redis credentials
resource "kubernetes_secret" "redis_credentials" {
  metadata {
    name      = "redis-credentials"
    namespace = "claude-agents"
  }
  
  data = {
    password = random_password.redis_password.result
    host     = module.redis.cache_nodes[0].address
    port     = module.redis.cache_nodes[0].port
    url      = "redis://:${random_password.redis_password.result}@${module.redis.cache_nodes[0].address}:${module.redis.cache_nodes[0].port}"
  }
  
  type = "Opaque"
  
  depends_on = [
    module.eks
  ]
}

# Claude Agents Helm Release
resource "helm_release" "claude_agents" {
  name       = "claude-agents"
  repository = "./helm"
  chart      = "claude-agents"
  namespace  = "claude-agents"
  
  create_namespace = true
  
  values = [
    templatefile("${path.module}/helm-values.yaml", {
      database_url = "postgresql://${var.postgres_username}:${random_password.postgres_password.result}@${module.rds.db_instance_address}:${module.rds.db_instance_port}/${var.postgres_db_name}"
      redis_url    = "redis://:${random_password.redis_password.result}@${module.redis.cache_nodes[0].address}:${module.redis.cache_nodes[0].port}"
      environment  = var.environment
      domain_name  = var.domain_name
    })
  ]
  
  depends_on = [
    module.eks,
    kubernetes_secret.database_credentials,
    kubernetes_secret.redis_credentials
  ]
}

# Output important information
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_address
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = module.redis.cache_nodes[0].address
  sensitive   = true
}

output "load_balancer_dns" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}