const ok_color = [15, 210, 70]
const no_color = [255, 128, 40]
const allElemsNames = ["email_input", "username_input", "name_input", "password_input", "agree_input"]
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
        if (elem_name == "email_input") {
            valid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(elem.value)
        } if (elem_name == "username_input") {
            valid = elem.value.length > 0 && !elem.value.includes("@")
        } if (elem_name == "name_input") {
            valid = elem.value.length > 0
        } if (elem_name == "password_input") {
            valid = elem.value.length > 0
        } if (elem_name == "agree_input") {
            valid = elem.checked
        }
        valides.push(valid)
    }
    for (let n = 0; n < valides.length; n++) {
        let elem = allElems[n]
        if (valides[n]) {
            if (allElems[n].type == "checkbox") {  }
            elem.classList.remove("invalid_input")
            elem.classList.add("valid_input")
        } else {
            elem.classList.remove("valid_input")
            elem.classList.add("invalid_input")
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
        let email = document.getElementById("email_input").value
        let username = document.getElementById("username_input").value
        let name = document.getElementById("name_input").value
        let password = document.getElementById("password_input").value
        request(`/request/registration/send_email?email=${email}&username=${username}`, function(response) {
            console.log(response)
            if (response["response"] == true) {
                code = prompt("code?")
                request(`/request/registration/check_code?email=${email}&name=${name}&password=${password}&code=${code}`, function(response2) {
                    console.log(response2["response"])
                    if (response2["response"]) {
                        setCookie("email", email)
                        setCookie("username", username)
                        setCookie("name", name)
                        setCookie("password_hash", response["hash"])
                        setRandomTheme()
                        window.location.assign("./")
                    }
                })
            }
        })
    }
}