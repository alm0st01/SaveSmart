document.addEventListener('DOMContentLoaded', function () {
            
        
    const form = document.getElementById('login-form');
    form.addEventListener('submit', function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
});

eel.login(data.email, data.password, true)(function(ret_value) {
    if (ret_value != false) {

        const expire_date = new Date();
        expire_date.setTime(expire_date.getTime() + (2*60*60*1000)); // 2 hours
        const expString = expire_date.toUTCString();


        eel.getentrywithattr("email",data.email)(function(ret_array){
            eel.print_text(ret_array);
            eel.print_text(ret_array[0]);
            document.cookie = `username=${ret_array[1]}; expires=${expString}; path=/`;
            document.cookie = `fname=${ret_array[2]}; expires=${expString}; path=/`;
            document.cookie = `lname=${ret_array[3]}; expires=${expString}; path=/`;
            document.cookie = `email=${data.email}; expires=${expString}; path=/`;
            document.cookie = `password=${data.password}; expires=${expString}; path=/`;
        });

        alert("Login successful!")
        window.location.href = 'account/banking/index.html'
    } else {
        alert("Username or password is incorrect");
    }
});

});
});