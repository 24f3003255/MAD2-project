const { createApp } = Vue;
createApp({
    data() {
        return {
            treks: [],
            editTrek: {
                id: null,
                available_slots: 0,
                status: ""
            },
            editModalInstance: null
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Staff") {
            window.location.href = "/";
            return;
        }
        this.loadTreks();
    },
    methods: {
        async loadTreks() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/staff/treks", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.message || "Failed to load treks");
                return;
            }
            this.treks = data;
        },
        openEditModal(trek) {
            this.editTrek.id = trek.id;
            this.editTrek.available_slots = trek.available_slots;
            this.editTrek.status = trek.status;
            const modal = document.getElementById("editTrekModal");
            this.editModalInstance = new bootstrap.Modal(modal);
            this.editModalInstance.show();
        },
        async updateTrek() {
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/staff/trek/${this.editTrek.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    available_slots: parseInt(this.editTrek.available_slots),
                    status: this.editTrek.status
                })
            });
            const data = await response.json();
            alert(data.message);
            if (response.ok) {
                this.editModalInstance.hide();
                this.loadTreks();
            }
        },
        async completeTrek(id) {
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/staff/trek/${id}/complete`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            alert(data.message);
            if (response.ok) {
                this.loadTreks();
            }
        },
        viewParticipants(id) {
            window.location.href = `/staff/trek/${id}/participants`;
        },
        goToDashboard() {
            window.location.href = "/staff";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            localStorage.removeItem("username");
            window.location.href = "/";
        }
    }
}).mount("#app");