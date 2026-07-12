const { createApp } = Vue;

createApp({
    data() {
        return {
            treks: [],
            allTreks: [],
            searchQuery: "",
            difficultyFilter: "",
            maxDuration: ""
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Trekker") {
            window.location.href = "/";
            return;
        }
        this.loadTreks();
    },
    methods: {
        async loadTreks() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/treks", {
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
            this.allTreks = data;
        },
        filterTreks() {
            const search = this.searchQuery.toLowerCase().trim();
            this.treks = this.allTreks.filter(trek => {
                const searchMatch =
                    trek.trek_name.toLowerCase().includes(search) ||
                    trek.location.toLowerCase().includes(search);
                const difficultyMatch =
                    !this.difficultyFilter ||
                    trek.difficulty === this.difficultyFilter;
                const durationMatch =
                    !this.maxDuration ||
                    trek.duration <= Number(this.maxDuration);
                return searchMatch && difficultyMatch && durationMatch;
            });
        },
        async bookTrek(id) {
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/user/book/${id}`, {
                method: "POST",
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
        goToDashboard() {
            window.location.href = "/user";
        },
        goToMyBookings() {
            window.location.href = "/user/bookings";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        }
    }
}).mount("#app");

