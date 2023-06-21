data "aws_availability_zones" "available" {}

module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "${var.namespace}-vpc"
  cidr = "10.0.0.0/16"

  azs              = data.aws_availability_zones.available.names
  private_subnets  = ["10.0.11.0/24", "10.0.12.0/24"]
  database_subnets = ["10.0.21.0/24"]

  create_database_subnet_group = true
  enable_nat_gateway           = false
  enable_vpn_gateway           = false

  tags = {
    terraform   = "true"
    environment = "dev"
  }
}

module "telegram-sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.namespace}-telegram-sg"
  description = "Security group for Telegram bot service"
  vpc_id      = module.vpc.vpc_id
}


module "bot-logic-sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.namespace}-bot-logic-sg"
  description = "Security group for the chatbot internal logic"
  vpc_id      = module.vpc.vpc_id

  computed_ingress_with_self = [{
    rule                     = "all-all"
    source_security_group_id = module.telegram-sg.security_group_id
    self                     = false
  }]
}


module "database-sg" {
  source = "terraform-aws-modules/security-group/aws"

  name        = "${var.namespace}-database-sg"
  description = "Security group for PostgreSQL database"
  vpc_id      = module.vpc.vpc_id

  computed_ingress_with_self = [{
    rule                     = "postgresql-tcp"
    source_security_group_id = module.bot-logic-sg.security_group_id
    self                     = false
  }]
}
