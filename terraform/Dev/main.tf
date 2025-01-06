# provider "azurerm" {
#   features {}
#   subscription_id = "307f3351-f3f3-42f2-aa13-405cd075f673"
# }

# resource "azurerm_resource_group" "pdf_processing" {
#   name     = "pdfProcessing-RG-TFtest"
#   location = "East US2"
# }

# resource "azurerm_storage_account" "pdf_storage" {
#   name                     = "pdfstorageacctftest"
#   resource_group_name      = azurerm_resource_group.pdf_processing.name
#   location                 = azurerm_resource_group.pdf_processing.location
#   account_tier             = "Standard"
#   account_replication_type = "LRS"

#   allow_nested_items_to_be_public = true
# #   allow_cross_tenant_replication  = true  # True by default 
# }

# resource "azurerm_storage_container" "json_storage" {
#   name                  = "json-storage-dev"
# #   storage_account_id = azurerm_storage_account.pdf_storage.id
#   storage_account_name  = azurerm_storage_account.pdf_storage.name
#   container_access_type = "blob"
#   depends_on = [azurerm_storage_account.pdf_storage]

# }

# resource "azurerm_storage_share" "pdf_share" {
#   name                 = "pdf-storage-dev"
# #   storage_account_id = azurerm_storage_account.pdf_storage.id
#   storage_account_name = azurerm_storage_account.pdf_storage.name
#   quota = "5"
#   depends_on = [azurerm_storage_account.pdf_storage]

# }

# resource "azurerm_service_plan" "function_plan" {
#   name                = "function-plan-dev"
#   location            = azurerm_resource_group.pdf_processing.location
#   resource_group_name = azurerm_resource_group.pdf_processing.name
# #   kind                = "FunctionApp"
#   os_type             = "Linux"  # Specify Linux for Python Functions
#   sku_name            = "Y1"   
  
# }

# resource "azurerm_linux_function_app" "function_app" {
#   name                       = "funcapp-pdf-proc-dev"
#   location                   = azurerm_resource_group.pdf_processing.location
#   resource_group_name        = azurerm_resource_group.pdf_processing.name
#   service_plan_id            = azurerm_service_plan.function_plan.id
#   storage_account_name       = azurerm_storage_account.pdf_storage.name
#   storage_account_access_key = azurerm_storage_account.pdf_storage.primary_access_key

#   site_config {
#     application_stack {
#       python_version = "3.11"
#     }
#   }

#   app_settings = {
#     "AZURE_STORAGE_CONNECTION_STRING" = azurerm_storage_account.pdf_storage.primary_connection_string
#     "AzureWebJobsStorage"             = azurerm_storage_account.pdf_storage.primary_connection_string
#     "BLOB_CONTAINER_NAME"             = azurerm_storage_container.json_storage.name
#     "FORM_RECOGNIZER_ENDPOINT"        = azurerm_cognitive_account.pdf_processing_intelligence.endpoint
#     "FORM_RECOGNIZER_KEY"             = azurerm_cognitive_account.pdf_processing_intelligence.primary_access_key
#     "SHARE_NAME"                      = azurerm_storage_share.pdf_share.name
#     "WEBSITE_ENABLE_SYNC_UPDATE_SITE" = "true"
#   }
# }

# resource "azurerm_cognitive_account" "pdf_processing_intelligence" {
#   name                = "pdfProcessingIntelligence12"
#   location            = azurerm_resource_group.pdf_processing.location
#   resource_group_name = azurerm_resource_group.pdf_processing.name
#   kind                = "CognitiveServices"
#   sku_name            = "S0"
# }



provider "azurerm" {
  features {}
  subscription_id = "307f3351-f3f3-42f2-aa13-405cd075f673"
}

module "resource_group" {
  source   = "../modules/resource_group"
  name     = "PDF-Processing-RG-TF"
  location = "East US2"
}

module "storage" {
  source              = "../modules/storage"
  name                = "pdfstorageaccproc"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  container_name      = "json-storage-dev"
  share_name          = "pdf-storage-dev"
}

module "service_plan" {
  source              = "../modules/service_plan"
  name                = "function-plan-pdfproc"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
}

module "cognitive_account" {
  source              = "../modules/cognitive_account"
  name                = "pdfProcIntelljson"
  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  
}

module "function_app" {
  source                   = "../modules/function_app"
  name                     = "funcapp-pdf-proc-dev"
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
    # "TELEGRAM_BOT_TOKEN"              = var.TELEGRAM_BOT_TOKEN
    # "TELEGRAM_CHAT_ID"                = var.TELEGRAM_CHAT_ID
    # "DISCORD_WEBHOOK_URL"             = var.DISCORD_WEBHOOK_URL
    "WEBSITE_ENABLE_SYNC_UPDATE_SITE" = "true"
  }
}
