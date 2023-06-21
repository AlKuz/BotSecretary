output "vpc" {
  value = {
    id = module.vpc.vpc_id
  }
}


output "sg" {
  value = {
    telegram  = module.telegram-sg.security_group_id
    bot-logic = module.bot-logic-sg.security_group_id
    database  = module.database-sg.security_group_id
  }
}