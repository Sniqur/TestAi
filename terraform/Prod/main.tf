provider "azurerm" {
  features {}
  subscription_id = var.SUBSCRIPTION_ID
  client_id       = var.CLIENT_ID
  client_secret   = var.CLIENT_SECRET
  tenant_id       = var.TENANT_ID
}

module "resource_group" {
  source   = "../modules/resource_group"
  name     = "PDF-Processing-RG-TF-prod"
  location = "East US2"
}

module "storage" {
  source              = "../modules/storage"
  name                = "pdfstorageaccprocprod"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  container_name      = "json-storage-prod"
  share_name          = "pdf-storage-prod"
  to_do_container_name ="to-do"

}

module "service_plan" {
  source              = "../modules/service_plan"
  name                = "function-plan-pdfprocprod"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
}

module "cognitive_account" {
  source              = "../modules/cognitive_account"
  name                = "pdfProcIntelljsonprod"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  
}

module "function_app" {
  source                   = "../modules/function_app"
  name                     = "funcapp-pdf-proc-prod"
  location                 = module.resource_group.location
  resource_group_name      = module.resource_group.name
  service_plan_id          = module.service_plan.service_plan_id
  storage_account_name     = module.storage.storage_account_name
  storage_account_access_key = module.storage.primary_access_key

  app_settings = {
    "AZURE_STORAGE_CONNECTION_STRING" = module.storage.primary_connection_string
    "AzureWebJobsStorage"             = module.storage.primary_connection_string
    "BLOB_CONTAINER_NAME"             = module.storage.container_name
    "FORM_RECOGNIZER_ENDPOINT"        = module.cognitive_account.endpoint
    "FORM_RECOGNIZER_KEY"             = module.cognitive_account.primary_access_key
    "SHARE_NAME"                      = module.storage.share_name
    "TODO_CONTAINER"                  = module.storage.to-do-container_name
    "TELEGRAM_BOT_TOKEN"              = var.TELEGRAM_BOT_TOKEN
    "TELEGRAM_CHAT_ID"                = var.TELEGRAM_CHAT_ID
    "DISCORD_WEBHOOK_URL"             = var.DISCORD_WEBHOOK_URL
    "WEBSITE_ENABLE_SYNC_UPDATE_SITE" = "true"
  }
}
