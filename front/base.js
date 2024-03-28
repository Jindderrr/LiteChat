function request(adr, func=function(response){console.log(response)}) {
    let xhr = new XMLHttpRequest()
    xhr.open("GET", adr, true)
    xhr.onload = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            func(JSON.parse(xhr.responseText))
        } else {
            console.error("request error: adr - " + adr + ", status - " + xhr.status + ", readyState - " + xhr.readyState)
            console.error(xhr)
        }
    }
    xhr.send()
}

function setCookie(name, value, days) {
    let expires = ""
    if (days) {
        let date = new Date()
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
        expires = "; expires=" + date.toUTCString()
    }
    document.cookie = name + "=" + value + expires + "; path=/"
    updateCookieVar()
}

function getCookie(name) {
    let nameEQ = name + "="
    let cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i]
        while (cookie.charAt(0) === ' ') {
            cookie = cookie.substring(1, cookie.length)
        } if (cookie.indexOf(nameEQ) === 0) {
            return cookie.substring(nameEQ.length, cookie.length)
        }
    }
    updateCookieVar()
}

var cookies
function updateCookieVar() {
    cookies = {}
    document.cookie.split(';').forEach(cookie => {
        let [name, value] = cookie.trim().split('=')
        cookies[name] = decodeURIComponent(value)
    })
}
updateCookieVar()
const THEMES_CLASSES = ["beige-ping-theme", "dark-theme", "light-theme", "purple-theme", "green-theme", "blue-theme"]
const NFONS = 5
function setRandomTheme() {
    setCookie("theme", Math.floor(Math.random() * THEMES_CLASSES.length))
    setCookie("nfon", Math.floor(Math.random() * NFONS))
}
