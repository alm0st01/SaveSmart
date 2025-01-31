document.addEventListener('DOMContentLoaded', function () {
            
        
    const form = document.getElementById('signup-form');
    form.addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
});

eel.signup(data.username, data.fname, data.lname, data.email, data.password)(function(ret_value) {
    if (ret_value == 1) {

        const expire_date = new Date();
        expire_date.setTime(expire_date.getTime() + (2*60*60*1000));
        const expString = expire_date.toUTCString();

        document.cookie = `username=${data.username}; expires=${expString}; path=/`;
        document.cookie = `fname=${data.fname}; expires=${expString}; path=/`;
        document.cookie = `lname=${data.lname}; expires=${expString}; path=/`;
        document.cookie = `email=${data.email}; expires=${expString}; path=/`;
        document.cookie = `password=${data.password}; expires=${expString}; path=/`;

        alert("Signup successful!")
        window.location.href = 'account/banking/index.html'
    } else {
        alert("Username or email taken. Please enter a new username or email.");
    }
});
});
});