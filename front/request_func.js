function request(adr, func) {
    let xhr = new XMLHttpRequest()
    xhr.open("GET", adr, true)
    xhr.onload = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            func(xhr.responseText)
        } else {
            console.error("request error: adr - " + adr + ", status - " + xhr.status + ", readyState - " + xhr.readyState)
            console.error(xhr)
        }
    }
    xhr.send()
}