export function getCookie(attr) {
    let temp = document.cookie.split(';').map(cookie => cookie.split('='));
    var cookies = temp.reduce((accumulator, [key, value]) =>
    ({ ...accumulator, [key.trim()]: decodeURIComponent(value)}),
    {});
    return cookies[attr]
}

eel.expose(getCookie, 'get_cookie')