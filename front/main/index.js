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

//------------------------------------------------------------------------------------------------------------------------------------------------

const NO_SELECTED_CHAT_COLOR = 'rgb(0, 0, 0, 0.03)'
const MOUSEOVER_CHAT_COLOR = 'rgb(0, 0, 0, 0.15)'
const SELECTED_CHAT_COLOR = 'rgb(0, 160, 0, 0.3)'
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

let num_chats = 50
for (let i = 0; i < num_chats; i++) {
    last_message = "Lol kek cheburek kek lol Ya crytoy nevyrayatno crytoy, Yefr erfers, Ya super cryt"
    let html = `
        <div class="chat_button"> 
            <div id="onmouse_div_${i}" class="onmouse_div" onmouseover="mouse_over(${i})" onmouseout="mouse_out(${i})" onclick="select_chat(${i})"> 
                <div class="ico_container"> 
                    <img src=/front/main/ico_${Math.floor(Math.random() * 2)}.png class="chat_ico"> 
                    <div id="chat_text_box_${i}" class="chat_button_text_box"> <nobr><b>Name</b> <br>${last_message}</nobr></div>
                </div>
                
            </div>
            <div class="chat_button"">
        </div>
    `
    document.getElementById("chats_container").innerHTML += html
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
    elem.style.borderRadius = "12px 0px 0px 12px"
}