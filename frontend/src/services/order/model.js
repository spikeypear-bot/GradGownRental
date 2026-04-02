export class OrderRecord {
  constructor(data) {
    this.id = data.id
    this.orderId = data.order_id
    this.studentName = data.student_name
    this.email = data.email
    this.phone = data.phone
    this.packageId = data.package_id
    this.selectedItems = data.selected_items || []
    this.rentalStartDate = data.rental_start_date
    this.rentalEndDate = data.rental_end_date
    this.totalAmount = Number(data.total_amount || 0)
    this.deposit = Number(data.deposit || 0)
    this.fulfillmentMethod = data.fulfillment_method
    this.status = data.status
    this.paymentId = data.payment_id || null
    this.holdId = data.hold_id || null
  }
}
