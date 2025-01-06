resource "azurerm_cognitive_account" "cognitive_account" {
  name                = var.name
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "CognitiveServices"
  sku_name            = "S0"
  
  
}