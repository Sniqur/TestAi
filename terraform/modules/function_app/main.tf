resource "azurerm_linux_function_app" "function_app" {
  name                       = var.name
  location                   = var.location
  resource_group_name        = var.resource_group_name
  service_plan_id            = var.service_plan_id
  storage_account_name       = var.storage_account_name
  storage_account_access_key = var.storage_account_access_key

  site_config {
    application_stack {
      python_version = "3.11"
    }
  }

  app_settings = var.app_settings

#   app_settings = {
#     "AZURE_STORAGE_CONNECTION_STRING" = module.storage.primary_connection_string
#     "AzureWebJobsStorage"             = module.storage.primary_connection_string
#     "BLOB_CONTAINER_NAME"             = module.storage.container_name
#     "FORM_RECOGNIZER_ENDPOINT"        = module.cognitive_account.endpoint
#     "FORM_RECOGNIZER_KEY"             = module.cognitive_account.primary_access_key
#     "SHARE_NAME"                      = module.storage.share_name
#     "WEBSITE_ENABLE_SYNC_UPDATE_SITE" = "true"
#   }
}