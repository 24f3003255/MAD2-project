const { createApp } = Vue

createApp({
    data() {
        return {
            total_users: 0,
            total_treks: 0,
            total_staff: 0,
            total_bookings: 0
        }
    },
    mounted() {
        const token = localStorage.getItem("token")
        const userRole = localStorage.getItem("role")
        if (!token || userRole !== "Admin") {
            window.location = "/"
            return
        }
        this.loadDashboard()
    },
    methods: {
        async loadDashboard() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/dashboard", {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            this.total_users = result.total_users
            this.total_treks = result.total_treks
            this.total_staff = result.total_staff
            this.total_bookings = result.total_bookings
        },
        async testReminder() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/test-reminder", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            alert(result.message)
        },
        async printReport() {
            const token = localStorage.getItem("token")
            const response = await fetch("/api/admin/report", {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`
                }
            })
            const result = await response.json()
            alert(result.message)
        },
        goToAddStaff() {
            window.location = "/admin/add-staff"
        },
        goToManageStaff() {
            window.location = "/admin/staffs"
        },
        goToAddTrek() {
            window.location = "/admin/add-trek"
        },
        goToManageTreks() {
            window.location = "/admin/manage-treks"
        },
        goToManageUsers() {
            window.location = "/admin/manage-users"
        },
        goHistory() {
            window.location = "/admin/history"
        },
        logout() {
            localStorage.removeItem("token")
            localStorage.removeItem("role")
            localStorage.removeItem("username")
            window.location = "/"
        }
    }
}).mount("#app")