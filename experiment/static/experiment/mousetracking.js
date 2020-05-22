const mousetracking = {
    onPointerUnlock: () => {
    },  // do nothing by default

    normalize_coordinates: function (coordinates) {
        // bottom center is (0,0), top right is (1, 1), top left is (-1,1)
        const coords = coordinates;
        const x_normalized = coords.x / coords.width - 0.5;
        const y_normalized = 1 - coords.y / coords.height;
        return [x_normalized, y_normalized];
    },

    add_current_coordinates: function () {
        const coordinates = {
            x: fake_cursor.position.x,
            y: fake_cursor.position.y,
            width: $(window).width(),
            height: $(window).height()
        };
        mousetracking.trajectory.push(coordinates);
        const xy_normalized = mousetracking.normalize_coordinates(coordinates);
    },

    handle_pointer_unlocking: function () {
        if (document.pointerLockElement === null) {
            mousetracking.onPointerUnlock();
        }

    },

    start_tracking: function () {
        console.log('Started tracking');
        mousetracking.trajectory = [];
        fake_cursor.turn_on();
        fake_cursor.hold();
        fake_cursor.hide();
    },

    stop_tracking: function () {
        $(document).unbind('mousemove', mousetracking.add_current_coordinates);
        console.log('Stopped tracking');
        mousetracking.plot_trajectory();
    },

    plot_trajectory: function () {
        plotting.make_canvas();
        for (let coords of mousetracking.trajectory) {
            plotting.add_point(coords.x, coords.y);
        }
    },

    reset: function () {
        mousetracking.trajectory = [];
        fake_cursor.turn_off();
    },

    release_cursor: function () {
        console.log('Released the cursor');
        fake_cursor.release(mousetracking.add_current_coordinates);
    }

};

const fake_cursor = {
    height: 20,

    add_event_listener: function (fun) {
        document.addEventListener('pointerlockchange', fun);
        document.addEventListener('mozpointerlockchange', fun);
    },

    lock_pointer: function () {
        const doc_elem = document.documentElement;
        doc_elem.requestPointerLock = doc_elem.requestPointerLock ||
            doc_elem.mozRequestPointerLock;
        doc_elem.requestPointerLock();
    },

    add: function () {
        if ($('#cursor-img').length) {
            return;
        }


        const cursor_img = document.createElement("img");
        cursor_img.src = cursorURI;
        cursor_img.id = "cursor-img";
        // This makes the cursor invisible to document.elementFromPoint.
        // Otherwise, it will just return the cursor image instead of the button.
        cursor_img.style.pointerEvents = "none";
        cursor_img.style.height = fake_cursor.height + "px";
        cursor_img.style.position = "absolute";
        cursor_img.style.left = "50%";
        cursor_img.style.bottom = "0%";
        cursor_img.style.visibility = 'hidden';
        document.body.appendChild(cursor_img);
    },

    mouseMoveCallback: null,

    position: {x: $(window).width() / 2, y: $(window).height() - 20},

    redraw: function () {
        const cursor_img = $('#cursor-img').get(0);
        const x = fake_cursor.position.x;
        cursor_img.style.left = x + "px";
        const y = fake_cursor.position.y;
        cursor_img.style.top = y + "px";
    },

    let_user_click: function () {
        // This is to avoid binding the function twice. I don't know a better way.
        fake_cursor.stop_clicking_with();
        window.addEventListener("mouseup", fake_cursor.click);
    },

    turn_on: function () {
        fake_cursor.reset_position();
        fake_cursor.lock_pointer();
        fake_cursor.add_event_listener(fake_cursor.handle_pointer_unlocking);
        fake_cursor.add();
        fake_cursor.redraw();
    },

    release: function (mouseMoveCallback) {
        // mouseMoveCallback - function that will be bound to the `mousemove` event.
        // We save it here so that we can unbind it later.
        fake_cursor.mouseMoveCallback = mouseMoveCallback;
        fake_cursor.show();
        fake_cursor.let_user_move();
        $(document).mousemove(mouseMoveCallback);
        fake_cursor.let_user_click();
    },

    hold: function () {
        $(document).unbind("mousemove", fake_cursor.mouseMoveCallback);
        fake_cursor.mouseMoveCallback = null;
        fake_cursor.stop_moving();
        fake_cursor.stop_clicking_with();
    },

    unlock_pointer: function () {
        document.exitPointerLock = document.exitPointerLock ||
            document.mozExitPointerLock;
        document.exitPointerLock();
    },

    remove_event_listener: function (fun) {
        document.removeEventListener('pointerlockchange', fun);
        document.removeEventListener('mozpointerlockchange', fun);
    },

    hide: function () {
        const cursor_img = $('#cursor-img').get(0);
        if (cursor_img) {
            cursor_img.style.visibility = 'hidden';
        }

    },

    show: function () {
        const cursor_img = $('#cursor-img').get(0);
        if (cursor_img) {
            cursor_img.style.visibility = 'visible';
        }

    },

    turn_off: function () {
        $(document).unbind("mousemove", fake_cursor.mouseMoveCallback);
        fake_cursor.mouseMoveCallback = null;
        fake_cursor.unlock_pointer();
        fake_cursor.remove_event_listener(fake_cursor.handle_pointer_unlocking);
        fake_cursor.hide();
        fake_cursor.stop_moving();

    },

    reset_position: function () {
        const position = fake_cursor.position;
        position.x = $(window).width() / 2;
        position.y = $(window).height() - fake_cursor.height;
    },

    bound_coordinates: function (x, y) {
        // bound coordinates by the window size minus one pixel
        // minus one pixel - so that the cursor is visible on the right and bottom edegs - this is normal behavior

        const width = $(window).width();
        x = Math.max(x, 0);
        x = Math.min(x, width - 1);

        const height = $(window).height();
        y = Math.max(y, 0);
        y = Math.min(y, height - 1);

        return [x, y];
    },

    copy_mouse_movement: function (event) {

        let x = fake_cursor.position.x += (event.movementX || event.originalEvent.movementX);
        let y = fake_cursor.position.y += (event.movementY || event.originalEvent.movementY);
        [x, y] = fake_cursor.bound_coordinates(x, y);

        fake_cursor.position.x = x;
        fake_cursor.position.y = y;

        fake_cursor.redraw();
    },

    stop_moving: function () {
        $(document).unbind('mousemove', fake_cursor.copy_mouse_movement);
    },

    let_user_move: function () {
        // This is to avoid binding the function twice. I don't know a better way.
        fake_cursor.stop_moving();
        $(document).mousemove(fake_cursor.copy_mouse_movement);
    },

    click: function () {
        const pos = fake_cursor.position;
        const object_under_cursor = document.elementFromPoint(pos.x, pos.y);
        if (object_under_cursor !== null) {
            object_under_cursor.click();
        }
    },

    stop_clicking_with() {
        $(window).unbind('mouseup', fake_cursor.click);
    },
};

const plotting = {
    make_canvas: function () {
        if (typeof plotting.canvas !== 'undefined') {
            return;
        }

        const canvas = document.createElement("canvas");
        plotting.canvas = canvas;

        canvas.setAttribute("style", "z-index:-1; display: block; width: 100%; height: 100%;");

        document.body.appendChild(canvas);
    },

    add_point: function (x, y) {
        const ctx = plotting.canvas.getContext("2d");
        const rect = plotting.canvas.getBoundingClientRect();
        const x_ = (x - rect.left) / (rect.right - rect.left) * plotting.canvas.width;
        const y_ = (y - rect.top) / (rect.bottom - rect.top) * plotting.canvas.height;
        ctx.fillRect(Math.round(x_), Math.round(y_), 1, 1);
    }
};
