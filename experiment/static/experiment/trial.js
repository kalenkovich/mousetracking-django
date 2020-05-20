function get_current_time(){
	return new Date()
}

trial = {
	uris: null,
	timing: null,

	results: {
		dt_start_pressed: null,
		dt_frame_presented: null,
		dt_audio_started: null,
		dt_response_selected: null,
		selected_response: null,
		trajectory: null
	},

	update_settings: function(data){
		trial.uris = data.uris;
		trial.timing = data.timing;
	},

	get_settings: function () {
		return new Promise((resolve, reject) => {
			$.ajax({
				url: 'get_new_trial_settings/',
				dataType: 'json',
				success: function(data) {
					trial.update_settings(data);
					resolve();
				}
			})
		})
	},

	send_results: function() {
		// also gets the new settings
		return new Promise((resolve, reject) => {
			$.post({
				url: 'save_trial_results/',
				headers: {"X-CSRFToken": csrf_token},
				dataType: 'json',
				data: JSON.stringify({results: trial.results}),
				success: function(data) {
					console.log('Results successfully sent')
					trial.update_settings(data);
					resolve();
				}
			})
		})
	},
	
	setup: function(){
		trial.add_all();
		trial.get_settings().then(trial.promise_to_load_all).then(start_button.show);
		fullscreen.enforce_fullscreen();
	},
	
	add_all: function(){
		frame.add();
		audio.add();
		response_options.add();
		start_button.add();
	},
	
	promise_to_load_all: function(){
		load_promises = [
			response_options.promise_to_load_images(),
			frame.promise_to_load_images(),
			audio.promise_to_load()];
		return Promise.all(load_promises);
	},
	
	hide_all: function(){
		// except the start button
		frame.hide();
		// audio.stop();
		response_options.hide();
		start_button.show();
	},
	
	start: function(){
		$('#start-button').prop("disabled", true);
		$('.response-div').prop("disabled", false);
		start_button.hide();
		mousetracking.start_tracking();
		trial.run();
	},
	
	run: function(){
		// show frame
		frame.show();
		trial.results.dt_frame_presented = get_current_time();
		window.setTimeout(
			function(){
				// hide frame, start playing audio
				frame.hide();
				audio.play();
				window.setTimeout(
					function(){
						// show options and release the cursor
						response_options.show();
						mousetracking.release_cursor();
					},
				trial.timing.audio)
			}, 
		
		trial.timing.frame)
	},
	
	abort: function(){
		$('.response-div').prop("disabled", true);
		$('#start-button').prop("disabled", false);
		mousetracking.reset();
		trial.hide_all();
	},
	
	stop: function(){
		$('.response-div').prop("disabled", true);
		$('#start-button').prop("disabled", false);
		mousetracking.stop_tracking();
		trial.results.trajectory = JSON.stringify(mousetracking.trajectory);
		trial.send_results().then(trial.hide_all);
	},
	
	debug: function(){
	    fullscreen.stop_enforcing_fullscreen();
	}
}

function promise_to_load_image(img_element, uri){
	return new Promise((resolve, reject) => {
		img_element.onload = function(){
			console.log(uri + ' loaded');
			resolve();
		};
		img_element.onerror = reject;
		img_element.src = uri;
	 });
}

frame = {
	calculate_sizes: function(){
		// In the offline version,
		// the frame had ~17 px borders and ~220 px square cells,
		// the screen resolution was 1920x780
		// returns cell side and border width as percentages of the width
		percent_per_pixel = 100 / 1920;
		border = 17 * percent_per_pixel;
		cell_side = 210 * percent_per_pixel;
		return [cell_side, border];
	},
	
	add: function(){
		if ($('#frame-div').length){return};
		div = document.createElement('div');
		div.style.visibility = 'hidden';
		div.className = 'center-of-the-screen';
		div.id = "frame-div";
		div.innerHTML = `
			<table class="frame">
				<tr>
					<td class="frame">
						<img class = "as-large-as-fits" id="image-0"></img>
					</td>
					<td class="frame">
						<img class = "as-large-as-fits" id="image-1"></img>
					</td>
				</tr>
				<tr>
					<td class="frame">
						<img class = "as-large-as-fits" id="image-2"></img>
					</td>
					<td class="frame">
						<img class = "as-large-as-fits" id="image-3"></img>
					</td>
				</tr>
			</table>
		`;
		document.body.appendChild(div);
		
		
		[cell_side, border] = frame.calculate_sizes();
		$('td.frame').css({
			'height': cell_side + 'vw',
			'width': cell_side + 'vw',
			'border-width': border + 'vw',
			'border-style': 'solid', 
			'border-color': 'brown'
		});
	},
	
	promise_to_load_images: function(){
		var promises = [];
		for (var i = 0; i < 4; i++){
			uri = trial.uris.frame_images[i];
			img_element = $('#image-' + i).get(0);
			if (uri !== null) {promises.push(promise_to_load_image(img_element, uri))};
		}
		return Promise.all(promises);
	},
	
	show: function(){
		$('#frame-div').css('visibility', 'visible');
	},
	
	hide: function(){
		$('#frame-div').css('visibility', 'hidden');
	},
}

audio = {
	add: function(){
		if ($('#audio').length){return};
		const audio_element = document.createElement('audio');
		audio_element.id = 'audio';
		audio_element.style.visibility = 'hidden';
		audio_element.addEventListener('play', (event) => {
		  	trial.results.dt_audio_started = get_current_time();
		});
		document.body.appendChild(audio_element);
	},
	
	promise_to_load: function(){
		audio_element = $('#audio').get(0);
		return new Promise((resolve, reject) => {
			audio_element.oncanplaythrough = function(){
				console.log('audio loaded');
				resolve();
			};
			audio_element.onerror = reject;
			audio_element.src = trial.uris.audio;
			audio_element.load();
		});
	},
	
	play: function(){
		audio_element = $('#audio').get(0);
		audio_element.play();
	}
}

response_options = {
	add_response: function(corner){
		id = 'response-' + corner;
		if ($('#' + id).length){return};
		div = document.createElement('div');
		div.className = 'response-div';
		div.id = id;
		cssText = "position: absolute; height:10vw; width: 10vw; top: 0%;";
		cssText += "border: 3px solid black;";
		if (corner == 'left'){
			cssText += 'left: 0%;';
		} else if (corner == 'right'){
			cssText += 'right: 0%;';
		}
		div.style.cssText = cssText;
		div.style.visibility = 'hidden';
		
		// Add solid background
		div.style.backgroundColor = 'white'
		
		// Add image
		div.innerHTML = '<img class = "as-large-as-fits" id=' + id + '-img></img>';
		
		// Stop trial on click
		div.onclick = function () {
			trial.results.dt_response_selected = get_current_time();
			trial.results.selected_response = corner;
			trial.stop();
		};
		
		document.body.appendChild(div);
	},
	
	add: function(){
		response_options.add_response('left');
		response_options.add_response('right');
	},
	
	promise_to_load_images: function(){
		var promises = [	
			promise_to_load_image($('#response-left-img').get(0), trial.uris.left),
			promise_to_load_image($('#response-right-img').get(0), trial.uris.right)
		]
		return Promise.all(promises);
	},
	
	show: function(){
		$('.response-div').css('visibility', 'visible');
	},
	
	hide: function(){
		$('.response-div').css('visibility', 'hidden');
	},
	
}

start_button = {
	add: function(){
		id = 'start-button';
		if ($('#' + id).length){return};
		div = document.createElement('div');
		div.className = 'bottom-center-of-the-screen';
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
		div.onclick = function(){
			trial.results.dt_start_pressed = get_current_time();
			trial.start()
		};
		
		div.style.visibility = 'hidden';
		document.body.appendChild(div);
	},
	
	show: function(){
		$('#start-button').css('visibility', 'visible');
	},
	
	hide: function(){
		$('#start-button').css('visibility', 'hidden');
	},
	
}
