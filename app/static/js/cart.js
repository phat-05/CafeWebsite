function toggleAddItemToCart(data, max_of_items) {
    let incBtn = document.getElementsByClassName("inc-item")
    if (data.total_quantity >= parseInt(max_of_items)) {
        for (let btn of incBtn)
            btn.classList.add("disabled")
    } else {
        for (let btn of incBtn)
            btn.classList.remove("disabled")
    }
}

function updateCartCounter(data) {
    let counters = document.getElementsByClassName("cart-counter")
    for (let element of counters)
        element.innerText = data.total_quantity;
}

function updateCartInfo(data) {
    let subs = document.getElementsByClassName("cart-sub")
    for (let element of subs) {
        element.innerText = data.subtotal.toLocaleString('en-US') + ' VNĐ'
    }

    let ser_fee = document.getElementsByClassName("cart-ser-fee")
    for (let element of ser_fee) {
        element.innerText = data.service_fee.toLocaleString('en-US') + ' VNĐ'
    }

    let totals = document.getElementsByClassName("cart-total")
    for (let element of totals) {
        element.innerText = data.total_price.toLocaleString('en-US') + ' VNĐ'
    }

    updateCartCounter(data)
}

function MyCustomAlert(message) {
    let alert = document.getElementById('custom-alert')
    alert.classList.remove('d-none')
    let alert_body = document.getElementById('alert-body')
    alert_body.innerText = message
}

function addToCart(id, name, image, price) {
    fetch('/api/carts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "id": id,
            "name": name,
            "image": image,
            "price": price
        })
    }).then(res => res.json()).then(data => {
        if (data.message) {
            MyCustomAlert(data.message)
        } else {
            updateCartCounter(data)
        }
    })
}

function updateCart(id, change) {
    let qtyElement = document.getElementById(`qty-${id}`)
    let qty = parseInt(qtyElement.innerText)
    let newQty = qty + change

    fetch(`/api/carts/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            "quantity": newQty,
        })
    }).then(res => res.json()).then(data => {
        qtyElement.innerText = newQty;

        if (parseInt(qtyElement.innerText) <= 1) {
            document.getElementById(`reduce-qty-${id}`).classList.add("disabled")
        } else {
            document.getElementById(`reduce-qty-${id}`).classList.remove("disabled")
        }

        let price = document.getElementById(`prod-${id}-price`).innerText
        document.getElementById(`price-${id}`).innerText = (parseFloat(newQty) * parseFloat(price) * 1000)
            .toLocaleString('en-US') + ' VNĐ'

        toggleAddItemToCart(data = data, 10)
        updateCartInfo(data)
    })
}


function deleteCart(id) {
    const modalElement = document.getElementById(`removeItem-${id}`);

    // Lấy instance (đối tượng điều khiển) của Modal từ Bootstrap
    const modalInstance = bootstrap.Modal.getInstance(modalElement);
    if (modalInstance) {
        modalInstance.hide();
    }
    fetch(`/api/carts/${id}`, {
        method: 'DELETE',
    }).then(res => res.json()).then(data => {
        if (data.flag) {
            location.reload()
        }

        document.getElementById(`prod-${id}`).remove()

        toggleAddItemToCart(data = data, 10)
        updateCartInfo(data)
    })
}

function addNote(id, obj) {
    let note = obj.value
    fetch(`/api/carts/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'note': note,
        })
    }).then(res => res.json()).then(data => {})
}

function order() {
    fetch("/api/order", {
        method: 'POST'
    }).then(res => res.json()).then(data => {
        MyCustomAlert(data.message)
        location.reload()
    })
}