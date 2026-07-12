const { createApp } = Vue;
createApp({
    data() {
        return {
            trek_name: "",
            participants: []
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Staff") {
            window.location.href = "/";
            return;
        }
        this.loadParticipants();
    },
    methods: {
        async loadParticipants() {
            const token = localStorage.getItem("token");
            const trekId = window.location.pathname.split("/")[3];
            const response = await fetch(`/api/staff/trek/${trekId}/participants`, {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.message || "Failed to load participants");
                return;
            }
            this.trek_name = data.trek_name;
            this.participants = data.participants;
        },
        goBack() {
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