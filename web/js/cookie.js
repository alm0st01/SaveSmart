export function getCookie(attr) {
    let temp = document.cookie.split(';').map(cookie => cookie.split('='));
    var cookies = temp.reduce((accumulator, [key, value]) =>
    ({ ...accumulator, [key.trim()]: decodeURIComponent(value)}),
    {});
    return cookies[attr]
}

export function logout(){
    const expString = new Date(0).toUTCString;
    document.cookie = `username=; expires=${expString}; path=/`;
    document.cookie = `fname=; expires=${expString}; path=/`;
    document.cookie = `lname=; expires=${expString}; path=/`;
    document.cookie = `email=; expires=${expString}; path=/`;
    document.cookie = `password=; expires=${expString}; path=/`;

    eel.print_text("hey");

    window.location.href='index.html';
}

window.logout = logout;

eel.expose(getCookie, 'get_cookie')