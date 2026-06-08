fetch('/game/latest.json')
.then(r => r.json())
.then(data => {

    let html = "<ul>";

    data.forEach(post => {
        html += `<li><a href="${post.url}">${post.title}</a></li>`;
    });

    html += "</ul>";

    document.getElementById("latest-posts").innerHTML = html;
});
