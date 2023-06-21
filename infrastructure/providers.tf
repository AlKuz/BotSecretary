provider "aws" {
  region  = var.region
  profile = "terraform-experiments"
  shared_credentials_files = [
    "%USERPROFILE%/.aws/config"
  ]
}
