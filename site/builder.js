


/**
 * @typedef {Object} PageData 
 * @property {string} id Reddit page 
 * @property {number} depth - 
 * @property {string} parent - 
 * @property {string[]} parents - 
 * @property {string[]} media_links - 
 * @property {string[]} media_links_local - 
 * @property {string} date_created - 
 * @property {string} title - 
 * @property {string} url - 
 * @property {string} author - 
 * @property {string} author_href - 
 * @property {string} content_html - 
 */

/**
 * @typedef {Object} MediaData
 * @property {string} id
 * @property {string} local_path
 * @property {string} date_created
 * @property {string} title
 * @property {string} url
 * @property {string} reddit_url
 * @property {Comment[]} comments
 * 
 */

/**
 * @typedef {Object} Comment
 * @property {string} author
 * @property {string} author_href
 * @property {string} comment_html
 */

/**
 * @param {PageData} page_data
 * @param {MediaData} media_data
 */
function main(page_data, media_data) {

    document.title = page_data.dirname + ": " + page_data.title;
    
    // insert app
    $("#app").html(getPageContent(page_data));

    /* load media post */
    const loadMediaPost = (sid) => {
        const data = media_data[sid]
        if (!data) {
            console.error("No media data for sid: "+sid)
        }
        $("#media-section").html(getMediaPostContent(data))
        $("a.media-post-button").each((i, b) => $(b).removeClass("highlighted"))
        $("a.media-post-button[data-sid="+ sid +"]").addClass("highlighted")
    }
    
    /* media post buttons */
    document.querySelectorAll("a.media-post-button").forEach(a_el => {
        const sid = a_el.getAttribute("data-sid")
        a_el.addEventListener('click', () => {
            loadMediaPost(sid)
            history.pushState({}, '', '?media_sid='+sid)
        })
    })

    /* page nav */

    const checkMediaPostFromURL = () => {
        const media_sid = (new URLSearchParams(window.location.search)).get("media_sid");
        if (media_sid) {
            console.log("sid:", media_sid)
            loadMediaPost(media_sid)
        }
    }
    
    // pop state
    window.addEventListener('popstate', (event) => {
        checkMediaPostFromURL();
    });

    checkMediaPostFromURL();

}



/**
 * 
 * @param {PageData} data 
 * @returns {string}
 */
function getPageContent(data) {

    // get nav html
    nav_html = '';
    for (let p of page_data.parents) {
        nav_html += /* html */`
            <a href="${page_data.parent_links[p]}">
                ${page_data.parent_titles[p]}
            </a>
            <div>/</div>
        `;
    }
    
    return /* html */ `

        <!-- HEADER -->
        <header>
            <nav>${nav_html}</nav>
        </header>
        
        <main>
            <!-- LEFT SIDE -->
            <section class="left-section">
                <a href="${data.url}">
                    <h1>${data.title}</h1>
                </a>
                <div class="content">
                    ${data.content_html}
                </div>
            </section>
        
            <!-- RIGHT SIDE -->
            <section id="media-section"></section>

        </main>
    `
}

/**
 * 
 * @param {MediaData} data 
 * @returns {string}
 */
function getMediaPostContent(data) {

    comment_html = ''
    for (let i = 0; i < data.comments.length; i++) {
        const comment = data.comments[i]
        comment_html += comment.comment_html;
    }
    
    return /* html */ `
    <a href="${data.reddit_url}" target="_blank">
        <h2>${data.title}</h2>
    </a>
    <div class="player-wrapper">
        <!-- <div id="player"></div> -->
        <video src="${data.local_path}" controls looped
        ></video>
    </div>
    <div class="comments-section">
        ${comment_html}
    </div>
    `
}


main(page_data, media_data)
