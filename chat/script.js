let message = "";
let thinking = false;
let baseUrl = "PARAM_BASE_URL";

function sendPrompt() {
    const promptInput = document.getElementById("prompt-input");
    const prompt = promptInput.value;
    const model = document.getElementById("model-select").value;

    const evtSource = new EventSource(`${baseUrl}/chat-stream/${prompt}`);

    const response = document.getElementById("response-text");
    const responseTitle = document.getElementById("response-title");
    const card = document.getElementById("prompt-response");

    response.textContent = "Thinking";
    card.classList.remove("finished");
    card.classList.remove("idle");
    card.classList.add("thinking");
    card.style.display = "block";
    responseTitle.textContent = prompt;
    promptInput.value = "";

    thinking = true

    setTimeout(() => think(1), 500)

    evtSource.addEventListener("message", function (event) {
        if (thinking) {
            thinking = false;
            response.textContent = ""
        }
        let data = JSON.parse(event.data);
        message = data.message;
        response.textContent += message;
        card.classList.remove("thinking");
        card.classList.add("loading");
    });

    evtSource.addEventListener("end", function (event) {
        console.log("Stream ended:", message);
        card.classList.remove("loading");
        card.classList.add("finished");
        evtSource.close();
    });
}

function think(i) {
    if (thinking) {
        setTimeout(() => think(i + 1), 500)
        document.getElementById("response-text").textContent = "Thinking" + ".".repeat(i % 4)
    }
}

function rePrompt(input) {
    if (input.oldvalue == "") {
        document.getElementById("prompt-response").classList.remove("finished");
        document.getElementById("prompt-response").classList.add("idle");
    }
}

function getModels() {
    const request = new Request(`${baseUrl}/models`);
    fetch(request)
        .then((response) => {
            if (response.status == 200) {
                return response.json();
            } else {
                document.getElementById("model-error").style.display = "inline";
                document.getElementById("model-select").style.display = "none";
                console.log('Failed to fetch models: ', response)
                return [];
            }
        })
        .then((data) => {
            for (const model of data.models) {
                var opt = document.createElement('option')
                opt.value = model.name
                opt.innerHTML = model.displayName + (model.allowed ? "" : " <span>🔒</span>")
                if (!model.allowed) {
                    opt.disabled = true
                }
                if(model.name == data.default) {
                    opt.selected = true
                }
                document.getElementById("model-select").appendChild(opt)
            }
        })
        .catch((error) => {
            document.getElementById("model-select").style.display = "none";
            document.getElementById("model-error").style.display = "inline";
            console.log('Failed to fetch models: ', error)
        })
}
