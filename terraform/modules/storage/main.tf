resource "azurerm_storage_account" "storage_account" {
  name                     = var.name
  resource_group_name      = var.resource_group_name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  allow_nested_items_to_be_public = true
}

resource "azurerm_storage_container" "storage_container" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.storage_account.name
  container_access_type = "blob"
}

resource "azurerm_storage_container" "to-do" {
  name                  = var.to_do_container_name
  storage_account_name  = azurerm_storage_account.storage_account.name
  container_access_type = "blob"
}

resource "azurerm_storage_share" "storage_share" {
  name                 = var.share_name
  storage_account_name = azurerm_storage_account.storage_account.name
  quota                = 5
}