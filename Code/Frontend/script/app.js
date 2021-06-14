const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
Chart.defaults.global.defaultFontColor = "#fff";

let html_rain, html_temperature, html_status_door,html_status_mail, html_code,html_new_code,btn_submit, btn_door, newRfidCode;
let currentRain, currentTemp , isMail;


const listenToUI = function () {
  btn_door.addEventListener("click", function () {
    console.log(newRfidCode)
    if (btn_door.innerHTML == "Open Door" && html_code.value == newRfidCode) {
      socket.emit('F2B_deur_open')
      btn_door.innerHTML = "Close Door"
      html_status_door.innerHTML = "Door is open"
      html_status_mail.innerHTML = "There is no mail at the moment"
      html_code.value = ""
    }

    else if (btn_door.innerHTML == "Close Door" && html_code.value == newRfidCode) {
      socket.emit('F2B_deur_toe')
      btn_door.innerHTML = "Open Door"
      html_status_door.innerHTML = "Door is closed"
      html_code.value = ""
    }
  
    else {
      console.log("Invalid Code")
    }
  })

};

const listenToSocket = function () {
  socket.on("connect", function () {
    console.log("Verbonden met de socket");
  });

  socket.on('B2F_new_code', function (value) {
    newRfidCode = value.newRfidCode
    console.log(newRfidCode)
  });

  socket.on("B2F_status_rain", function (value) {
    currentRain = value.currentRain;
    html_rain.innerHTML = `${currentRain} % regen`;
  });

  socket.on("B2F_door_opened", function () {
    html_status_mail.innerHTML = "There is no mail at the moment"
  });

  socket.on("B2F_status_temp", function (value) {
    currentTemp = value.currentTemp;
    html_temperature.innerHTML = `${currentTemp} °C`;
  });

  socket.on('B2F_mail_delivered', function (value) {
    if (value.isMail == true) {
      html_status_mail.innerHTML = "You've Got Mail "
    }
    else {
      html_status_mail.innerHTML = "There is no mail at the moment"
    }
  })
  
  socket.on('B2F_history', function (value) {
    console.log(value.Value)
  })
};

const showTempChart = function (jsonTemperatuur) {
  var data = [];
  var labelsTemp = [];
  //console.log(jsonTemperatuur);
  for (let i of jsonTemperatuur) {
    data.push(i.Value);
  }
  for (let i of jsonTemperatuur) {
    labelsTemp.push(moment(i.Timestamp).format("DD/MM HH:mm"));
  }
  console.log(labelsTemp);
  console.log(data);
  var ctx = document.getElementById('myChart1').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labelsTemp.reverse(),
      datasets: [{
        label: 'Temperature °C',
        data: data.reverse(),
        backgroundColor:'rgba(255, 255, 255, 0.8)',
        borderColor : "#27a6c2",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            suggestedMin: 0,
            suggestedMax: 40
          }

        }]
      }
    }
  });
};

const showRainChart = function (jsonTemperatuur) {
  var data = [];
  var labelsTemp = [];
  //console.log(jsonTemperatuur);
  for (let i of jsonTemperatuur) {
    data.push(i.Value);
  }
  for (let i of jsonTemperatuur) {
    labelsTemp.push(moment(i.Timestamp).format("DD/MM HH:mm"));
  }
  console.log(labelsTemp);
  console.log(data);
  var ctx = document.getElementById('myChart2').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labelsTemp.reverse(),
      datasets: [{
        label: 'Rain %',
        data: data.reverse(),
        backgroundColor:'rgba(255, 255, 255, 0.8)',
        borderColor: "#27a6c2",
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            suggestedMin: 0,
            suggestedMax: 100
          }

        }]
      }
    }
  });
};



const getTempHist = function () {
  handleData(`http://${lanIP}/temperature`, showTempChart, 'GET');
};
const getRainHist = function () {
  handleData(`http://${lanIP}/rain`, showRainChart, 'GET');
}


document.addEventListener("DOMContentLoaded", function () {
  console.info("DOM geladen");
  html_rain = document.querySelector(".js-rain");
  html_temperature = document.querySelector(".js-temp");
  html_status_door = document.querySelector(".js-status-door")
  html_status_mail = document.querySelector(".js-status-mail")
  html_code = document.querySelector(".js-input-code")
  html_new_code = document.querySelector(".js-input-new-code")
  btn_door = document.querySelector(".js-door-button")
  btn_submit = document.querySelector(".js-code-submit")
  getTempHist();
  getRainHist();
  listenToUI();
  listenToSocket();
})
