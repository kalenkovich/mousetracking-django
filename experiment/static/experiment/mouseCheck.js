const mouseCheck = {
    isMouse: null,

    oneWheelLooksLikeMouse: function (e) {
        console.log(
            'wheelDelta', e.wheelDelta,
            'deltaMode', e.deltaMode,
            'deltaY', e.deltaY
        )

        let isMouse = false;
        if ('wheelDelta' in e && e.wheelDelta % 120 === 0 && e.wheelDelta !== 0) {
                isMouse = true;
        } else if (!('wheelDelta' in e)) {  // firefox/IE
            if (e.deltaMode === 1 &&  Number.isInteger(e.deltaY)) {  // firefox
                isMouse = true;
            } else if (e.deltaMode === 0 &&  e.deltaY > 50) {  // ie
                isMouse = true;
            }

        }
        return isMouse;
    },

    tenWheelsLookLikeMouse: (function() {
        const arrayOfChecks = [];

        let finished = false;
        return function(e) {
            if (!finished) {
                arrayOfChecks.push(mouseCheck.oneWheelLooksLikeMouse(e));
                if (arrayOfChecks.length >= 10){
                   mouseCheck.isMouse = arrayOfChecks.every(Boolean);
                   mouseCheck.revealContinueButton();
                   finished = true;
                }
            }
        };
    })(),

    runMouseCheck: function(){
        mouseCheck.render();
    },

    revealContinueButton: function(){
        const buttonElement = document.getElementById("mouseCheck-continue-button");
        buttonElement.disabled = false;
        buttonElement.style.visibility = "visible";
    },

    render: function(){
        const container = $('#hc-container');

        // Instruction
        $('<hr/>').appendTo(container);
        $('<div/>', {
          class: 'mouseCheck-instruction',
          // text: 'To check the mouse, scroll using the wheel in the window below until the "Continue" button appears'
          text: 'Для проверки работы мыши прокрутите колесиком окошко снизу, пока не появится кнопка "Продолжить"'
        }).appendTo(container);

        // Scrollable window with the hidden "continue" button.
        $('<div/>', {
            id: "mouseCheck-scrollable-div",
            class: "mouseCheck-scrollable border",
        }).appendTo(container);
        const scrollableDiv = $('#mouseCheck-scrollable-div');
        // Empty span of the same height (set in css to class .mouseCheck-scrollable)
        $('<div/>', {
            class: "mouseCheck-scrollable",
        }).appendTo(scrollableDiv);


        // Add button to continue
        $('<br/>').appendTo(container);
        $('<button/>', {
          id: 'mouseCheck-continue-button',
          class: 'mouseCheck-instruction btn btn-primary',
          disabled: true,
          // text: 'Continue',
          text: 'Продолжить',
          click: function () {
            container.empty();
            $(document).trigger('mouseCheckEnd', {didPass: mouseCheck.isMouse});
          }
        }).appendTo(scrollableDiv);

        // Listen for scrolling
        document.addEventListener("wheel", mouseCheck.tenWheelsLookLikeMouse, false);
    },

};
