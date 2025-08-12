


/**
 * @typedef {Object} LeafPageData 
 * @property {string} id - Reddit page 
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
 * @param {LeafPageData} data
 */
function main(data, comments) {

    // console.log(data)

    /* INSERT APP */
    $("#app").html(getLeafPageContent());


    /* HYDRATE */
    $('h1').text(data.title);
        
    document.title = "Performer: " + data.title;

    document.querySelector('.content').innerHTML = data.content_html;
    // console.log(data.content_html);

    // add nav
    const nav = $('nav');
    for (let p of data.parents) {
        const href = 
        nav.append(/* html */`
            <a href="${data.parent_links[p]}">
                ${data.parent_titles[p]}
            </a>
            <div>/</div>
        `);
    }
    nav.append(` <div> ${data.title} </div> `);
    
}



// Leaf page means the pages that directly link to media
function getLeafPageContent() {
    return /* html */ `
        <!-- HEADER -->
        <header>
            
            <nav></nav>
            
        </header>
        
        <main>
            <!-- LEFT SIDE -->
            <section class="left-section">
        
                <h1></h1>
                
                <div class="content"></div>
            
            </section>
        
            <!-- RIGHT SIDE -->
            <section class="right-section">
        
                <div class="player-wrapper">
                    <div id="player"></div>
                </div>

                <div class="comments-section">

                    
                    
                </div>
                
            </section>

        </main>
    `
}


main(data, null)
