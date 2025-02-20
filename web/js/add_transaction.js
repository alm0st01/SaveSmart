document.addEventListener('DOMContentLoaded', function () {
            
        
    const form = document.getElementById('add-transaction-form');
    form.addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
});

eel.add_transaction(data.transaction_type, data.amount, data.transaction_date, data.transaction_name, data.description)(function(ret_value) {
    if (ret_value) {
        alert("Success!")
        window.location.href = 'account/banking/index.html'
    } else {
        alert("Transaction Failed. Please try again.");
    }
});
});
});