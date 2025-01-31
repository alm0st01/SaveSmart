class webheader extends HTMLElement {
    connectedCallback(){
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'css/default.css';
        document.head.appendChild(link);
        this.innerHTML = `
            <header>
                <button style="all:unset; width: 18%; cursor:pointer;" onclick="window.location.href='index.html'">    
                    <img src="images/logo.png" style="width:100%;height:auto;">
                </button>
                <div class="headersection">
                    <button class="headerbutton" onclick="window.location.href='help/index.html'">Help</button>
                    <button class="headerbutton" onclick="window.location.href='account/auth/signup/index.html'">Signup</button>
                    <button class="headerbutton" onclick="window.location.href='account/auth/login/login.html'">Login</button>
                    <button class="headerbutton" id="accountbutton" onclick="window.location.href='account/banking/index.html'">Account</button>
                    <button onclick="alert('The search feature is currently unavailable.')" style="all:unset; width: 10%; cursor:pointer; ">
                        <img src="images/search.png" style="background-color:transparent; width: 60%; height: auto;">
                    </button>
                    <!--<div style="width:5%"></div>-->
                </div>
            </header>
        `;
    }
}

customElements.define("web-header", webheader)

class webfooter extends HTMLElement {
    connectedCallback(){

        
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'css/default.css';
        document.head.appendChild(link);

        this.innerHTML = `
            <footer>
                <p>SaveSmart © 2025</p>
            </footer>
        `;
    }
}

customElements.define("web-footer", webfooter)