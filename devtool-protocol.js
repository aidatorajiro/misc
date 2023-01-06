const {WebSocket} = require('ws');
const {randomUUID} = require('crypto');

const fs = require('fs');

(async function () {
    const mainData = await fetch('http://localhost:9222/json');
    const mainJson = await mainData.json();
    const getResponseBody_id_table = {};
    
    console.log(mainJson[0].webSocketDebuggerUrl);
    
    const getId = (() => {
        let currentId = Math.floor(Math.random()*1000000000);
    
        return () => {
            currentId++;
            console.log("sending request id %s", currentId)
            return currentId;
        }
    })();
    
    const ws = new WebSocket(mainJson[0].webSocketDebuggerUrl, {
        perMessageDeflate: false
    });
    
    ws.on('open', function open() {
      ws.send(JSON.stringify({"id": getId(), "method": "Fetch.enable","params": {"patterns": [{"requestStage": "Response" }]}}));
    });
    
    ws.on('message', function message(data) {
      let received = JSON.parse(data)
      if (received.id !== undefined) {
         // direct response from server
         console.log('received response of id %s', received.id);
         if (received.error !== undefined) {
             console.error('ERR!', received.error)
         }
         if (received.result !== undefined && received.result.body !== undefined && received.id in getResponseBody_id_table) {
             const metadata = getResponseBody_id_table[received.id]
             console.log('Body received: %s', metadata.request.url)
              ws.send(JSON.stringify({"id": getId(), "method": "Fetch.continueRequest","params": {"requestId": metadata.requestId}}));
             console.log('sent continueRequest')
             let uuid = randomUUID()
             fs.writeFileSync("out/" + uuid + ".data", received.result.body)
             fs.writeFileSync("out/" + uuid + ".json", JSON.stringify(metadata))
             delete getResponseBody_id_table[received.id]
         }
      } else {
          // extra data from server
          if (received.method === "Fetch.requestPaused") {
              const requestId = received.params.requestId;
              const url = received.params.request.url;
              console.log('paused request %s: %s', requestId, url)
              const getResponseBody_id = getId();
              ws.send(JSON.stringify({"id": getResponseBody_id, "method": "Fetch.getResponseBody","params": {"requestId": requestId}}));
              getResponseBody_id_table[getResponseBody_id] = received.params
            
              // ws.send(JSON.stringify({"id": getId(), "method": "Fetch.continueRequest","params": {"requestId": requestId}}));
              // console.log('sent continueRequest')
          }
      }
    });
})();