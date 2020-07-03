function get_current_time() {
    return new Date()
}

const trial = {

    results: {
        dt_start_pressed: null,
        dt_frame_presented: null,
        dt_audio_started: null,
        dt_response_selected: null,
        selected_response: null,
        trajectory: null,
        trial_id: null
    },

    // Trial info (what to show, whether it has been run) are stored in localStorage
    set uris(value) {
        localStorage.setItem('uris', JSON.stringify(value));
    },

    get uris() {
        return JSON.parse(localStorage.getItem('uris'));
    },

    set timing(value) {
        localStorage.setItem('timing', JSON.stringify(value));
    },

    get timing() {
        return JSON.parse(localStorage.getItem('timing'));
    },

    set has_been_run(value) {
        localStorage.setItem('has_been_run', JSON.stringify(value));
    },

    get has_been_run() {
        return JSON.parse(localStorage.getItem('has_been_run'));
    },

    set trial_id(value) {
        localStorage.setItem('trial_id', JSON.stringify(value));
    },

    get trial_id() {
        return JSON.parse(localStorage.getItem('trial_id'));
    },

    set correct_response(value) {
        localStorage.setItem('correct_response', JSON.stringify(value));
    },

    get correct_response() {
        return JSON.parse(localStorage.getItem('correct_response'));
    },

    set full_detailed_feedback(value) {
        localStorage.setItem('full_detailed_feedback', JSON.stringify(value));
    },

    get full_detailed_feedback() {
        return JSON.parse(localStorage.getItem('full_detailed_feedback'));
    },

    update_settings: function (data) {
        trial.uris = data.uris;
        trial.timing = data.timing;
        trial.trial_id = data.trial_id;
        trial.correct_response = data.correct_response;
        trial.full_detailed_feedback = data.full_detailed_feedback;
        trial.has_been_run = false;
    },
    // end of trial info stuff

    handle_ajax_response: function (data) {
        if (data.type === 'trial_settings') {
            trial.update_settings(data);
        } else if (data.type === 'redirect') {
            // Reloading will result in exiting fullscreen and pointer unlocking. We should not reaact to those.
            fullscreen.onFullscreenExit = () => {};  // do nothing
            mousetracking.onPointerUnlock = () => {};  // do nothing
            window.location.href = window.location.href;
        }
    },

    get_settings: function () {
        // Gets new trial settings from the server if necessary.
        // Might get called when the current settings have not been used yet, then resolves immediately.
        return new Promise((resolve, reject) => {
            // trial.has_been_run is null before any settings were received at all
            if (trial.has_been_run === true || trial.has_been_run === null) {
                $.ajax({
                    url: 'get_new_trial_settings/',
                    dataType: 'json',
                    success: function (data) {
                        trial.handle_ajax_response(data);
                        resolve();
                    }
                })
            } else {
                resolve();
            }
        })
    },

    send_results: function () {
        // also gets the new settings
        return new Promise((resolve, reject) => {
            $.post({
                url: 'save_trial_results/',
                headers: {"X-CSRFToken": csrf_token},
                dataType: 'json',
                data: JSON.stringify({results: trial.results}),
                success: function (data) {
                    console.log('Results successfully sent');
                    trial.handle_ajax_response(data);
                    resolve();
                }
            })
        })
    },

    setup: function () {
        trial.add_all();
        trial.get_settings()
            .then(trial.promise_to_load_all)
            .then(start_button.show);
        fullscreen.onFullscreenExit = trial.abort;
        fullscreen.enforce_fullscreen();
    },

    add_all: function () {
        frame.add();
        audio.add();
        response_options.add();
        start_button.add();
        feedback.add();
        modal.setup();
    },

    promise_to_load_all: function () {
        const load_promises = [
            response_options.promise_to_load_images(),
            frame.promise_to_load_images(),
            audio.promise_to_load()];
        return Promise.all(load_promises);
    },

    hide_all: function () {
        frame.hide();
        // audio.stop();
        response_options.hide();
        start_button.hide();
        feedback.hide();
    },

    start: function () {
        start_button.disable();
        response_options.enable();
        start_button.hide();
        mousetracking.onPointerUnlock = trial.abort;
        mousetracking.start_tracking();
        trial.run();
    },

    run: function () {
        trial.has_been_run = true;
        trial.results.trial_id = trial.trial_id;
        // show frame
        frame.show();
        trial.results.dt_frame_presented = get_current_time();
        window.setTimeout(
            function () {
                // hide frame, start playing audio
                frame.hide();
                audio.play();
                window.setTimeout(
                    function () {
                        // show options and release the cursor
                        response_options.show();
                        mousetracking.release_cursor();
                    },
                    trial.timing.audio)
            },

            trial.timing.frame)
    },

    abort: function () {
        // Hide everything
        response_options.disable();
        start_button.enable();
        trial.hide_all();

        // Discard any mousetracking data
        mousetracking.reset();

        /// Set up a new trial (if the last trial has not been run yet, it will not change)
        trial.setup();
    },

    stop: function () {
        response_options.disable();
        start_button.enable();
        trial.hide_all();

        // send the results to the server
        mousetracking.stop_tracking();
        trial.results.trajectory = mousetracking.trajectory;
        Promise.all([
            feedback.show_and_hide_promise(trial.correct_response)
                .then(trial.show_all_stimuli)  // only done during the first couple of the training trials
                .then(trial.check_initiation_time),
            trial.send_results()]
        )
            .then(trial.promise_to_load_all)
            .then(start_button.show);
    },

    debug: function () {
        fullscreen.stop_enforcing_fullscreen();
    },

    check_initiation_time: function () {
        const initiationTimeInMs = trial.results.trajectory[1].t - trial.results.trajectory[0].t;
        return new Promise(function (resolve) {
            if (initiationTimeInMs > 1000) {
                modal.text = 'Пожалуйста, начинайте выбор сразу после того, как появятся варианты ответа, даже если вы еще ' +
                      'не до конца уверены в своем решении';
                modal.show();
            }
            return resolve();
        });
    },

    show_all_stimuli: function() {
        return new Promise((resolve) => {
            if (!trial.full_detailed_feedback) {
                return resolve();
            }

            modal.text =
                'Сейчас мы снова покажем рамку, варианты ответа и проиграем вопрос. Так будет происходить только в ' +
                'течение первых нескольких тренировочных предъявлений - в дальнейшем мы будем только сообщать, ' +
                'правильно ли вы ответили.';
            modal.onHideRunOnce = () => {  // this function will be run when the message above is closed
                frame.show();
                response_options.disable();
                response_options.show();
                audio.play();

                window.setTimeout(
                    () => {
                        modal.text = 'Продолжите, когда будете готовы';
                        modal.onHideRunOnce = () => {  // this function will be run when the message above is closed
                            trial.hide_all();
                            return resolve();
                        };
                        modal.show();
                    },
                6000);
            };

            modal.show();


        });
    },
};

function promise_to_load_image(img_element, uri) {
    if (uri != null) {
        return new Promise((resolve, reject) => {
            img_element.onload = function () {
                console.log(uri + ' loaded');
                resolve();
            };
            img_element.onerror = reject;
            img_element.style.display = 'inline';
            img_element.src = uri;
        })
    } else {
        return new Promise((resolve, reject) => {
            img_element.style.display = 'none';
            img_element.src = '';
            resolve();
        })
    }
}

frame = {
    calculate_sizes: function () {
        // In the offline version,
        // the frame had ~17 px borders and ~220 px square cells,
        // the screen resolution was 1920x780
        // returns cell side and border width as percentages of the width
        const percent_per_pixel = 100 / 1920;
        const border = 17 * percent_per_pixel;
        const cell_side = 210 * percent_per_pixel;
        const image_side = 120 * percent_per_pixel;
        return [cell_side, border, image_side];
    },

    add: function () {
        if ($('#frame-div').length) {
            return
        }

        const div = document.createElement('div');
        div.style.visibility = 'hidden';
        div.className = 'center-of-the-screen';
        div.id = "frame-div";
        div.innerHTML = `
			<table class="frame">
				<tr>
					<td class="frame">
    					<div class="frame-image-container">
	    					<img class = "as-large-as-fits" id="image-0">
	    				</div>
					</td>
					<td class="frame">
						<div class="frame-image-container">
						    <img class = "as-large-as-fits" id="image-1">
						</div>
					</td>
				</tr>
				<tr>
					<td class="frame">
					    <div class="frame-image-container">
						    <img class = "as-large-as-fits" id="image-2">
                        </div>
					</td>
					<td class="frame">
					    <div class="frame-image-container">
						    <img class = "as-large-as-fits" id="image-3">
						</div>
					</td>
				</tr>
			</table>
		`;
        document.body.appendChild(div);


        [cell_side, border, image_side] = frame.calculate_sizes();

        $('td.frame').css({
            'height': cell_side + 'vw',
            'width': cell_side + 'vw',
            'border-width': border + 'vw',
            'border-style': 'solid',
            'border-color': 'brown',
            'text-align': 'center'
        });

        $('.frame-image-container').css({
            'height': image_side + 'vw',
            'width': image_side + 'vw',
            'display': 'inline-block'
        });
    },

    promise_to_load_images: function () {
        const promises = [];
        for (let i = 0; i < 4; i++) {
            let uri = trial.uris.frame_images[i];
            let img_element = $('#image-' + i).get(0);
            promises.push(promise_to_load_image(img_element, uri));
        }
        return Promise.all(promises);
    },

    show: function () {
        $('#frame-div').css('visibility', 'visible');
    },

    hide: function () {
        $('#frame-div').css('visibility', 'hidden');
    },
};

audio = {
    log_dt_audio_started: function() {
        trial.results.dt_audio_started = get_current_time();
    },

    add: function () {
        if ($('#audio').length) {
            return
        }

        const audio_element = document.createElement('audio');
        audio_element.id = 'audio';
        audio_element.style.visibility = 'hidden';
        audio_element.addEventListener('play', audio.log_dt_audio_started);
        document.body.appendChild(audio_element);
    },

    promise_to_load: function () {
        const audio_element = $('#audio').get(0);
        return new Promise((resolve, reject) => {
            audio_element.oncanplaythrough = function () {
                console.log('audio loaded');
                resolve();
            };
            audio_element.onerror = reject;
            audio_element.src = trial.uris.audio;
            audio_element.load();
        });
    },

    play: function () {
        const audio_element = $('#audio').get(0);
        audio_element.play();
    }
};

response_options = {
    add_response: function (corner) {
        const id = 'response-' + corner;
        if ($('#' + id).length) {
            return
        }

        const div = document.createElement('div');
        div.className = 'response-div';
        div.id = id;
        let cssText = "position: absolute; height:10vw; width: 10vw; top: 0%;";
        cssText += "border: 3px solid black;";
        if (corner === 'left') {
            cssText += 'left: 0%;';
        } else if (corner === 'right') {
            cssText += 'right: 0%;';
        }
        div.style.cssText = cssText;
        div.style.visibility = 'hidden';

        // Add solid background
        div.style.backgroundColor = 'white';

        // Add image
        div.innerHTML = '<img class = "as-large-as-fits" id=' + id + '-img>';

        // Stop trial on click
        div.onclick = function () {
            trial.results.dt_response_selected = get_current_time();
            trial.results.selected_response = corner;
            trial.stop();
        };

        document.body.appendChild(div);
    },

    add: function () {
        response_options.add_response('left');
        response_options.add_response('right');
    },

    promise_to_load_images: function () {
        const promises = [
            promise_to_load_image($('#response-left-img').get(0), trial.uris.left),
            promise_to_load_image($('#response-right-img').get(0), trial.uris.right)
        ];
        return Promise.all(promises);
    },

    show: function () {
        $('.response-div').css('visibility', 'visible');
    },

    hide: function () {
        $('.response-div').css('visibility', 'hidden');
    },

    enable: function() {
        $('.response-div').prop("disabled", false);
    },

    disable: function() {
        $('.response-div').prop("disabled", true);
    },
};

start_button = {
    add: function () {
        const id = 'start-button';
        if ($('#' + id).length) {
            return
        }

        const div = document.createElement('div');
        div.className = 'bottom-center-of-the-screen unselectable';
        div.id = id;
        div.style.height = "10vh";
        div.style.width = "20vw";
        div.innerHTML = "Start";
        div.style.fontSize = "5vh";
        // Center text horizontally and vertically
        div.style.textAlign = "center";
        div.style.verticalAlign = "middle";
        div.style.lineHeight = div.style.height;

        // Add a border
        div.style.borderWidth = "3px";
        div.style.borderStyle = 'solid';
        div.style.borderColor = 'brown';

        // Add solid background
        div.style.backgroundColor = 'white';

        // Start on click
        div.onclick = function () {
            trial.results.dt_start_pressed = get_current_time();
            trial.start()
        };

        div.style.visibility = 'hidden';
        document.body.appendChild(div);
    },

    show: function () {
        $('#start-button').css('visibility', 'visible');
    },

    hide: function () {
        $('#start-button').css('visibility', 'hidden');
    },

    enable: function() {
        $('#start-button').prop("disabled", false);
    },

    disable: function() {
        $('#start-button').prop("disabled", true);
    },
};


const modal = {
    setup: () => {
        document.getElementById("modal-close").onclick = modal.hide;
    },

    onHideRunOnce: () => {},  // intentionally does nothing

    get element() {
        return $('#myModal').get(0);
    },

    set text(s) {
        $('#modalText').get(0).innerText = s;
    },

    show: () => {
        modal.element.style.display = "block";
        mousetracking.switch_to_real_cursor();
    },

    hide: () => {
        modal.element.style.display = "none";

        // Hiding the pop-up can result in triggering additional code if modal.onHideRunOnce is set to a function.
        modal.onHideRunOnce();
        modal.onHideRunOnce = () => {};  // intentionally does nothing
    },
};


const feedback = {
    duration: 500,

    id: 'feedback-msg',

    add: function () {
        if ($('#' + feedback.id).length) {
            return
        }

        const div = document.createElement('div');
        div.className = 'center-of-the-screen unselectable';
        div.id = feedback.id;
        div.style.height = "auto";
        div.style.width = "20vw";
        div.style.fontSize = "3vw";
        // Center text horizontally and vertically
        div.style.textAlign = "center";
        div.style.verticalAlign = "middle";
        div.style.lineHeight = div.style.height;

        // Add a border
        div.style.borderWidth = "5px";
        div.style.borderStyle = 'solid';

        // Add solid background
        div.style.backgroundColor = 'white';
        div.style.visibility = 'hidden';
        document.body.appendChild(div);
    },

    show: function (correct_response) {
        const div = $('#' + feedback.id).get(0);
        if (trial.results.selected_response == correct_response){
            div.innerHTML = 'Correct!';
            div.style.borderColor = 'green';
        } else {
            div.innerHTML = 'That was incorrect, unfortunately';
            div.style.borderColor = 'red';
        }
        div.style.visibility = 'visible';
    },

    hide: function () {
        const div = $('#' + feedback.id).get(0);
        div.style.visibility = 'hidden';
    },

    show_and_hide_promise: function(correct_response) {
        return new Promise((resolve) => {
            window.setTimeout(
            function () {
                feedback.show(correct_response);
                window.setTimeout(
                    function () {
                        // show options and release the cursor
                        feedback.hide();
                        resolve();
                    },
                    feedback.duration)
            },

            100)
        })
    }

};
