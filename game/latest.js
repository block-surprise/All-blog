fetch('/game/latest.json')
.then(r => r.json())
.then(data => {

    let html = "";

    data.forEach(post => {

        html += `
        <a class="latest-item" href="${post.url}">
            <div class="latest-title">
                ${post.title}
            </div>
        </a>
        `;

    });

    document.getElementById("latest-posts").innerHTML = html;

});
