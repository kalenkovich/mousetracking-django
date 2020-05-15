var fullscreen = {
	/* View in fullscreen */
	open: function() {
		var elem = document.documentElement;
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
	close: function() {
	    var elem = document.documentElement;
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
	
	add_event_listener: function(fun){
		/* Standard syntax */
		document.addEventListener("fullscreenchange", fun);

		/* Firefox */
		document.addEventListener("mozfullscreenchange", fun);

		/* Chrome, Safari and Opera */
		document.addEventListener("webkitfullscreenchange", fun);

		/* IE / Edge */
		document.addEventListener("msfullscreenchange", fun);
	},
	
	remove_event_listener: function(fun){
		/* Standard syntax */
		document.removeEventListener("fullscreenchange", fun);

		/* Firefox */
		document.removeEventListener("mozfullscreenchange", fun);

		/* Chrome, Safari and Opera */
		document.removeEventListener("webkitfullscreenchange", fun);

		/* IE / Edge */
		document.removeEventListener("msfullscreenchange", fun);
	},
	
	ask_for_fullscreen: function(){
		if (document.fullscreenElement !== null){return}
		$(".backdrop").fadeTo(200, 1);
		$("#btn-go-fullscreen").off('click');
		$("#btn-go-fullscreen").click(fullscreen.switch_to_fullscreen);
	},
	
	hide_popup: function(){
		$(".backdrop").fadeOut(200);
	},
		
	switch_to_fullscreen: function(){
		fullscreen.hide_popup();
		fullscreen.open();
	},
	
	handle_exit: function(){
		if (document.fullscreenElement === null){
			trial.abort();
			fullscreen.ask_for_fullscreen();
		}
	},
	
	enforce_fullscreen: function(){
		fullscreen.add_event_listener(fullscreen.handle_exit);
		fullscreen.ask_for_fullscreen();
	},
	
	stop_enforcing_fullscreen: function(){
		fullscreen.hide_popup();
		fullscreen.remove_event_listener(fullscreen.handle_exit);
	},
}
