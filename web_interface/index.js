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
    await sendCommand(connectedPort, "INIT_COMMS");
    await sendCommand(connectedPort, "BLINK_LED");
    await readLoop(reader);
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
        // console.log(currentLine, "|", value);
        if (currentLine.endsWith("\n")) {
            try {
                const data = JSON.parse(currentLine);
                // console.log(data);
                await handleCommand(data);
            } catch (e){
                console.log(`Error parsing JSON: ${currentLine}`)
            }
            currentLine = "";
        }

    }
    // reader.read().then(({ value, done }) => {
    //     if (done) {
    //         console.log("DONE");
    //         return;
    //     }
    //     if (wantToClose) {
    //         console.log("Closing");
    //         connectedPort.close();
    //         return;
    //     }
    //     try {
    //         const data = JSON.parse(value);
    //         console.log(data);
    //     } catch (e){
    //         console.log(`Error parsing JSON: ${value}`)
    //         //console.error(e.message);
    //     }
    //     //console.log(value);
        
    //     readLoop(reader);
    // });
}

navigator.serial.addEventListener("disconnect", (e) => {
    // Remove `e.target` from the list of available ports.
    connectedPort = undefined;
    console.log("Disconnected");
});

document.getElementById("disconnect").onclick = async function() {
    
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
        default:
            console.log("Unknown command: " + command.command);
    }
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