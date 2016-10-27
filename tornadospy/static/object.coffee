do ->
    $("ul li a").one("mouseover", ->
        $a = $(this)
        $.ajax(
            url: "#{location.pathname}?type=repr"
            type: "POST"
            data: $a.attr("href").slice(1)
            dataType: "text"
            success: (data) ->
                $a.attr("title", data)
        )
    )
