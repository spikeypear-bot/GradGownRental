// Inventory Service Models
// Defines data structures for inventory-related API responses

export class GraduationPackage {
  constructor(data, summary = {}) {
    this.packageId = data.packageId
    this.institution = data.institution
    this.educationLevel = data.educationLevel
    this.faculty = data.faculty
    this.hatStyle = data.hatStyle // { styleId, itemName, itemType, rentalFee, deposit }
    this.hoodStyle = data.hoodStyle
    this.gownStyle = data.gownStyle
    // Summary fields from parent response
    this.totalDeposit = summary.totalDeposit || 0
    this.totalRentalFee = summary.totalRentalFee || 0
    this.totalPrice = summary.totalPrice || 0
  }

  // Helper method to get display name for the package
  getDisplayName() {
    return `${this.institution} - ${this.educationLevel} (${this.faculty})`
  }

  // Helper to get all styles as array
  getStyles() {
    return [this.hatStyle, this.hoodStyle, this.gownStyle].filter(s => s)
  }
}

export class Inventory {
  constructor(data) {
    this.modelId = data.modelId
    this.style = data.style
    this.size = data.size
    this.totalQuantity = data.totalQuantity
    this.description = data.description
  }
}

export class InventoryStyle {
  constructor(data) {
    this.styleId = data.styleId
    this.styleName = data.styleName
    this.rentalFee = data.rentalFee
    this.depositFee = data.depositFee
    this.description = data.description
  }
}

export class ItemHold {
  constructor(data) {
    this.holdId = data.holdId
    this.items = data.items // Array of { modelId, qty, chosenDate }
    this.createdAt = data.createdAt
    this.expiresAt = data.expiresAt
  }
}

export class AvailabilityResponse {
  constructor(data) {
    this.date = data.date
    this.totalAvailable = data.totalAvailable
    this.components = data.components // { hat, hood, gown }
  }
}

export class Availability90Response {
  constructor(data) {
    this.modelId = data.modelId
    this.availability = data.availability // Array of daily availability
  }
}
