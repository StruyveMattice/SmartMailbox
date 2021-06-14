const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

let html_new_code, btn_submit;

const listenToUI = function () {
    btn_submit.addEventListener("click", function () {
        console.log('btn pressed')
        socket.emit('F2B_new_code', html_new_code.value)
        console.log(html_new_code.value)
        html_new_code.value = ""
    })
}
const listenToSocket = function () { }

document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  html_new_code = document.querySelector(".js-input-new-code")
  btn_submit = document.querySelector(".js-code-submit")
  listenToUI();
  listenToSocket();
})
