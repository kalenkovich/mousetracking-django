const mouseCheck = {
    runMouseCheck: function(){
        mouseCheck.render();
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
          disabled: false,  // TODO: enable after at least some scrolling
          // text: 'Continue',
          text: 'Продолжить',
          click: function () {
            container.empty();
            $(document).trigger('mouseCheckEnd', {didPass: true});
          }
        }).appendTo(scrollableDiv);
    },


};
