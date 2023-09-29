// Description: This file contains the code for the web interface of the project.

/**
 * @type {SerialPort} 
 */
let connectedPort;
let wantToClose = false;
let reader;
let time_offset;

document.getElementById("connect").onclick = async function() {
    const usbVendorId = 0x239A;
    connectedPort = await navigator.serial
        .requestPort({ filters: [{ usbVendorId }] })
    console.log("got port")
    let wantToClose = false;
    await connectedPort.open({ baudRate: 115200 });
    console.log(connectedPort.getInfo());
    let decoder = new TextDecoderStream();
    let inputStream = connectedPort.readable.pipeThrough(decoder);
    reader = inputStream.getReader();
    await setUpTOTKey();
    await readLoop(reader);
}

async function setUpTOTKey() {
    await sendCommand(connectedPort, "INIT_COMMS");
    await sendCommand(connectedPort, "BLINK_LED");
    await sendCommand(connectedPort, "GET_VOLTAGE");
    await sendCommand(connectedPort, "LIST_KEYS");
}

async function readLoop(reader) {
    currentLine = ""
    while (!wantToClose){
        let value;
        let done;
        try {
            ({value, done} = await reader.read())
        } catch (e) {
            // type error is just the port closing
            // only catch that
            if (e.name != "TypeError") {
                throw e;
            } else {
                console.log("Port closed");
                return;
            }
        }
        if (done) {
            console.log("DONE");
            return;
        }
        if (value.includes("🐍")) {
            continue; // first line has a snake and isn't JSON
            // make sure a snake can never be in an actual packet
        }
        currentLine += value;
        console.debug(currentLine, "|", value);
        if (currentLine.endsWith("\n")) {
            try {
                const data = JSON.parse(currentLine);
                // console.log(data);
                await handleCommand(data);
            } catch (e){
                console.log(`Error parsing JSON: ${currentLine}`)
                throw e
            }
            currentLine = "";
        }

    }
}

navigator.serial.addEventListener("disconnect", (e) => {
    // Remove `e.target` from the list of available ports.
    connectedPort = undefined;
    console.log("Disconnected");
});

document.getElementById("disconnect").onclick = async function() {
    // TODO
}

/**
 * 
 * @param {SerialPort} port 
 * @param {string} command 
 * @param {} args 
 */
async function sendCommand(port, command, args={}) {
    console.log("sending command " + JSON.stringify({ command, args }))
    const encoder = new TextEncoder();
    const writer = port.writable.getWriter();
    const data = encoder.encode(JSON.stringify({ command, args })+"\n");
    await writer.write(data);
    writer.releaseLock();
}

async function handleCommand(command){
    console.log("handling command " + JSON.stringify(command));
    switch (command.command) {
        case "COMMS_START_ACK":
            calculateTimeOffset(command.args.current_time);
            break;
        case "TIME_SET_ACK":
            calculateTimeOffset(command.args.current_time);
            break;
        case "TIME_GET_RESPONSE":
            calculateTimeOffset(command.args.current_time);
            break;
        case "BLINK_ACK":
            break;
        case "VOLTAGE_GET_RESPONSE":
            document.getElementById("battery-voltage").textContent = `${command.args.voltage}V`;
            break;
        case "KEY_LIST_RESPONSE":
            // each key should be in a row with a Remove button
            // that remove button should call removeKey with the key id
            const keyList = document.getElementById("key-list");
            keyList.innerHTML = "";
            for (const service_name of command.args.keys) {
                const row = document.createElement("div");
                const keyId = document.createElement("span");
                keyId.textContent = service_name;
                const removeButton = document.createElement("button");
                removeButton.textContent = "Remove";
                removeButton.onclick = () => {
                    removeKey(service_name);
                }
                row.appendChild(keyId);
                row.appendChild(removeButton);
                // put the key ID on the left and the remove button on the right using flexbox
                row.style.display = "flex";
                row.style.justifyContent = "space-between";
                keyList.appendChild(row);
            }
            break;
        case "KEY_REMOVE_ACK":
            await sendCommand(connectedPort, "LIST_KEYS");
            break;
        case "KEY_ADD_ACK":
            await sendCommand(connectedPort, "LIST_KEYS");
            break;
        case "LOG":
            switch (command.args.level) {
                case "DEBUG":
                    console.debug("board: " + command.args.msg);
                    break;
                case "INFO":
                    console.info("board: " + command.args.msg);
                    break;
                case "WARNING":
                    console.warn("board: " + command.args.msg);
                    break;
                case "ERROR":
                    console.error("board: " + command.args.msg);
                    alert("Error from board: " + command.args.msg);
            }
            break;
        default:
            console.log("Unknown command: " + command.command);
    }
}

function removeKey(service_name) {
    // confirm with modal
    document.getElementById("remove-confirm-key").textContent = service_name;
    document.getElementById("remove-confirm-dialog").showModal();
}

document.getElementById("remove-confirm").onclick = async function(e) {
    e.preventDefault();
    document.getElementById("remove-confirm-dialog").close();
    const service_name = document.getElementById("remove-confirm-key").textContent;
    await sendCommand(connectedPort, "REMOVE_KEY", { service_name });
}

document.getElementById("remove-cancel").onclick = async function(e) {
    e.preventDefault();
    document.getElementById("remove-confirm-dialog").close();
}

document.getElementById("add-key-start").onclick = async function() {
    // use a modal
    document.getElementById("add-key-modal").showModal();
}

document.getElementById("add-key-cancel").onclick = async function(e) {
    e.preventDefault();
    document.getElementById("add-key-modal").close();
}

document.getElementById("add-key-form").onkeydown = async function(e) {
    // submit on enter
    if (e.key == "Enter") {
        document.getElementById("add-key-form").onsubmit(e);
    }
}

document.getElementById("add-key-form").onsubmit = async function(e) {
    e.preventDefault();
    const service_name = document.getElementById("add-key-service-name").value;
    const secret = document.getElementById("add-key-secret").value;
    document.getElementById("add-key-modal").close();
    // make sure there are no snake emojis in the key or service name (edge case)
    if (service_name.includes("🐍") || secret.includes("🐍")) {
        alert("Invalid key or service name (no sneks allowed, sorry)");
        return;
    }
    document.getElementById("add-key-service-name").value = "";
    document.getElementById("add-key-secret").value = "";
    await sendCommand(connectedPort, "ADD_KEY", { service_name, secret, "digits": 6 });
}

function calculateTimeOffset(timestamp){
    const itsTime = new Date(timestamp*1000);
    const ourTime = new Date();
    time_offset = ourTime-itsTime;
    console.log("Their time: " + itsTime.toUTCString())
    console.log("Time offset: " + time_offset/1000);
    document.getElementById("time-difference").textContent = `${time_offset/1000} seconds`;
}

setInterval(() => {
    document.getElementById("computer-time").textContent = new Date().toUTCString();
    if (time_offset) {
        document.getElementById("key-time").textContent = new Date(new Date().getTime() - time_offset).toUTCString();
    }
}, 100);

document.getElementById("sync-time").onclick = async function() {
    if (!connectedPort) {
        console.log("Not connected");
        return;
    }
    await sendCommand(connectedPort, "SET_TIME", { current_time: Math.floor(new Date().getTime()/1000) });
}