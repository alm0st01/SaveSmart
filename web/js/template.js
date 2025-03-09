import { getCookie, logout } from './cookie.js';

class webheader extends HTMLElement {
    connectedCallback(){
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'css/default.css';
        document.head.appendChild(link);
        this.innerHTML = `
            <script src='js/cookie.js' type="module"></script>
            <header>
                <div class="img-box">
                <button onclick="window.location.href='index.html'" style="all:unset;">
                    <img src="images/logo.png" class="logo">
                </button>
                </div>
                <div class="headersection">
                    <button class="headerbutton" id="loginbutton" onclick="window.location.href='account/auth/login/login.html'">Login</button>
                    <button class="headerbutton" id="signupbutton" onclick="window.location.href='account/auth/signup/index.html'">Signup</button>
                    <button class="headerbutton" id="accountbutton" onclick="window.location.href='account/banking/index.html'">Account</button>
                    <button class="headerbutton" id="helpbutton" onclick="window.location.href='goals/index.html'">Budgeting & Goals</button>
                    <button class="headerbutton" id="logoutbutton" onclick="window.logout()">Logout</button>
                    <!--<button class="search-btn" onclick="alert('The search feature is currently unavailable.')">
                        <img src="images/search.png" class="search-icon">
                    </button>-->
                </div>
            </header>
        `;


        const attribute = 'fname';
        const isLoggedIn = getCookie(attribute) && document.cookie.includes(attribute+'=');
        const accountButton = this.querySelector('#accountbutton');
        const helpButton = this.querySelector('#helpbutton');
        const loginButton = this.querySelector('#loginbutton');
        const signupButton = this.querySelector('#signupbutton');
        const logoutButton = this.querySelector('#logoutbutton');
        if (isLoggedIn) {
            accountButton.textContent = getCookie(attribute)+"'s Account";
            loginButton.style.display = 'none';
            signupButton.style.display = 'none';
        }
        else {
            accountButton.style.display = 'none';
            helpButton.style.display = 'none';
            logoutButton.style.display = 'none';
            
        }

        
        const title = document.title;
        
        var activeButton;

        if (title == "Help"){
            activeButton = this.querySelector('#helpbutton');
            activeButton.className = "headerbutton active";
        }
        else if (title == "Signup"){
            activeButton = this.querySelector('#signupbutton');
            activeButton.className = "headerbutton active";
        }
        else if (title == "Login"){
            activeButton = this.querySelector('#loginbutton');
            activeButton.className = "headerbutton active";
        }
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