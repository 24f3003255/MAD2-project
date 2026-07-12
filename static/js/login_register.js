const { createApp } = Vue;

createApp({
    data() {
        return {
            email: "",
            password: "",
            username: "",
            regEmail: "",
            regPassword: ""
        };
    },
    methods: {
        async register() {
            if (!this.username || !this.regEmail || !this.regPassword) {
                alert("Please fill all fields.");
                return;
            }
            const response = await fetch("/api/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: this.username,
                    email: this.regEmail,
                    password: this.regPassword
                })
            });
            const result = await response.json();
            if (!response.ok) {
                alert(result.message);
                return;
            }
            alert(result.message);
            this.username = "";
            this.regEmail = "";
            this.regPassword = "";
        },
        async login() {
            if (!this.email || !this.password) {
                alert("Enter your email and password.");
                return;
            }
            const response = await fetch("/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: this.email,
                    password: this.password
                })
            });
            const result = await response.json();
            if (!response.ok) {
                alert(result.message);
                return;
            }
            localStorage.setItem("token", result.token);
            localStorage.setItem("role", result.role);
            localStorage.setItem("username", result.username);
            if (result.role === "Admin") {
                window.location.href = "/admin";
            } else if (result.role === "Staff") {
                window.location.href = "/staff";
            } else {
                window.location.href = "/user";
            }
        }
    }
}).mount("#app");