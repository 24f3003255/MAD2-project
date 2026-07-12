const { createApp } = Vue;
createApp({
    data() {
        return {
            username: "",
            total_bookings: 0
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Trekker") {
            window.location.href = "/";
            return;
        }
        this.loadDashboard();
    },
    methods: {
        async loadDashboard() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/dashboard", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.message || "Failed to load dashboard");
                return;
            }
            this.username = data.username;
            this.total_bookings = data.total_bookings;
        },
        goToAvailableTreks() {
            window.location.href = "/user/treks";
        },
        goToMyBookings() {
            window.location.href = "/user/bookings";
        },
        goProfile() {
            window.location.href = "/user/profile";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        }
    }
}).mount("#app");
