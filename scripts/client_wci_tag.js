/**  FILL THE VALUES BELOW  */
var CONVERSION_IMPORT_URL = ""; // fill with your bsp webhook URL
var WHATSAPP_NUMBER = ""; // fill with your whatsapp number account. E.g. +15550801213

/** DO NOT CHANGE BELOW */
function encodeMessage(message) {
  return encodeURIComponent(message);
}
function getMessageWithProtocol(protocol_number) {
  return "[Chat ID: " + protocol_number + "] Hi there!";
}
function getURL(message) {
  return "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + message;
}
function getProtocolNumber() {
  return crypto.randomUUID()
    .split("")
    .filter(function (value, index, self) {
      return self.indexOf(value) === index;
    })
    .join("")
    .slice(-6);
}
function getGclid() {
  var params = new URLSearchParams(location.search);
  var gclid = params.get("gclid");

  if (!gclid) {
    // Checks for a cookie
    var gcookie = document.cookie.split(";").map(function (cookie) {
      return cookie.split("=");
    });
    gcookie = gcookie.find(function (cookie) {
      return cookie[0].trim() == "_gcl_aw";
    });

    if (gcookie) gclid = gcookie[1].split(".")[2];
  }
  return gclid;
}
var protocol_number = getProtocolNumber();
var message = encodeMessage(getMessageWithProtocol(protocol_number));
var payload = {};

var url = new URL(CONVERSION_IMPORT_URL);
var params = new URLSearchParams(url);
params.set("chatid", protocol_number);
params.set("gclid", getGclid());

fetch(CONVERSION_IMPORT_URL + "?" + params.toString(), {
  method: "POST",
  headers: {
    "Content-type": "application/json",
  },
  body: JSON.stringify(payload),
})
  .then(function (response) {
    return response.json();
  })
  .catch(function (err) {
    console.error(err);
  })
  .then(function () {
    location.replace(getURL(message));
  });

// Uncomment the folllowing lines if you'd like to have the protocol number
// in the datalyer
// dataLayer.push({
//   'protocol_number': protocol_number,
//   'event': 'click_on_wci'
// });
