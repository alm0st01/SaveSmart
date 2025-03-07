document.addEventListener('DOMContentLoaded', function () {
            
        
    const form = document.getElementById('login-form');
    form.addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
});

eel.login(data.email, data.password, true)(function(response) {
    if (response && response.success) {
        const expire_date = new Date();
        expire_date.setTime(expire_date.getTime() + (2*60*60*1000)); // 2 hours
        const expString = expire_date.toUTCString();

        // Store unencrypted values in cookies
        const values = response.values;
        document.cookie = `username=${values.username}; expires=${expString}; path=/`;
        document.cookie = `fname=${values.fname}; expires=${expString}; path=/`;
        document.cookie = `lname=${values.lname}; expires=${expString}; path=/`;
        document.cookie = `email=${values.email}; expires=${expString}; path=/`;
        document.cookie = `password=${values.password}; expires=${expString}; path=/`;

        alert("Login successful!")
        window.location.href = 'account/banking/index.html'
    } else {
        alert("Username or password is incorrect");
    }
});

});
});