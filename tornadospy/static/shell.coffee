do ->
    $input = $("#input")
    $output = $("#output")
    $prompt = $("#prompt")
    history = []
    historyPos = 0

    focus_input = ->
        window.scroll(0, document.body.scrollHeight)
        $input.focus()

    $("html").click((e) ->
        if e.eventPhase == Event.AT_TARGET
            focus_input()
    )

    $("#submit").submit((e) ->
        e.preventDefault()
        input = $input.val()
        txt = $output.text() + $prompt.text() + input
        if input && input != history[history.length - 1]
            history.push(input)
        historyPos = history.length
        $prompt.text("")
        $output.text(txt)
        $.ajax(
            type: "POST",
            data: input,
            success: (data) ->
                prompt = if data then ">>> " else "... "
                $prompt.text(prompt)
                if data != "\n"
                    data = "\n" + data
                $output.text(txt + data)
                focus_input()
        )
        $input.val("")
        focus_input()
    )

    $input.keydown((e) ->
        code = e.keyCode
        if code in [38, 40]
            e.preventDefault()
            if code == 38 && historyPos > 0
                historyPos--
            else if code == 40 && historyPos < history.length
                historyPos++
            $input.val(history[historyPos])
    )

    focus_input()
