// я крутой

const ok_color = [15, 210, 70]
const no_color = [255, 128, 40]
const allElemsNames = ["email-username_input", "password_input"]
const allElems = new Array
for (let elem of allElemsNames) {
    allElems.push(document.getElementById(elem))
}
let valides = new Array
let currentColor = [no_color, no_color]
let av = true

function changeColor() {
    valides = new Array
    for (let elem_name of allElemsNames){
        let valid = false
        let elem = document.getElementById(elem_name)
        if (elem_name == "email-username_input") {
            valid = elem.value.length > 0
        } if (elem_name == "password_input") {
            valid = elem.value.length > 0
        }
        valides.push(valid)
    }
    for (let n = 0; n < valides.length; n++) {
        let elem = allElems[n]
        if (valides[n]) {
            elem.classList.remove("invalid_border")
            elem.classList.add("valid_border")
        } else {
            elem.classList.remove("valid_border")
            elem.classList.add("invalid_border")
        }
    }
    av = true
    for (let x of valides) {
        if (!x) {av = false}
    }
    let button = document.getElementById("send_button")
    let container = document.getElementById("container")
    if (av) {
        container.classList.remove("invalid_container")
        container.classList.add("valid_container")
        button.classList.remove("invalid_button")
        button.classList.add("valid_button")
    } else {
        container.classList.remove("valid_container")
        container.classList.add("invalid_container")
        button.classList.remove("valid_button")
        button.classList.add("invalid_button")
    }
}

setInterval(changeColor, 50)

function send() {
    if (av) {
        let email = document.getElementById("email-username_input").value
        let password = document.getElementById("password_input").value
        request(`/request/login?email-username=${email}&password=${password}`, function(response) {
            console.log(response)
            if (response["response"]) {
                setCookie("email", response["email"], 30)
                setCookie("username", response["username"], 30)
                setCookie("name", response["name"], 30)
                setCookie("password_hash", response["hash"], 30)
                window.location.assign("./")
            }
        })
    }
}