const { createApp } = Vue;
createApp({
    data() {
        return {
            staff_name: "",
            assigned_treks: 0,
            registered_trekkers: 0
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Staff") {
            window.location.href = "/";
            return;
        }
        this.loadDashboard();
    },
    methods: {
        async loadDashboard() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/staff/dashboard", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.message || "Failed to load dashboard");
                return;
            }
            this.staff_name = data.staff_name;
            this.assigned_treks = data.assigned_treks;
            this.registered_trekkers = data.registered_trekkers;
        },
        goToAssignedTreks() {
            window.location.href = "/staff/treks";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            localStorage.removeItem("username");
            window.location.href = "/";
        }
    }
}).mount("#app");