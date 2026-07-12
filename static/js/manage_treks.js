const { createApp } = Vue;
createApp({
    data() {
        return {
            treks: [],
            allTreks: [],
            staffOptions: [],
            searchQuery: "",
            editTrekData: {
                id: null,
                trek_name: "",
                location: "",
                difficulty: "",
                duration: "",
                available_slots: "",
                assigned_staff_id: "",
                status: "",
                start_date: "",
                end_date: "",
                description: ""
            },
            editModalInstance: null
        };
    },
    mounted() {
        this.loadTreks();
        this.loadStaffOptions();
    },
    methods: {
        async loadTreks() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/admin/treks", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            this.treks = data;
            this.allTreks = data;
        },
        async loadStaffOptions() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/admin/staff-options", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            this.staffOptions = await response.json();
        },
        searchTreks() {
            const search = this.searchQuery.toLowerCase().trim();
            if (search === "") {
                this.treks = this.allTreks;
                return;
            }
            this.treks = this.allTreks.filter(trek =>
                trek.trek_name.toLowerCase().includes(search) ||
                trek.location.toLowerCase().includes(search) ||
                String(trek.id).includes(search)
            );
        },
        goToDashboard() {
            window.location.href = "/admin";
        },
        goToAddTrek() {
            window.location.href = "/admin/add-trek";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        },
        openEditModal(trek) {
            this.editTrekData = { ...trek };
            const modal = document.getElementById("editTrekModal");
            this.editModalInstance = new bootstrap.Modal(modal);
            this.editModalInstance.show();
        },
        async updateTrek() {
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/admin/trek/${this.editTrekData.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(this.editTrekData)
            });
            const result = await response.json();
            alert(result.message);
            if (response.ok) {
                this.editModalInstance.hide();
                this.loadTreks();
            }
        },
        async deleteTrek(id) {
            if (!confirm("Are you sure you want to delete this trek?")) {
                return;
            }
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/admin/trek/${id}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const result = await response.json();
            alert(result.message);
            if (response.ok) {
                this.loadTreks();
            }
        }
    }
}).mount("#app");