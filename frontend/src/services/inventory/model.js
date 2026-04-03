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

  // Helper to get all styles as array — handles both flat { itemName } and { inventoryStyle: { itemName } } shapes
  getStyles() {
    return [this.hatStyle, this.hoodStyle, this.gownStyle]
      .filter(s => s)
      .map(s => s.inventoryStyle || s)
  }
}

export class DetailedPackage {
  constructor(data) {
    this.packageId = data.packageId
    this.institution = data.institution
    this.educationLevel = data.educationLevel
    this.faculty = data.faculty
    // Each style bucket: { inventoryStyle: { styleId, itemName, itemType, rentalFee, deposit }, models: [{ modelId, size, totalQty }] }
    this.hatStyle = data.hatStyle || null
    this.hoodStyle = data.hoodStyle || null
    this.gownStyle = data.gownStyle || null
    this.totalDeposit = Number(data.totalDeposit || 0)
    this.totalRentalFee = Number(data.totalRentalFee || 0)
    this.totalPrice = Number(data.totalPrice || 0)
  }

  // Returns array of style buckets with { inventoryStyle, models[] }
  getStyleBuckets() {
    return [this.hatStyle, this.hoodStyle, this.gownStyle].filter(Boolean)
  }

  // Returns per-item size options: [{ itemType, itemName, models: [{ modelId, size, totalQty }] }, ...]
  getItemSizeOptions() {
    return this.getStyleBuckets().map(bucket => ({
      itemType: bucket.inventoryStyle?.itemType,
      itemName: bucket.inventoryStyle?.itemName,
      models: (bucket.models || []).map(m => ({
        modelId: m.modelId,
        size: String(m.size || '').toUpperCase(),
        totalQty: m.totalQty
      }))
    }))
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
    // Soft-hold duration is currently 10 minutes from creation
    this.expiresAt = data.expiresAt || null
  }
}

export class AvailabilityResponse {
  constructor(data) {
    this.date = data.date
    this.totalAvailable = data.totalAvailable
    // components: [{ inventoryDto: { modelId, size, totalQty }, availableQty }]
    this.components = (data.components || []).map(c => ({
      modelId: c.inventoryDto?.modelId,
      size: String(c.inventoryDto?.size || '').toUpperCase(),
      totalQty: c.inventoryDto?.totalQty,
      availableQty: c.availableQty
    }))
  }

  // Returns a Set of sizes that have availableQty > 0
  getAvailableSizes() {
    return new Set(
      this.components.filter(c => c.availableQty > 0).map(c => c.size)
    )
  }

  // Returns available qty for a specific modelId
  getAvailableQtyForModel(modelId) {
    return this.components.find(c => c.modelId === modelId)?.availableQty ?? 0
  }
}

export class Availability90Response {
  constructor(data) {
    this.modelId = data.modelId
    this.availability = data.availability // Array of daily availability
  }
}