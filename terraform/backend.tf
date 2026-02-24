terraform {
  backend "s3" {
    bucket         = "k8s-platform-aws-tfstate"
    key            = "terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "k8s-platform-aws-tflock"
    encrypt        = true
  }
}
