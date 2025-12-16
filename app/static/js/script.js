$(document).ready(function () {

    $(".cate-box").click(function (e) {
        e.preventDefault();
        const id = $(this).attr("data-id");
        const cur_id = $(this).attr("data-current-id");
        const url = new URL(window.location)

        if (cur_id) {
            url.searchParams.set("category_id", id);
        }
        if (Number(cur_id) === Number(id)) {
            url.searchParams.delete("category_id");
        }

        window.location.href = url.toString();
    });

    $("#sort-select").change(function () {
        const url = new URL(window.location)
        const sort = $(this).val();
        if (sort !== "") {
            url.searchParams.set("sort", sort);
        } else {
            url.searchParams.delete("sort");
        }

        window.location.href = url.toString();
    })

    $("#search-form").submit(function (e) {
        e.preventDefault();
        const url = new URL(window.location)
        const kw = $("#search-form input").val();
        if (kw !== "") {
            url.searchParams.set("kw", kw);
        }
        else {
            url.searchParams.delete("kw");
        }
        window.location.href = url.toString();
    })

    $(".kw-rm").click(function (e) {
        e.preventDefault();
        const url = new URL(window.location);
        url.searchParams.delete("kw");
        window.location.href = url.toString();
    })

    $(".sort-rm").click(function (e) {
        e.preventDefault();
        const url = new URL(window.location);
        url.searchParams.delete("sort");
        window.location.href = url.toString();
    })

    $(window).scroll(function () {
        if ($(window).scrollTop() > 2500) {
            $("#btn-back-to-top").slideDown();
        } else {
            $("#btn-back-to-top").slideUp();
        }
    });

    $("#btn-back-to-top").click(function () {
        $('html, body').animate({scrollTop: 0}, '1');
    });
})