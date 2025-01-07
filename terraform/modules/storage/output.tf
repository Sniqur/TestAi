output "storage_account_name" {
  value = azurerm_storage_account.storage_account.name
}

output "primary_access_key" {
  value = azurerm_storage_account.storage_account.primary_access_key
}

output "primary_connection_string" {
  value = azurerm_storage_account.storage_account.primary_connection_string
}

output "container_name" {
  value = azurerm_storage_container.storage_container.name
}

output "to-do-container_name" {
  value = azurerm_storage_container.to-do.name
}

output "share_name" {
  value = azurerm_storage_share.storage_share.name
}