const { createApp } = Vue

createApp({
    data() {
        return {
            bookings: [],
            allBookings: [],
            searchQuery: ""
        }
    },
    mounted() {
        this.loadHistory()
    },
    methods: {
        async loadHistory() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/history", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            this.bookings = result
            this.allBookings = result
        },
        searchHistory() {
            const search = this.searchQuery.toLowerCase().trim()
            if (!search) {
                this.bookings = this.allBookings
                return
            }
            this.bookings = this.allBookings.filter(booking =>
                booking.username.toLowerCase().includes(search) ||
                booking.trek_name.toLowerCase().includes(search) ||
                String(booking.booking_id).includes(search)
            )
        },
        goDashboard() {
            window.location = "/admin"
        },
        logout() {
            localStorage.removeItem("token")
            localStorage.removeItem("role")
            localStorage.removeItem("username")
            window.location = "/"
        }
    }
}).mount("#app")