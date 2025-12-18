def stats_cart(cart, configs=None):
    total_quantity, subtotal = 0, 0
    service_fee_rate = float(configs["SERVICE_FEE"]['value'] if configs else 0.05)

    if cart:
        for item in cart.values():
            total_quantity += item["quantity"]
            subtotal += float(item["price"]) * item["quantity"]

        service_fee = service_fee_rate * subtotal
        total_price = subtotal + service_fee

        return {
            "total_quantity": total_quantity,
            "subtotal": subtotal,
            "service_fee_rate": service_fee_rate * 100,
            "service_fee": service_fee,
            "total_price": total_price,
        }
