const { createApp } = Vue;
createApp({
    data() {
        return {
            username: "",
            email: ""
        };
    },
    mounted() {
        this.loadProfile();
    },
    methods: {
        async loadProfile() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/profile", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            this.username = data.username;
            this.email = data.email;
        },
        async updateProfile() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/profile", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    username: this.username,
                    email: this.email
                })
            });
            const data = await response.json();
            alert(data.message);
        },
        goDashboard() {
            window.location.href = "/user";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        }
    }
}).mount("#app");