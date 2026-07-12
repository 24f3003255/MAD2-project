const { createApp } = Vue;
createApp({
    data() {
        return {
            bookings: []
        };
    },
    mounted() {
        const token = localStorage.getItem("token");
        const role = localStorage.getItem("role");
        if (!token || role !== "Trekker") {
            window.location.href = "/";
            return;
        }
        this.loadBookings();
    },
    methods: {
        async loadBookings() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/bookings", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            if (!response.ok) {
                alert(data.message || "Failed to load bookings");
                return;
            }
            this.bookings = data;
        },
        async exportCSV() {
            const token = localStorage.getItem("token");
            const response = await fetch("/api/user/export-history", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            alert(data.message);
            this.checkExport();
        },
        async checkExport() {
            const token = localStorage.getItem("token");
            const interval = setInterval(async () => {
                const response = await fetch("/api/user/export-status", {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                const data = await response.json();
                if (data.status === "Completed") {
                    clearInterval(interval);
                    const download = await fetch("/api/user/download-export", {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    if (!download.ok) {
                        alert("Download failed");
                        return;
                    }
                    const blob = await download.blob();
                    const url = window.URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = "Trekking_History.csv";
                    document.body.appendChild(link);
                    link.click();
                    link.remove();
                    window.URL.revokeObjectURL(url);
                    alert("CSV downloaded successfully");
                }
            }, 2000);
        },
        async cancelBooking(id) {
            const token = localStorage.getItem("token");
            const response = await fetch(`/api/user/booking/${id}/cancel`, {
                method: "PUT",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });
            const data = await response.json();
            alert(data.message);
            if (response.ok) {
                this.loadBookings();
            }
        },
        goToDashboard() {
            window.location.href = "/user";
        },
        goToAvailableTreks() {
            window.location.href = "/user/treks";
        },
        logout() {
            localStorage.removeItem("token");
            localStorage.removeItem("role");
            window.location.href = "/";
        }
    }
}).mount("#app");
