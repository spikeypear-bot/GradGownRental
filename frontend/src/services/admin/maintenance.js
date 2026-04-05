import { fetchOrdersByStatus } from './helpers'

const STORAGE_KEY = 'admin-maintenance-stages'
const DETAILS_KEY = 'admin-maintenance-details'

export function readStageMap() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')
  } catch {
    return {}
  }
}

export function writeStageMap(stageMap) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stageMap))
}

export function readMaintenanceDetails() {
  try {
    return JSON.parse(localStorage.getItem(DETAILS_KEY) || '{}')
  } catch {
    return {}
  }
}

export function writeMaintenanceDetails(detailsMap) {
  localStorage.setItem(DETAILS_KEY, JSON.stringify(detailsMap))
}

// Fetch item details from inventory service
async function fetchItemDetails(modelId) {
  try {
    const inventoryUrl = import.meta.env.VITE_INVENTORY_API_BASE_URL || 'http://localhost:8080'
    const response = await fetch(`${inventoryUrl}/api/inventory/models/${modelId}`)
    if (response.ok) {
      const result = await response.json()
      // Extract the data object and flatten it with style info
      if (result.data) {
        return {
          modelId: result.data.modelId,
          itemName: result.data.style?.itemName || 'Unknown Item',
          itemType: result.data.style?.itemType || 'Gown',
          size: result.data.size || 'Unknown Size',
          totalQty: result.data.totalQty
        }
      }
    } else {
      console.warn(`Inventory API returned status ${response.status} for model ${modelId}`)
    }
  } catch (error) {
    console.warn(`Failed to fetch item details for ${modelId}:`, error)
  }
  // Fallback - at least preserve the modelId
  return {
    modelId,
    itemName: 'Unknown Item',
    itemType: 'Gown',
    size: 'Unknown Size',
    totalQty: 0
  }
}

function buildQueueId(orderId, subsetKey, stage) {
  return `${orderId}:${subsetKey}:${stage}`
}

export function mapOrderToMaintenanceItem(order, stage, selectedPackages = [], subsetKey = stage, itemDetailsMap = {}) {
  // For Repair/Laundry queues, we need to return an array of items (one per selected package)
  // selectedPackages should contain {modelId, qty, size?, itemName?, itemType?, ...}
  // itemDetailsMap is a map of modelId -> {modelId, itemName, itemType, size, totalQty}
  // Prefer fields from selectedPackages if available (e.g., size stored in order)
  
  return selectedPackages.map((pkg, idx) => {
    // Extract modelId - could be a string (older format) or an object (newer format)
    const modelId = typeof pkg === 'string' ? pkg : (pkg.modelId || '')
    const details = itemDetailsMap[modelId] || {}
    
    // Prefer size from package (stored in order), fallback to inventory details, then unknown
    const size = pkg.size || details.size || 'Unknown Size'
    const itemName = pkg.itemName || details.itemName || 'Unknown Item'
    const itemType = pkg.itemType || details.itemType || 'Gown'
    
    return {
      id: buildQueueId(order.orderID, modelId, stage),
      orderId: order.orderID,
      modelId: modelId,
      itemName: itemName,
      itemType: itemType,
      size: size,
      qty: (pkg.qty || 1),
      stage: stage,
      dateAdded: order.returned_at || order.updated_at || new Date().toISOString(),
      subsetKey
    }
  })
}

export async function loadMaintenanceBuckets(orderApiUrl) {
  const [returnedOrders, damagedOrders] = await Promise.all([
    fetchOrdersByStatus(orderApiUrl, 'RETURNED'),
    fetchOrdersByStatus(orderApiUrl, 'RETURNED_DAMAGED')
  ])

  // Collect all unique modelIds to fetch details
  const allModelIds = new Set()
  ;[...returnedOrders, ...damagedOrders].forEach(order => {
    (order.selected_items || []).forEach(item => {
      allModelIds.add(item.modelId)
    })
    ;(order.damaged_items || []).forEach(item => {
      allModelIds.add(item.modelId || item)
    })
  })

  // Fetch all item details in parallel
  const itemDetailsMap = {}
  await Promise.all(
    Array.from(allModelIds).map(async (modelId) => {
      const details = await fetchItemDetails(modelId)
      // Always add details to map (fetchItemDetails now always returns an object)
      itemDetailsMap[modelId] = details
    })
  )

  // Build repair queue from RETURNED_DAMAGED orders
  const repairQueue = damagedOrders.flatMap(order => {
    const damagedItems = order.damaged_items || []
    if (!damagedItems.length) return []
    
    // Enrich damaged_items with data from selected_items (which has size, itemName, etc.)
    const selectedItemsMap = {}
    ;(order.selected_items || []).forEach(item => {
      selectedItemsMap[item.modelId] = item
    })
    
    // Merge damaged_items with their enriched data from selected_items
    const enrichedDamagedItems = damagedItems.map(damagedItem => {
      const selectedItem = selectedItemsMap[damagedItem.modelId] || {}
      return {
        ...damagedItem,
        size: selectedItem.size,
        itemName: selectedItem.itemName,
        itemType: selectedItem.itemType
      }
    })
    
    return mapOrderToMaintenanceItem(order, 'repair', enrichedDamagedItems, 'damaged', itemDetailsMap)
  })

  // Build wash queue from RETURNED orders (items that weren't damaged)
  const washQueue = returnedOrders.flatMap(order => {
    const selectedItems = order.selected_items || []
    if (!selectedItems.length) return []
    
    return mapOrderToMaintenanceItem(order, 'wash', selectedItems, 'clean', itemDetailsMap)
  })

  return {
    repairQueue,
    washQueue,
    completedQueue: []
  }
}
