class web_header extends HTMLElement {
    connectedCallback(){

        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = '/css/headerfooter.css';
        document.head.appendChild(link);

        this.innerHTML = `
            <header>
                <img src="/images/logo.png" style="width:20%;height:auto;">
                <div class="headersection">
                    <button class="headerbutton">Help</button>
                    <button class="headerbutton">Login/Account</button>
                    <button style="all:unset; width: 10%; cursor:pointer; ">
                        <img src="/images/search.png" style="background-color:transparent; width: 60%; height: auto;">
                    </button>
                    <!--<div style="width:5%"></div>-->
                </div>
            </header>
        `;
    }
}

customElements.define("web_header", web_header)