const fullscreen = {
    onFullscreenExit: () => {
    },  // do nothing by default

    add_popup: function () {
        if ($('#backdrop-div').length) {
            return
        }

        const div = document.createElement('div');
        div.id = "fullscreen-modal-div";
        div.innerHTML = `
		  </div>
		    <div class="fullscreen-modal-content">
		        <p>
                    This experiment must be run in fullscreen mode.
                    <br>
                    To exit fullscreen mode, press ESC or F11.
                </p>
<!--                <button id="btn-go-fullscreen">Switch to fullscreen</button>-->
                <button id="btn-go-fullscreen">Перейти в полноэкранный режим</button>
            </div>
		`;
        document.body.appendChild(div);
    },

    /* View in fullscreen */
    open: function () {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen();
        } else if (elem.mozRequestFullScreen) { /* Firefox */
            elem.mozRequestFullScreen();
        } else if (elem.webkitRequestFullscreen) { /* Chrome, Safari and Opera */
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) { /* IE/Edge */
            elem.msRequestFullscreen();
        }
    },

    /* Close fullscreen */
    close: function () {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { /* Firefox */
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { /* Chrome, Safari and Opera */
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { /* IE/Edge */
            document.msExitFullscreen();
        }
    },

    add_event_listener: function (fun) {
        /* Standard syntax */
        document.addEventListener("fullscreenchange", fun);

        /* Firefox */
        document.addEventListener("mozfullscreenchange", fun);

        /* Chrome, Safari and Opera */
        document.addEventListener("webkitfullscreenchange", fun);

        /* IE / Edge */
        document.addEventListener("msfullscreenchange", fun);
    },

    remove_event_listener: function (fun) {
        /* Standard syntax */
        document.removeEventListener("fullscreenchange", fun);

        /* Firefox */
        document.removeEventListener("mozfullscreenchange", fun);

        /* Chrome, Safari and Opera */
        document.removeEventListener("webkitfullscreenchange", fun);

        /* IE / Edge */
        document.removeEventListener("msfullscreenchange", fun);
    },

    isFullscreen: function() {
        return Boolean(
            document.fullscreenElement || /* Standard syntax */
            document.webkitFullscreenElement || /* Chrome, Safari and Opera syntax */
            document.mozFullScreenElement ||/* Firefox syntax */
            document.msFullscreenElement /* IE/Edge syntax */
        );
    },

    ask_for_fullscreen: function () {
        if (fullscreen.isFullscreen()) {
            return
        }
        $('#fullscreen-modal-div').fadeTo(200, 1);

        const button_selector =  $("#btn-go-fullscreen");
        button_selector.off('click');
        button_selector.click(fullscreen.switch_to_fullscreen);
    },

    hide_popup: function () {
        $('#fullscreen-modal-div').fadeOut(200);
    },

    switch_to_fullscreen: function () {
        fullscreen.hide_popup();
        fullscreen.open();
        // disable scrollbars
        $("body").css("overflow", "hidden");
    },

    handle_exit: function () {
        if (!fullscreen.isFullscreen()) {
            fullscreen.onFullscreenExit();
            $("body").css("overflow", "auto");
            fullscreen.ask_for_fullscreen();
        }
    },

    enforce_fullscreen: function () {
        fullscreen.add_popup();
        fullscreen.add_event_listener(fullscreen.handle_exit);
        fullscreen.ask_for_fullscreen();
    },

    stop_enforcing_fullscreen: function () {
        fullscreen.hide_popup();
        fullscreen.remove_event_listener(fullscreen.handle_exit);
    },
};
