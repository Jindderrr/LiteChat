if (cookies["password_hash"] == undefined) {
    window.location.href = "/login"
}

let IS_VERTICAL_MODE = false
if (getCookie("theme") == undefined) { setCookie("theme", 0) }
if (getCookie("nfon") == undefined) { setCookie("nfon", 0) }

let WS = new WebSocket("ws://127.0.0.1:5000")

WS.onopen = function() {
    WS.send(JSON.stringify({"username": cookies["username"], "password_hash": cookies["password_hash"]}))
}

WS.onmessage = function(event) {
    let data = JSON.parse(event.data)
    console.log(data)
    if (data["type"] == "change_chat_answer") {
        document.getElementById("message_container").innerHTML= ""
        LAST_MSG_INDEX = 0
        for (let msg of data["all_messages"]) {
            add_msg(msg["msg_text"], msg["msg_sender"], msg["msg_time"])
            console.log(msg["msg_text"])
        }
        scrollChatDown()
    } else if (data["type"] == "new_msg_in_your_chat") {
        add_msg(data["message"]["msg_text"], data["message"]["msg_sender"], data["message"]["msg_time"])
        scrollChatDown()
    }
}

function scrollChatDown() {
    document.getElementById("chat_container").scrollBy(0, document.getElementById("chat_container").scrollHeight)
}

// chats_menu
let chats = []
let known_users
request(`/request/get_my_chats?username=${cookies["username"]}&password_hash=${cookies["password_hash"]}`, function(response) {
    chats = response["chats_and_groups"]
    chats = chats.sort((a, b) => {
        console.log(a)
        a_d = new Date(a["chat_last_message"]["message_date"])
        b_d = new Date(b["chat_last_message"]["message_date"])
        console.log(new Date(a["chat_last_message"]["message_date"]))
        if (a_d < b_d) {
            return 1
        } else { return -1 }
    })
    known_users = response["known_users"]
    console.warn(response)
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



function changeFon() {
    let fon_index = Number(cookies["nfon"])
    fon_index += 1
    if (fon_index == NFONS) { fon_index = 0 }
    document.getElementById("chat_fon_img").src = "../front/data/chat_fon" + fon_index + ".jpg"
    setCookie("nfon", fon_index)
} document.getElementById("chat_fon_img").src = "../front/data/chat_fon" + cookies["nfon"] + ".jpg"

function changeTheme() {
    document.documentElement.classList.remove(THEMES_CLASSES[cookies["theme"]])
    let theme = Number(getCookie("theme")) + 1
    if (theme == THEMES_CLASSES.length) {theme = 0}
    document.documentElement.classList.add(THEMES_CLASSES[theme])
    setCookie("theme", theme)
    if (theme == 1 || theme == 2) {
        let jc = "w"
        if (theme == 2) { jc = "b" }
        for (let n = 0; n < JN; n++) {
            let j = document.getElementById("J" + n)
            //alert(j.src)
            if (j.src[j.src.length-15] == "1") {
                j.src = '/front/main/1jackdaws_'+jc+'.svg'
            } else {
                j.src = '/front/main/2jackdaws_'+jc+'.svg'
            }
        }
    }
} document.documentElement.classList.add(THEMES_CLASSES[cookies["theme"]])

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
                    <img src=/front/icons/${chats[i]["chat_ico"]}.jpg class="chat_ico"> 
                    <div id="chat_name_text_box_${i}" class="chat_button_text_box"> <nobr><b>${chats[i]["chat_name"]}</b><br>${chats[i]["chat_last_message"]["message_text"].replace(/<br>/g, " ")}</nobr></div>
                    <div id="chat_text_box__${i}" class="chat_button_time_box"> <i> ${chats[i]["chat_last_message"]["message_date"]} </i> </div>
                </div>
            </div>
        `
        document.getElementById("chats_container").innerHTML += html
    }
    if (SelectedChat == -1 && chats.length != 0) { select_chat(0) }
}

function resize_chat_text_box() {
    for (let i = 0; i < num_chats; i++) {
        document.getElementById("chat_text_box_" + i).style.width = 100 + "px"
    }
}

function select_chat(i) {
    JN = 0
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
    document.getElementById("selected_chat_ico").src = `/front/icons/${chats[i]["chat_ico"]}.jpg`
    //elem.style.borderRadius = "12px 0px 0px 12px"
}

//

function to_vertical_mode() {
    document.getElementById("left_panel_container").style.visibility = "hidden"
    document.getElementById("chats_container").style.visibility = "hidden"
    document.getElementById("chat_container").style.width = "100%"
    document.getElementById("chats_container_top").style.width = "100%"
    document.getElementById("chat_text_input_container").style.width = "calc(100% - 50px)"
    // document.getElementById("emojis_menu").style.right = "4%"
}

function to_horizontal_mode() {
    document.getElementById("left_panel_container").style.visibility = "visible"
    document.getElementById("chats_container").style.visibility = "visible"
    document.getElementById("chat_container").style.width = "calc(100% - 35% - 50px)"
    document.getElementById("chats_container_top").style.width = "calc(100% - 35% - 50px)"
    document.getElementById("chat_text_input_container").style.width = "calc(100% - 35% - 50px - 50px)"
    // document.getElementById("emojis_menu").style.right = "4%"
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

let in_settings = false
function settings() {
    in_group_settings = false
    document.getElementById("settings_group_container").classList.remove("settings_group_container_visible")
    in_settings = !in_settings
    let settings_container = document.getElementById("settings_container")
    if (in_settings) {
        settings_container.classList.add("settings_container_visible")
        document.getElementById("settings_row_name").innerHTML = "name: " + cookies["name"]
        document.getElementById("settings_row_username").innerHTML = "username: " + cookies["username"]
        document.getElementById("settings_row_email").innerHTML = "email: " + cookies["email"]
        document.getElementById("settings_head_ico").src = `/front/icons/${cookies["username"]}.jpg`
    } else {
        settings_container.classList.remove("settings_container_visible")
    }
}

let in_group_settings
function settingsGroup() {
    in_settings = false
    document.getElementById("settings_container").classList.remove("settings_container_visible")
    in_group_settings = !in_group_settings
    let settings_container = document.getElementById("settings_group_container")
    if (in_group_settings) {
        settings_container.classList.add("settings_group_container_visible")
        for (let usr of chats[SelectedChat]["all_users"]) {
            document.getElementById("settings_group_users_box").innerHTML += 
            `
                <div class="group_users_container">
                    <div class="group_users_box"> 
                        <img src="/front/icons/test_bot.jpg" class="chat_ico">
                        ${usr["username"]}
                    </div>
                </div>
            `
        }
        document.getElementById("settings_group_ico").src = `/front/icons/${chats[SelectedChat]["chat_ico"]}.jpg`
    } else {
        settings_container.classList.remove("settings_group_container_visible")
    }
}

// отправка сообщения
function send_msg() {
    let msgText = document.getElementById("message_textarea").value
    document.getElementById("message_textarea").value = ""
    send_msg_text(msgText)
}

function send_msg_text(text) {
    WS.send(JSON.stringify({"type": "send_msg", "args": {"msg_text": text, "chat_id": chats[SelectedChat]["chat_id"]}}))
    autoResize()
    autoScroll()
}

function autoScroll() {
    let scrollingDiv = document.getElementById('chat_container')
    scrollingDiv.scrollTop = scrollingDiv.scrollHeight
}


let JN = 0
function add_msg(msgText, sender_username, date = "Sun, 07 Apr 2024 16:52:43 GMT") {
    let whose_msg = Number(cookies["username"] != sender_username)
    msgText = format_msg_text(msgText)
    theme = Number(getCookie("theme")) + 1
    LAST_MSG_INDEX += 1
    let jc = "b"
    if (theme == 2) { jc = "w" }
    date = new Date(date)
    let min = String(date.getMinutes())
    let hour = String(date.getHours())
    if(min.length == 1) { min = "0" + min }
    if(hour.length == 1) { hour = "0" + hour }
    date = hour + ":" + min
    jf = () => {if (sender_username == cookies['username']) { return `<img id="J${JN}" src=/front/main/2jackdaws_${jc}.svg class="jackdaw_svg"></img>`} else { return ""} }
    let html = `
        <div class="message_box" style="justify-content: ${["end", "start", "center"][whose_msg]};">
            <div id="message_${LAST_MSG_INDEX}" class="${["my_message", "no_my_message", "notification_message"][whose_msg]}">
                ${msgText}
                <span class="my_message_time">
                ${date}
                ${jf()}
                </span>
            </div>
            
        </div>
    `
    JN++
    document.getElementById("message_container").innerHTML += html
}

const DOMAINS = [".ru", ".рф", ".com", ".net", ".org", ".info", ".biz", ".online", ".shop", ".site", ".site", ".xyz", ".uk", ".de", ".cn", ".nl", ".br", ".au", ".fr", ".eu"]
function format_msg_text(text) {
    text = text.split(" ")
    for (let n = 0; n < text.length; n++) {
        i = text[n]
        i.toLowerCase()
        for (let d of DOMAINS) {
            if (i.includes(d)) {
                console.log("-"*100)
                console.log(i)
                console.log(text)
                console.log(d)
                if (i.indexOf(d) != 0) {
                    text[n] = '<a target="_blank" href=' + i + '>' + i + "</a>"
                    break
                }
            }
            let si = i.split("\n")
            for (let n2 = 0; n2 < si.length; n2++) {
                i2 = si[n2]
                if (i2[0] == "/" && i2.split("/").length == 2) {
                    si[n2] = '<span style="color: var(--bot-commands-color); cursor:pointer" onclick="send_msg_text('+"'"+i2+"'"+')">'+i2+'</span>'
                }
            }
            text[n] = si.join("\n")
        }
    }
    text = text.join(" ")
    let ch = {"\n": "<br>", "T^{": "<i>", "}^T": "</i>", "T-{": "<b>", "}-T": "</b>", "T_{": "<u>", "}_T": "</u>"}
    for (let i in ch){
        text = text.split(i)
        text = text.join(ch[i])
    }
    return text
}

const smiles_message_button = document.querySelector('.smiles_message_button')
const emojis_menu = document.querySelector('.emojis_menu')
let timeoutId

smiles_message_button.addEventListener('mouseover', () => {
    emojis_menu.style.visibility = "visible"
    clearTimeout(timeoutId)
})
emojis_menu.addEventListener('mouseover', () => {
    emojis_menu.style.visibility = "visible"
    clearTimeout(timeoutId)
})
emojis_menu.addEventListener('mouseout', () => {
    timeoutId = setTimeout(() => {
        emojis_menu.style.visibility = "hidden"
    }, 200)
})
smiles_message_button.addEventListener('mouseout', () => {
    timeoutId = setTimeout(() => {
        emojis_menu.style.visibility = "hidden"
    }, 300)
})



function openFileSelector() {
    document.getElementById('fileInput').click()
}

document.getElementById('fileInput').addEventListener('change', function() {
    var file = this.files[0]
    if (file) {
        let formData = new FormData()
        formData.append('file', file)
        let xhr = new XMLHttpRequest()
        xhr.open('POST', `http://127.0.0.1:8080/edit_profile_icon?username=${cookies["username"]}`, true)
        xhr.onload = function() {
            if (xhr.status != 200) {
                alert('Ошибка при загрузке файла на сервер')
            }
        }
        xhr.send(formData)
        setTimeout(() => {
            document.getElementById("settings_head_ico").src = `/front/icons/${cookies["username"]}.jpg?${new Date().getTime()}`
        }, 1000)
    }
})

function closeAll_pop_up_windows() {
    document.getElementById("pop-up_window_container").style.visibility = "hidden"
    document.getElementById("create_group_container").style.visibility = "hidden"
}

function createGroupPopUp() {
    document.getElementById("pop-up_window_container").style.visibility = "visible"
    document.getElementById("create_group_container").style.visibility = "visible"
    document.getElementById("create_group_known_users").innerHTML = ""
    for (let usr of known_users) {
        document.getElementById("create_group_known_users").innerHTML += `
        <div id="UserContainerInCreateGroupPopUp_${usr["username"]}" class="create_group_known_user_info_container" onclick="selectUserInCreateGroupPopUp('${usr["username"]}')">
            <div class="create_group_known_user_info">
                <img src=/front/icons/${usr["username"]}.jpg class="chat_ico">
                <span style="padding-left: 12px;">${usr["name"]}</span>
            </div>
        </div>
        `
    }
}

let selectedUsersInCreateGroupPopUp = []
function selectUserInCreateGroupPopUp(user) {
    if (selectedUsersInCreateGroupPopUp.includes(user)) {
        document.getElementById("UserContainerInCreateGroupPopUp_" + user).classList.remove("create_group_known_user_info_container_selected")
        selectedUsersInCreateGroupPopUp = selectedUsersInCreateGroupPopUp.filter(item => item != user)
    } else {
        document.getElementById("UserContainerInCreateGroupPopUp_" + user).classList.add("create_group_known_user_info_container_selected")
        selectedUsersInCreateGroupPopUp.push(user)
    }
    document.getElementById("selectedUsersInCreateGroupPopUp").innerHTML = selectedUsersInCreateGroupPopUp.join(", ")
}

function createGroupApply() {
    let group_name = document.getElementById("create_group_name").value
    if (group_name != "" && selectedUsersInCreateGroupPopUp.length != 0) {
        request(`/request/start_group?username=${cookies["username"]}&password_hash=${cookies["password_hash"]}&chat_name=${group_name}&users=${selectedUsersInCreateGroupPopUp.join(",")},${cookies["username"]}`)
        closeAll_pop_up_windows()
    } else {
        if (group_name == "") { alert("You must specify the name of the group!") }
        else if (selectedUsersInCreateGroupPopUp.length == 0) { alert("You need to select at least one participant!") }
    }
}

document.getElementById("chat_container").addEventListener('scroll', () => {
    if (document.getElementById("message_container").getBoundingClientRect().bottom - window.innerHeight/3*2 <= window.innerHeight) {
        document.getElementById("scroll_btn").classList.remove("scroll_btn_vis")
    } else {
        document.getElementById("scroll_btn").classList.add("scroll_btn_vis")
    }
})