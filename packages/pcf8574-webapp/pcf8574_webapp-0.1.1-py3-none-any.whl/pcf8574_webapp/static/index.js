const socket = new ReconnectingWebSocket(`ws://${location.host}/ws`);
let pinStates = {};

// Update UI based on pinStates array
function updateUI(bus, address) {
    pinStates[bus][address].forEach((state, index) => {
        const checkboxes = document.getElementsByClassName(`pin-${bus}-${address}-${index}`);
        if (checkboxes.length === 0) return;

        for (const checkbox of checkboxes) {
            checkbox.checked = state % 2;
            checkbox.classList.toggle("overridden", state > 1);
        }
    });
}

// Toggle pin state and send update to WebSocket server
function togglePin(bus, address, pinIndex) {
    if (!(bus in pinStates)) {
        pinStates[bus] = {};
    }
    if (!(address in pinStates[bus])) {
        pinStates[bus][address] = Array(8).fill(false);
    }
    if (socket.readyState === ReconnectingWebSocket.OPEN) {
        if (pinStates[bus][address][pinIndex] < 2) {
            pinStates[bus][address][pinIndex] = 2;
        } else {
            pinStates[bus][address][pinIndex] = (pinStates[bus][address][pinIndex] + 1) % 4;
        }
    }
    updateUI(bus, address);
    if (socket.readyState === ReconnectingWebSocket.OPEN) {
        const override = pinStates[bus][address].map(state =>
            state > 1 ? !!(state % 2) : null
        );
        const payload = {
            i2c_bus: bus,
            i2c_address: address,
            values: {
                override: override
            }
        };
        socket.send(JSON.stringify(payload));
    }
}

// Handle incoming WebSocket messages
socket.onmessage = function(event) {
    let data;
    try {
        data = JSON.parse(event.data);
    } catch (e) {
        console.error("Invalid JSON:", event.data);
        return;
    }

    const bus = data["i2c_bus"];
    const address = data["i2c_address"];
    const unspoiled = data["values"]["unspoiled"];
    const override = data["values"]["override"];

    if (!(bus in pinStates)) {
        pinStates[bus] = {};
    }
    if (!(address in pinStates[bus])) {
        pinStates[bus][address] = Array(8).fill(false);
    }

    for (let i=0; i < 8; i++) {
        const isOverridden = override[i] !== null;
        pinStates[bus][address][i] = isOverridden ? override[i] + 2 : (unspoiled[i] ? 1 : 0);
    }
    updateUI(bus, address);
};

// Handle WebSocket connection open
socket.onopen = function() {
    console.log("Connected to WebSocket server.");
    document.getElementById("status").classList.add("hidden");
    socket.send("init");
};

// Handle WebSocket closure and attempt reconnection
socket.onclose = function () {
    console.log("Disconnected from WebSocket server.");
    document.getElementById("status").classList.remove("hidden");
    // setTimeout(connect, 3000);
};
