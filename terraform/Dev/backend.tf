terraform {
required_providers {
  azurerm = {
    source = "hashicorp/azurerm"
    version = ">=3.0"
  }
}
required_version = "1.9.8"
  backend "azurerm" {
    resource_group_name  = "TF-PDF-test"
    storage_account_name = "tfpfdtest"
    container_name       = "tfpdftest-dev"
    key                  = "terraform.tfstate"
  }
}