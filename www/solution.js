$(document).ready(function() {
    $("div.page:hidden:first").show();

    $("a.prev_page").click(function() {
        var currpage = $("div.page:visible:first")
        var prevpage = currpage.prev('div.page');

        if (! currpage.is("div.page:first")) {
            currpage.hide()
            prevpage.show()
        }
    });

    $("a.next_page").click(function() {
        var currpage = $("div.page:visible:first")
        var nextpage = currpage.next('div.page');

        if (! currpage.is("div.page:last")) {
            currpage.hide()
            nextpage.show()
        }
    });
})
