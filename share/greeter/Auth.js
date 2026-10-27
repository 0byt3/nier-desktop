// greetd owns PAM and session creation. Never log or persist authentication data.
function create(backend, changed) {
    var state = { busy: false, active: false, waiting: false, canceling: false,
        prompt: "Password", echo: false, message: "", error: false };
    var pending = null;

    function publish() { changed(Object.assign({}, state)); }
    function reset(message, error) {
        pending = null;
        state = { busy: false, active: false, waiting: false, canceling: false,
            prompt: "Password", echo: false, message: message || "", error: !!error };
        publish();
    }
    return {
        submit: function(user, response) {
            if (state.busy || state.canceling) return;
            user = String(user || "").trim();
            if (!user) { reset("Enter your username.", true); return; }
            state.message = "Signing in…";
            state.error = false;
            state.busy = true;
            if (state.waiting) {
                state.waiting = false;
                publish();
                backend.respond(String(response));
            } else {
                state.active = true;
                pending = String(response);
                publish();
                backend.createSession(user);
            }
        },
        message: function(message, error, responseRequired, echoResponse) {
            if (!state.active || state.canceling) return;
            state.message = String(message || "");
            state.error = !!error;
            if (responseRequired) {
                if (pending !== null && !echoResponse) {
                    var response = pending;
                    pending = null;
                    publish();
                    backend.respond(response);
                    return;
                }
                pending = null;
                state.prompt = String(message || "Authentication response");
                state.echo = !!echoResponse;
                state.waiting = true;
                state.busy = false;
            }
            publish();
        },
        ready: function() {
            if (!state.active || state.canceling) return;
            pending = null;
            state.active = false;
            state.busy = true;
            state.waiting = false;
            state.message = "Starting your desktop…";
            publish();
            backend.launch();
        },
        failure: function(message) { reset(message || "Authentication failed. Try again.", true); },
        cancel: function() {
            pending = null;
            if (!state.active) { reset(); return; }
            state.canceling = true;
            state.active = false;
            state.waiting = false;
            state.busy = true;
            state.message = "Canceling…";
            publish();
            backend.cancelSession();
        },
        inactive: function() { if (state.canceling) reset(); }
    };
}
