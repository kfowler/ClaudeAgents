# Terraform Variables for Claude Agents Infrastructure

# General Configuration
variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "claude-agents"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "owner" {
  description = "Owner/team responsible for the infrastructure"
  type        = string
  default     = "devops-team"
}

variable "cost_center" {
  description = "Cost center for billing purposes"
  type        = string
  default     = "engineering"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-west-2"
}

# Network Configuration
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "database_subnet_cidrs" {
  description = "CIDR blocks for database subnets"
  type        = list(string)
  default     = ["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]
}

# Kubernetes Configuration
variable "kubernetes_version" {
  description = "Kubernetes version for EKS cluster"
  type        = string
  default     = "1.28"
}

variable "node_groups" {
  description = "EKS node groups configuration"
  type = map(object({
    instance_types = list(string)
    capacity_type  = string
    scaling_config = object({
      desired_size = number
      max_size     = number
      min_size     = number
    })
    update_config = object({
      max_unavailable_percentage = number
    })
    disk_size = number
    ami_type  = string
    labels    = map(string)
    taints = list(object({
      key    = string
      value  = string
      effect = string
    }))
  }))
  default = {
    system = {
      instance_types = ["m5.large"]
      capacity_type  = "ON_DEMAND"
      scaling_config = {
        desired_size = 3
        max_size     = 5
        min_size     = 3
      }
      update_config = {
        max_unavailable_percentage = 25
      }
      disk_size = 50
      ami_type  = "AL2_x86_64"
      labels = {
        "node-type" = "system"
      }
      taints = []
    }
    application = {
      instance_types = ["m5.xlarge", "m5a.xlarge"]
      capacity_type  = "SPOT"
      scaling_config = {
        desired_size = 3
        max_size     = 10
        min_size     = 3
      }
      update_config = {
        max_unavailable_percentage = 25
      }
      disk_size = 100
      ami_type  = "AL2_x86_64"
      labels = {
        "node-type" = "application"
      }
      taints = []
    }
    compute = {
      instance_types = ["c5.2xlarge", "c5a.2xlarge"]
      capacity_type  = "SPOT"
      scaling_config = {
        desired_size = 2
        max_size     = 8
        min_size     = 0
      }
      update_config = {
        max_unavailable_percentage = 50
      }
      disk_size = 100
      ami_type  = "AL2_x86_64"
      labels = {
        "node-type" = "compute"
      }
      taints = [
        {
          key    = "compute-intensive"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }
}

# Database Configuration
variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "15.4"
}

variable "postgres_instance_class" {
  description = "RDS instance class for PostgreSQL"
  type        = string
  default     = "db.r6g.large"
}

variable "postgres_allocated_storage" {
  description = "Initial allocated storage for PostgreSQL (GB)"
  type        = number
  default     = 100
}

variable "postgres_max_allocated_storage" {
  description = "Maximum allocated storage for PostgreSQL (GB)"
  type        = number
  default     = 1000
}

variable "postgres_db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "claude_agents"
}

variable "postgres_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "claude"
}

variable "postgres_backup_retention" {
  description = "PostgreSQL backup retention period (days)"
  type        = number
  default     = 7
}

variable "postgres_backup_window" {
  description = "PostgreSQL backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "postgres_maintenance_window" {
  description = "PostgreSQL maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# Redis Configuration
variable "redis_version" {
  description = "Redis engine version"
  type        = string
  default     = "7.0"
}

variable "redis_node_type" {
  description = "ElastiCache node type for Redis"
  type        = string
  default     = "cache.r6g.large"
}

variable "redis_num_nodes" {
  description = "Number of Redis cache nodes"
  type        = number
  default     = 1
}

variable "redis_backup_retention" {
  description = "Redis snapshot retention period (days)"
  type        = number
  default     = 5
}

variable "redis_backup_window" {
  description = "Redis backup window"
  type        = string
  default     = "05:00-07:00"
}

variable "redis_maintenance_window" {
  description = "Redis maintenance window"
  type        = string
  default     = "sun:07:00-sun:09:00"
}

# Monitoring Configuration
variable "cloudwatch_log_retention" {
  description = "CloudWatch logs retention in days"
  type        = number
  default     = 30
}

variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

# Load Balancer Configuration
variable "alb_access_logs_retention_days" {
  description = "ALB access logs retention in days"
  type        = number
  default     = 30
}

# Domain Configuration
variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "claude-agents.local"
}

variable "create_route53_zone" {
  description = "Create Route53 hosted zone"
  type        = bool
  default     = false
}

# Security Configuration
variable "enable_waf" {
  description = "Enable AWS WAF for the ALB"
  type        = bool
  default     = true
}

variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the application"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

# Backup and Disaster Recovery
variable "enable_cross_region_backup" {
  description = "Enable cross-region backup for RDS"
  type        = bool
  default     = false
}

variable "backup_region" {
  description = "AWS region for cross-region backups"
  type        = string
  default     = "us-east-1"
}

# Cost Optimization
variable "enable_spot_instances" {
  description = "Enable spot instances for cost optimization"
  type        = bool
  default     = true
}

variable "auto_scaling_target_capacity" {
  description = "Target capacity percentage for auto scaling"
  type        = number
  default     = 80
}

# Feature Flags
variable "enable_service_mesh" {
  description = "Enable Istio service mesh"
  type        = bool
  default     = false
}

variable "enable_gitops" {
  description = "Enable ArgoCD for GitOps"
  type        = bool
  default     = true
}

variable "enable_chaos_engineering" {
  description = "Enable Chaos Engineering tools"
  type        = bool
  default     = false
}

variable "enable_policy_engine" {
  description = "Enable Open Policy Agent"
  type        = bool
  default     = true
}

# Environment-specific overrides
variable "env_config" {
  description = "Environment-specific configuration overrides"
  type = map(object({
    postgres_instance_class     = string
    redis_node_type            = string
    node_group_instance_types  = list(string)
    enable_multi_az           = bool
    backup_retention_days     = number
    monitoring_level          = string
  }))
  default = {
    development = {
      postgres_instance_class    = "db.t3.micro"
      redis_node_type           = "cache.t3.micro"
      node_group_instance_types = ["t3.medium"]
      enable_multi_az          = false
      backup_retention_days    = 1
      monitoring_level         = "basic"
    }
    staging = {
      postgres_instance_class    = "db.r6g.large"
      redis_node_type           = "cache.r6g.large"
      node_group_instance_types = ["m5.large", "m5a.large"]
      enable_multi_az          = true
      backup_retention_days    = 7
      monitoring_level         = "enhanced"
    }
    production = {
      postgres_instance_class    = "db.r6g.xlarge"
      redis_node_type           = "cache.r6g.xlarge"
      node_group_instance_types = ["m5.xlarge", "m5a.xlarge", "c5.xlarge"]
      enable_multi_az          = true
      backup_retention_days    = 30
      monitoring_level         = "advanced"
    }
  }
}