let LAST_MSG_ID = 0
let IS_VERTICAL_MODE = false


let WS = new WebSocket("ws://127.0.0.1:5000");

WS.onopen = function() {
    WS.send(JSON.stringify({"username": cookies["username"], "password_hash": cookies["password_hash"]}))
}

WS.onmessage = function(event) {
    console.log("с сервера: " + event.data)
}

// chats_menu
let chats = []
request(`/request/get_my_chats?username=${cookies["username"]}&password_hash=${cookies["password_hash"]}`, function(response) {
    chats = response
    UpdateChats()
})

//message placeholder

const place_holder_text = "message.."
function autoResize() {
    const textarea = document.getElementById('message_textarea')
    textarea.style.height = 'auto'
    document.getElementById("chat_text_input_container").style.height = textarea.scrollHeight + 30 + 'px'
    textarea.style.height = textarea.scrollHeight + 0 + 'px'
}
autoResize()

function printPlaceholder() {
    let elem = document.getElementById("message_textarea")
    let ct = elem.placeholder
    let nt = place_holder_text
    let et = ""
    for (let i = 0; i < ct.length + 1; i++) {
        et += nt[i]
    }
    elem.placeholder =  et
    if (et != place_holder_text) { setTimeout(printPlaceholder, Math.random() * 200 + 20 ) }
}
setTimeout(printPlaceholder, 300)

//chats

const NO_SELECTED_CHAT_COLOR = 'rgb(0, 0, 0, 0.03)'
const MOUSEOVER_CHAT_COLOR = 'rgb(0, 0, 0, 0.12)'
const SELECTED_CHAT_COLOR = 'rgb(110, 90, 80, 0.3)'
let SelectedChat = -1

function mouse_over(id) {
    if (id != SelectedChat) {
        document.getElementById("onmouse_div_" + id).style.backgroundColor = MOUSEOVER_CHAT_COLOR
    }
}
function mouse_out(id) {
    if (id != SelectedChat) {
        document.getElementById("onmouse_div_" + id).style.backgroundColor = NO_SELECTED_CHAT_COLOR
    }
}

function UpdateChats() {
    for (let i = 0; i < chats.length; i++) {
        let html = `
            <div id="onmouse_div_${i}" class="chat_button" onmouseover="mouse_over(${i})" onmouseout="mouse_out(${i})" onclick="select_chat(${i})"> 
                <div class="chat_button_text_container">
                    <img src=/front/main/ico_${Math.floor(Math.random() * 2)}.png class="chat_ico"> 
                    <div id="chat_name_text_box_${i}" class="chat_button_text_box"> <nobr><b>${chats[i]["chat_name"]}</b><br>${chats[i]["chat_last_message"]["message_text"]}</nobr></div>
                    <div id="chat_text_box__${i}" class="chat_button_time_box"> <i> ${chats[i]["chat_last_message"]["message_date"]} </i> </div>
                </div>
            </div>
        `
        document.getElementById("chats_container").innerHTML += html
    }
}

function resize_chat_text_box() {
    for (let i = 0; i < num_chats; i++) {
        document.getElementById("chat_text_box_" + i).style.width = 100 + "px"
    }
}

function select_chat(i) {
    if (SelectedChat != -1) {
        let elem = document.getElementById("onmouse_div_" + SelectedChat)
        elem.style.backgroundColor = NO_SELECTED_CHAT_COLOR
        elem.style.borderRadius = "12px"

    }
    SelectedChat = i
    elem = document.getElementById("onmouse_div_" + i)
    elem.style.backgroundColor = SELECTED_CHAT_COLOR
    document.getElementById("top_text").innerHTML = "<b>" + chats[SelectedChat]["chat_name"] + "</b>"
    WS.send(JSON.stringify({"type": "change_chat", "args": {"selected_chat_id": chats[SelectedChat]["chat_id"]}}))
    //elem.style.borderRadius = "12px 0px 0px 12px"
}

//

function to_vertical_mode() {
    document.getElementById("left_panel_container").style.visibility = "hidden"
    document.getElementById("chats_container").style.visibility = "hidden"
    document.getElementById("chat_container").style.width = "100%"
    document.getElementById("chats_container_top").style.width = "100%"
    document.getElementById("chat_text_input_container").style.width = "92%"
}

function to_horizontal_mode() {
    document.getElementById("left_panel_container").style.visibility = "visible"
    document.getElementById("chats_container").style.visibility = "visible"
    document.getElementById("chat_container").style.width = "calc(100% - 35% - 50px)"
    document.getElementById("chats_container_top").style.width = "calc(100% - 35% - 50px)"
    document.getElementById("chat_text_input_container").style.width = "calc(92% - 35% - 50px)"
}

window.addEventListener('resize', function() {
    IS_VERTICAL_MODE = window.innerHeight / window.innerWidth > 1
    if (IS_VERTICAL_MODE) { to_vertical_mode() }
    else {to_horizontal_mode()}
})
if (window.innerHeight / window.innerWidth > 1) { to_vertical_mode() }
else {to_horizontal_mode()}

// кнопки левой панели

function newChat() {
    another_username = prompt("username?")
    request(`/request/start_chat?my_username=${cookies["username"]}&another_username=${another_username}`)
}


// отправка сообщения
function send_msg() {
    let msgText = document.getElementById("message_textarea").value
    document.getElementById("message_textarea").value = ""
    WS.send(JSON.stringify({"type": "send_msg", "args": {"msg_text": msgText, "chat_id": chats[SelectedChat]["chat_id"]}}))
    // request(`/request/send_msg?username=${cookies["username"]}&password_hash=${cookies["password_hash"]}&msg_text=${msgText}&chat_id=${chats[SelectedChat]["chat_id"]}`)
    autoResize()
    autoScroll()
}

function autoScroll() {
    let scrollingDiv = document.getElementById('chat_container');
    scrollingDiv.scrollTop = scrollingDiv.scrollHeight
}

function add_msg(msgText, whose_msg) {
    let html = `
        <div class="message_box" style="justify-content: ${["end", "start", "center"][whose_msg]};">
            <div class="${["my_message", "no_my_message", "notification_message"][whose_msg]}">
                ${msgText}
            </div>
        </div>
    `
    document.getElementById("message_container").innerHTML += html
}

// function get_updates() {
//     request(`/request/get_updates?username=${cookies["username"]}&password_hash=${cookies["password_hash"]}&current_chat_id=${chats[SelectedChat]["chat_id"]}&last_msg_id=${LAST_MSG_ID}&need_chats_updates=${!IS_VERTICAL_MODE}`, function(response) {

//     })
// }